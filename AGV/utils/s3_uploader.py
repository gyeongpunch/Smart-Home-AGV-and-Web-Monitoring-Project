import os, json, time, random
from datetime import datetime
import threading
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError

# ────────────────────────────────────────────────
# 환경 변수 로딩 (.env 파일에서 AWS 자격증명 읽기)
# ────────────────────────────────────────────────
load_dotenv("config/secrets.env")

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION    = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
BUCKET  = os.getenv("S3_BUCKET", "ssafy-iot-logs")
PREFIX  = os.getenv("S3_PREFIX", "raw/")

s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

_event_id = 100
_reading_id = 200

def make_payload():
    """랜덤 이벤트 및 센서 읽기 JSON 반환"""
    global _event_id, _reading_id
    now_iso = datetime.utcnow().isoformat() + 'Z'
    _event_id += 1
    _reading_id += 1
    return {
        "devices": [
            {"device_id": 1, "device_name": "jetson-robot", "device_type": "robot", "description": "AGV 로봇"},
            {"device_id": 5, "device_name": "gripper-servo", "device_type": "servo", "description": "집게 모터"}
        ],
        "events": [{
            "event_id": _event_id,
            "device_id": random.choice([1, 5]),
            "event_time": now_iso,
            "event_type": random.choice(["power_on", "power_off", "pick_up", "put_down"]),
            "note": "JetBot action event"
        }],
        "sensor_readings": [{
            "reading_id": _reading_id,
            "device_id": 1,
            "metric": "battery",
            "reading_time": now_iso,
            "value_float": round(random.uniform(20, 100), 2),
            "threshold": None,
            "unit": "%"
        }]
    }

def start_s3_uploader():
    """
    10초마다 payload를 생성해 S3에 업로드하는 데몬 함수
    main.py에서 threading.Thread(target=start_s3_uploader, daemon=True).start()로 실행
    """
    try:
        s3.list_buckets()
        print("✅ S3 연결 확인됨")
    except NoCredentialsError:
        print("❌ AWS 자격증명 오류")
        return

    while True:
        payload = make_payload()
        key = PREFIX + datetime.utcnow().strftime("%Y/%m/%d/") + \
              f"iot_data_{datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')}.json"
        s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(payload).encode('utf-8'))
        print(f"{datetime.now():%H:%M:%S} ▶ S3 업로드 완료: s3://{BUCKET}/{key}")
        time.sleep(10)