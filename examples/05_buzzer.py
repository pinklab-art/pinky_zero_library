"""Buzzer - 알림음 / 음이름 / 멜로디 / 상황별 소리."""
import time

import pinkyzero
from pinkyzero import Buzzer

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다

pinkyzero.connect(HOST)
bz = Buzzer()

print("알림음 1번 (4kHz - 가장 크게 들리는 소리)")
bz.beep()
time.sleep(0.5)

print("알림음 3번")
bz.beep(count=3)
time.sleep(0.5)

print("계이름으로: 도레미파솔")
bz.melody("도 레 미 파 솔")
time.sleep(0.5)

print("영어 계이름도 같다: do re mi fa sol")
bz.melody("do re mi fa sol")
time.sleep(0.5)

print("영어 음이름도 가능: C5 E5 G5")
bz.melody(["C5", "E5", "G5"])
time.sleep(0.5)

print("음마다 길이 다르게 (작은 별)")
bz.melody([("도", 300), ("도", 300), ("솔", 300), ("솔", 300),
           ("라", 300), ("라", 300), ("솔", 600)])
time.sleep(0.5)

bz.close()
print("완료")

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
