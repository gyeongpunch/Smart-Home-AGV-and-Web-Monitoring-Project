import threading, time
import cv2
import numpy as np
from jetbot import bgr8_to_jpeg

class WorkingAreaFind(threading.Thread):
    def __init__(self, camera, image_widget):
        super().__init__()
        self.camera = camera
        self.image_widget = image_widget
        self.active = True
        self.flag = 1

        # 색상 정의
        self.colors = {
            1: {'name': 'purple', 'lower': np.array([129, 50, 70]), 'upper': np.array([158, 255, 255])},
            2: {'name': 'blue', 'lower': np.array([94, 80, 2]), 'upper': np.array([126, 255, 255])}
        }
        self.cx, self.cy = 224 // 2, 224 // 2

    def run(self):
        while self.active:
            frm = self.camera.value
            hsv = cv2.blur(cv2.cvtColor(frm, cv2.COLOR_BGR2HSV), (15, 15))
            lower = self.colors[self.flag]['lower']
            upper = self.colors[self.flag]['upper']

            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.dilate(cv2.erode(mask, None, 2), None, 2)
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if cnts:
                c = max(cnts, key=cv2.contourArea)
                (x, y), _ = cv2.minEnclosingCircle(c)
                if abs(self.cx - x) < 15 and abs(self.cy - y) < 15:
                    self.flag = 2 if self.flag == 1 else 1

            self.image_widget.value = bgr8_to_jpeg(frm)
            time.sleep(0.1)

        print("🛑 WorkingAreaFind 중단됨")

    def stop(self):
        self.active = False
