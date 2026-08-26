"""Quickstart - 연결 → 센서 켜기 → 배터리/방위 한 번 읽기."""
import time

import pinkyzero
from pinkyzero import Battery, IMU

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkyzero.connect(HOST)          # 로봇 IP (한 번)
print("연결:", pinkyzero.client().connected)

pinkyzero.enable_all()           # IMU·터치 측정 ON (보드 그룹은 로봇이 켜둔다)
time.sleep(0.4)                 # 첫 측정 프레임 도착 대기

print("배터리:", Battery().get_voltage(), "V /", Battery().get_percentage(), "%")
print("방위(heading):", IMU().heading(), "도")

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
