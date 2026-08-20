from setuptools import setup, find_packages

setup(
    name="pinkylib",
    version="0.2",
    description="Pinky Zero PC client library (WebSocket remote control)",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "websocket-client",
        "numpy",           # LCD.image() 의 RGB565 변환
        "pillow",          # LCD.image() 로 이미지 파일 열기
        "opencv-python",   # 카메라 read_array / 영상 예제
    ],
)
