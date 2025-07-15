from SCSCtrl import TTLServo
import time

def setup_gripper(channel=0):
    """집게 서보 초기화 및 중립 위치로 이동"""
    gripper = TTLServo(channel=channel)
    gripper.angle = 90
    return gripper

def grip(gripper):
    """물건을 집는다 (닫힘)"""
    gripper.angle = 0
    print("🦾 집게 닫힘 (Grip)")
    time.sleep(1)

def release(gripper):
    """물건을 놓는다 (열림)"""
    gripper.angle = 90
    print("🦾 집게 열림 (Release)")
    time.sleep(1)
