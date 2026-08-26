"""IMU - 방위/자세(roll,pitch)/자이로/캘리브레이션 실시간 출력."""
import time

import pinkyzero
from pinkyzero import IMU

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkyzero.connect(HOST)
imu = IMU()

# 처음 한 번 캘리브레이션 — 안내대로 로봇을 움직이면 값이 정확해져요.
# (그냥 값만 보고 싶으면 이 줄을 지우고 imu.enable(True) 만 하세요)
imu.calibrate()

print("로봇을 돌려보세요. Ctrl+C 로 종료")
try:
    while True:
        h, r, p = imu.read_euler()
        print(f"heading {h}°  roll {r}°  pitch {p}°  "
              f"gyro {imu.read_gyro()}  accel {imu.read_accel()}  "
              f"calib(s/g/a/m) {imu.calibration_status()}")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\n종료")

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
