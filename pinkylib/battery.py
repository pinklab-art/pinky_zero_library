"""배터리 - 전압 / 잔량(SOC). (제로 서버의 캐시된 상태를 읽음)"""
from ._client import client


class Battery:
    def get_voltage(self):
        """배터리 전압 [V]."""
        return client().field("batt_V", "pico")

    def get_percentage(self):
        """배터리 잔량 [%] (0~100)."""
        return client().field("soc", "pico")

    def close(self):
        pass
