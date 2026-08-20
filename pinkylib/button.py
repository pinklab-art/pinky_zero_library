"""Button - 버튼 3개 상태 (bit0=전원버튼). 1=안눌림, 0=눌림."""
from ._client import client


class Button:
    def read(self):
        """[b0, b1, b2] (각 0/1)."""
        v = client().require("pico").get("buttons")
        if v is None:
            return None
        return [(v >> i) & 1 for i in range(3)]

    def is_pressed(self, index=0):
        """index 버튼이 눌렸는지 (0=눌림 → True)."""
        b = self.read()
        return b is not None and b[index] == 0

    def close(self):
        pass
