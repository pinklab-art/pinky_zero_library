"""read_array() - 카메라 프레임에 필터를 걸어 한 창에 나란히 보기.

원본 / 흑백 / 메디안 / 가우시안 / 윤곽선을 실시간으로 비교한다.
  q  종료
  s  지금 화면을 vision_grid.jpg 로 저장
"""
import time

import cv2
import numpy as np

import pinkyzero
from pinkyzero import Camera

HOST = "192.168.7.1"        # 로봇 주소. 로봇 AP(pinky_zxxxx)에 붙었으면 이대로,
                            # 공유기를 거쳐 붙으면 로봇 IP 로 바꾼다
WIN = "Pinky Zero - filters"


def to_bgr(img):
    """흑백(1채널)이면 3채널로. 한 창에 붙이려면 채널 수가 같아야 한다."""
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def put_label(img, text):
    """왼쪽 위에 이름. 검은 테두리를 먼저 그려야 밝은 배경에서도 읽힌다."""
    out = img.copy()
    for color, thick in ((0, 0, 0), 3), ((255, 255, 255), 1):
        cv2.putText(out, text, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thick)
    return out


pinkyzero.connect(HOST)
cam = Camera()
cam.start(fps=15)
time.sleep(0.5)

print("창이 뜹니다.  q = 종료,  s = 저장")
while True:
    frame = cam.read_array()          # JPEG 대신 OpenCV BGR 배열
    if frame is None:
        print("프레임이 안 옵니다. 로봇 카메라가 켜져 있는지 확인하세요.")
        break

    filtered = {
        "original": frame,
        "gray":     cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
        "median":   cv2.medianBlur(frame, 9),        # 점 노이즈 제거. 커널은 홀수
        "gaussian": cv2.GaussianBlur(frame, (9, 9), 0),
        "canny":    cv2.Canny(frame, 100, 200),      # 윤곽선
    }

    tiles = [put_label(to_bgr(img), name) for name, img in filtered.items()]
    tiles.append(np.zeros_like(tiles[0]))            # 3x2 격자의 빈 칸
    grid = np.vstack([np.hstack(tiles[0:3]), np.hstack(tiles[3:6])])

    cv2.imshow(WIN, grid)

    key = cv2.waitKey(30) & 0xFF
    if key == ord("q"):
        break
    if key == ord("s"):
        cv2.imwrite("vision_grid.jpg", grid)
        print("저장: vision_grid.jpg")
    # 창의 닫기 버튼을 눌렀을 때도 빠져나온다
    if cv2.getWindowProperty(WIN, cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
cam.close()

pinkyzero.disconnect()   # 로봇을 코딩모드에서 내보낸다.
                        # 안 부르면 이 프로그램이 살아있는 동안 로봇 화면이
                        # 코딩모드에 묶여 있고, 로봇 3번 버튼도 안 먹는다.
