"""Motion - 광학 마우스 센서(PAT9125) dx/dy 델타."""
from ._client import client


class Motion:
    def read(self):
        """(dx, dy) 델타."""
        st = client().require("pico")
        return st.get("motion_dx"), st.get("motion_dy")

    def close(self):
        pass
