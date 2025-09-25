import os
import json
import pymysql
import boto3
from openai import OpenAI
from datetime import datetime

# ───────────────────────────────────────────────────────────────────────
# 환경변수 설정
# ───────────────────────────────────────────────────────────────────────
DB_HOST     = os.environ['DB_HOST']
DB_PORT     = int(os.environ.get('DB_PORT', 3306))
DB_USER     = os.environ['DB_USER']
DB_PASS     = os.environ['DB_PASSWORD']
DB_NAME     = os.environ['DB_NAME']

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
SES_SENDER     = os.environ['SES_SENDER']    # e.g. 'noreply@yourdomain.com'
SES_RECIPIENT  = os.environ['SES_RECIPIENT'] # 보고서 수신자

# OpenAI 및 SES 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)
ses    = boto3.client('ses', region_name=os.environ.get('AWS_DEFAULT_REGION','ap-northeast-2'))

# ───────────────────────────────────────────────────────────────────────
# 1) RDS에서 모든 디바이스 목록 조회
# ───────────────────────────────────────────────────────────────────────
def fetch_devices():
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS,
        db=DB_NAME, charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        cur.execute("SELECT device_id, device_name FROM device")
        devices = cur.fetchall()
    conn.close()
    return devices

# ───────────────────────────────────────────────────────────────────────
# 2) 특정 디바이스의 최근 200개 이벤트·리딩을 조회
# ───────────────────────────────────────────────────────────────────────
def fetch_device_data(device_id, limit=200):
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS,
        db=DB_NAME, charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cur:
        # 이벤트
        cur.execute(
            "SELECT event_time, event_type, note "
            "FROM `event` "
            "WHERE device_id = %s "
            "ORDER BY event_time DESC "
            "LIMIT %s",
            (device_id, limit)
        )
        events = cur.fetchall()[::-1]  # 시간 오름차순으로 뒤집기

        # 센서 리딩
        cur.execute(
            "SELECT reading_time, metric, value_float "
            "FROM sensor_reading "
            "WHERE device_id = %s "
            "ORDER BY reading_time DESC "
            "LIMIT %s",
            (device_id, limit)
        )
        readings = cur.fetchall()[::-1]
    conn.close()
    return events, readings

# ───────────────────────────────────────────────────────────────────────
# 3) GPT 프롬프트 생성
# ───────────────────────────────────────────────────────────────────────
def make_prompt(device_name, events, readings):
    text = [f"장치 **{device_name}** 의 최근 {len(events)}개 이벤트와 {len(readings)}개 센서 리딩입니다.\n"]
    text.append("=== 이벤트 내역 ===")
    for e in events:
        note = e['note'] or '-'
        text.append(f"{e['event_time']} | {e['event_type']} | {note}")
    text.append("\n=== 센서 리딩 ===")
    for r in readings:
        text.append(f"{r['reading_time']} | {r['metric']} = {r['value_float']}")
    text.append(
        "\n위 데이터를 바탕으로 아래 항목을 포함한 간결한 보고서를 작성해 주세요:\n"
        "1) 주요 발생 이벤트 요약\n"
        "2) 센서 값의 특이점 또는 트렌드\n"
        "3) 권장 조치 사항\n"
    )
    return "\n".join(text)

# ───────────────────────────────────────────────────────────────────────
# 4) OpenAI에 요약 요청
# ───────────────────────────────────────────────────────────────────────
def summarize_with_gpt(prompt: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=500,
        temperature=0.3
    )
    return resp.choices[0].message.content.strip()

# ───────────────────────────────────────────────────────────────────────
# 5) SES로 이메일 발송
# ───────────────────────────────────────────────────────────────────────
def send_email(subject: str, body: str):
    ses.send_email(
        Source=SES_SENDER,
        Destination={'ToAddresses':[SES_RECIPIENT]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )

# ───────────────────────────────────────────────────────────────────────
# Lambda 핸들러: 디바이스별 보고서 작성·전송
# ───────────────────────────────────────────────────────────────────────
def lambda_handler(event, context):
    devices = fetch_devices()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    for dev in devices:
        dev_id   = dev['device_id']
        dev_name = dev['device_name']

        # 2) 데이터 조회
        events, readings = fetch_device_data(dev_id)

        # 데이터 없으면 스킵
        if not events and not readings:
            print(f"[{dev_name}] 데이터 없음 → 스킵")
            continue

        # 3) GPT 요약
        prompt = make_prompt(dev_name, events, readings)
        report = summarize_with_gpt(prompt)

        # 4) 이메일 전송
        subject = f"[IoT 보고서][{dev_name}] {now_str}"
        body    = f"{report}\n\n— IoT 자동 보고 시스템"
        send_email(subject, body)
        print(f"[{dev_name}] 보고서 전송 완료")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': '모든 디바이스 보고서를 전송했습니다.'})
    }
