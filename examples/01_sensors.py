"""센서 읽기 - 배터리/바닥IR/거리IR/모션/버튼/엔코더를 0.5초마다 출력."""
import time

import pinkylib
from pinkylib import Battery, IR, Motion, Button, Motor

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkylib.connect(HOST)
time.sleep(0.4)                 # 첫 측정 프레임 도착 대기

batt, ir, mot, btn = Battery(), IR(), Motion(), Button()
enc = Motor(auto_enable=False)  # 엔코더 읽기용 (모터는 켜지 않음)

print("Ctrl+C 로 종료")
try:
    while True:
        print(f"배터리 {batt.get_voltage()}V  "
              f"바닥IR {ir.read_floor()}  거리IR {ir.read_range()}  "
              f"모션 {mot.read()}  버튼 {btn.read()}  엔코더 {enc.get_encoder()}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n종료")

pinkylib.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
