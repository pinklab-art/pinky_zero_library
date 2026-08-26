"""pinkyzero (Pinky Zero, PC용) - WebSocket으로 제로 서버를 원격 제어.

    import pinkyzero
    pinkyzero.connect()                     # 한 번만. 기본 192.168.7.1
    pinkyzero.disconnect()                  # 다 쓰면. 로봇이 자기 화면으로 돌아간다

    from pinkyzero import Battery, IR, Motor, LED, Camera
    print(Battery().get_voltage())
    Motor().set_rpm(30, 30)
"""
import importlib
from typing import TYPE_CHECKING

from ._client import (   # noqa: F401
    DEFAULT_HOST, connect, disconnect, client, enable_imu, enable_touch,
    enable_all, sensor_enabled, SensorOffError,
)

_FUNCS = ["DEFAULT_HOST", "connect", "disconnect", "client",
          "enable_imu", "enable_touch", "enable_all", "sensor_enabled",
          "SensorOffError"]

_LAZY = {
    "Battery": ".battery",
    "IR": ".ir",
    "Motion": ".motion",
    "Button": ".button",
    "IMU": ".imu",
    "Motor": ".motor",
    "LED": ".led",
    "Camera": ".camera",
    "Buzzer": ".buzzer",
    "LCD": ".lcd",
    "Mic": ".mic",
    "Speaker": ".speaker",
}

__all__ = list(_LAZY) + _FUNCS

if TYPE_CHECKING:
    from .battery import Battery
    from .ir import IR
    from .motion import Motion
    from .button import Button
    from .imu import IMU
    from .motor import Motor
    from .led import LED
    from .camera import Camera
    from .buzzer import Buzzer
    from .lcd import LCD
    from .mic import Mic
    from .speaker import Speaker


def __getattr__(name):
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    obj = getattr(importlib.import_module(module, __name__), name)
    globals()[name] = obj
    return obj


def __dir__():
    return sorted(_LAZY) + _FUNCS
