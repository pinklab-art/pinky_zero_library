"""Camera - 스냅샷 저장 + 실시간 영상 창으로 보기.

로봇에 picamera2 가 있어야 동작.
"""
import time

import cv2

import pinkyzero
from pinkyzero import Camera

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다
WIN = "Pinky Zero"

pinkyzero.connect(HOST)
cam = Camera()
cam.start(fps=15)
time.sleep(0.5)

# 1) 스냅샷 저장
jpg = cam.snapshot()          # JPEG 바이트
with open("shot.jpg", "wb") as f:
    f.write(jpg)
print(f"스냅샷 저장: {len(jpg)} bytes → shot.jpg")

# 2) 실시간 영상
print("창이 뜹니다. 끄려면 창을 고른 뒤 q 를 누르세요.")
while True:
    frame = cam.read_array()          # 최신 프레임을 OpenCV BGR 배열로
    if frame is None:
        print("프레임이 안 옵니다. 로봇 카메라가 켜져 있는지 확인하세요.")
        break

    cv2.imshow(WIN, frame)

    if cv2.waitKey(30) & 0xFF == ord("q"):
        break
    # 창의 닫기 버튼을 눌렀을 때도 빠져나온다
    if cv2.getWindowProperty(WIN, cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
cam.close()

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
