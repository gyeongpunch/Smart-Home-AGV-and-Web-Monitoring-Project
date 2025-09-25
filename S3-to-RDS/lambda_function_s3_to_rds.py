import os
import json
import logging
import pymysql
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 환경변수 또는 Secrets Manager 에 저장한 RDS 접속 정보
DB_HOST     = os.environ['DB_HOST']
DB_PORT     = int(os.environ.get('DB_PORT', 3306))
DB_USER     = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME     = os.environ['DB_NAME']

# S3 클라이언트
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    S3 PUT 이벤트로 호출됨.
    raw/ 아래에 올라온 JSON 파일을 읽어 파싱한 뒤,
    device, event, sensor_reading 테이블에 INSERT 합니다.
    """
    # 1) 이벤트에서 버킷명, 객체 키 추출
    for rec in event['Records']:
        bucket = rec['s3']['bucket']['name']
        key    = rec['s3']['object']['key']
        logger.info(f"Processing s3://{bucket}/{key}")
        
        # 2) S3에서 파일 다운로드
        obj = s3.get_object(Bucket=bucket, Key=key)
        raw = obj['Body'].read().decode('utf-8')
        data = json.loads(raw)
        
        # 3) RDS 연결
        conn = pymysql.connect(
            host     = DB_HOST,
            port     = DB_PORT,
            user     = DB_USER,
            password = DB_PASSWORD,
            db       = DB_NAME,
            charset  = 'utf8mb4',
            cursorclass = pymysql.cursors.DictCursor
        )
        
        try:
            with conn.cursor() as cur:
                # 4) device 테이블 UPSERT (중복 삽입 방지)
                for d in data.get('devices', []):
                    sql = """
                    INSERT INTO device (device_id, device_name, device_type, description)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      device_name = VALUES(device_name),
                      device_type = VALUES(device_type),
                      description = VALUES(description);
                    """
                    cur.execute(sql, (
                        d['device_id'],
                        d['device_name'],
                        d['device_type'],
                        d.get('description')
                    ))
                
                # 5) event 테이블 INSERT
                for e in data.get('events', []):
                    sql = """
                    INSERT INTO `event` (event_id, device_id, event_time, event_type, note)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      device_id  = VALUES(device_id),
                      event_time = VALUES(event_time),
                      event_type = VALUES(event_type),
                      note       = VALUES(note);
                    """
                    # ISO8601 → MySQL DATETIME
                    etime = datetime.fromisoformat(e['event_time'].replace('Z','+00:00'))
                    cur.execute(sql, (
                        e['event_id'],
                        e['device_id'],
                        etime,
                        e['event_type'],
                        e.get('note')
                    ))
                
                # 6) sensor_reading 테이블 INSERT
                for s in data.get('sensor_readings', []):
                    sql = """
                    INSERT INTO sensor_reading
                      (reading_id, device_id, metric, reading_time, value_float, threshold, unit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      device_id    = VALUES(device_id),
                      metric       = VALUES(metric),
                      reading_time = VALUES(reading_time),
                      value_float  = VALUES(value_float),
                      threshold    = VALUES(threshold),
                      unit         = VALUES(unit);
                    """
                    rtime = datetime.fromisoformat(s['reading_time'].replace('Z','+00:00'))
                    cur.execute(sql, (
                        s['reading_id'],
                        s['device_id'],
                        s['metric'],
                        rtime,
                        s['value_float'],
                        s.get('threshold'),
                        s.get('unit')
                    ))
                
                # 커밋
                conn.commit()
                logger.info("DB insert/updates successful.")
        
        finally:
            conn.close()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processed S3 data and stored to RDS.'})
    }
