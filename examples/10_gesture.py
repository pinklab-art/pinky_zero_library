"""Gesture - 터치 제스처 인식 테스트.

화면을 상/하/좌/우로 스와이프하거나 탭/더블탭/롱프레스 해보세요.
서버가 순간 제스처를 래치(~350ms)해서 놓칠 확률을 낮춥니다.
"""
import time

import pinkyzero
from pinkyzero import LCD

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkyzero.connect(HOST)
lcd = LCD()
lcd.enable(True)                # 터치 측정 ON

emoji = {"up": "⬆️  위로", "down": "⬇️  아래로", "left": "⬅️  왼쪽",
         "right": "➡️  오른쪽", "click": "👆 탭", "double": "✌️ 더블탭",
         "long": "✊ 롱프레스"}

print("스와이프/탭 해보세요 (Ctrl+C 종료)")
n = 0
try:
    while True:
        g = lcd.wait_gesture(timeout=30)
        if g:
            n += 1
            print(f"[{n:3d}] {emoji.get(g, g)}   ({g})")
except KeyboardInterrupt:
    print(f"\n총 {n}개 제스처 인식. 종료")

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
