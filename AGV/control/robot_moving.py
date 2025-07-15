import threading, time
import numpy as np
from collections import deque
from vision.preprocess import preprocess

class RobotMoving(threading.Thread):
    def __init__(self, camera, robot, model, device, mean, std,
                 x_slider, y_slider, image_widget,
                 steering_slider, speed_slider,
                 speed_gain_slider, steering_gain_slider,
                 steering_dgain_slider, steering_bias_slider):
        super().__init__()
        self.active = True
        self.camera = camera
        self.robot = robot
        self.model = model
        self.device = device
        self.mean = mean
        self.std = std
        self.x_slider = x_slider
        self.y_slider = y_slider
        self.image_widget = image_widget
        self.steering_slider = steering_slider
        self.speed_slider = speed_slider
        self.speed_gain_slider = speed_gain_slider
        self.steering_gain_slider = steering_gain_slider
        self.steering_dgain_slider = steering_dgain_slider
        self.steering_bias_slider = steering_bias_slider
        self.last = 0.0
        self.buf = deque(maxlen=5)

    def run(self):
        while self.active:
            frm = self.camera.value
            x, y = self.model(preprocess(frm, self.device, self.mean, self.std))\
                        .detach().float().cpu().numpy().flatten()
            y = (0.5 - y) / 2
            self.x_slider.value = x
            self.y_slider.value = y
            self.image_widget.value = self.camera.value

            ang = np.arctan2(x, y)
            pid = ang * self.steering_gain_slider.value + (ang - self.last) * self.steering_dgain_slider.value
            self.last = ang
            steer = pid + self.steering_bias_slider.value
            self.buf.append(steer)
            s = sum(self.buf) / len(self.buf)

            self.steering_slider.value = s
            sp = self.speed_gain_slider.value * max(1 - abs(s) * 1.5, 0.3)
            self.speed_slider.value = sp

            L = max(min(sp + s, 1), 0)
            R = max(min(sp - s, 1), 0)
            self.robot.left_motor.value = L
            self.robot.right_motor.value = R
            print(f"[Motors] L={L:.2f}, R={R:.2f}")
            time.sleep(0.1)

        self.robot.stop()

    def stop(self):
        self.active = False
        self.robot.stop()