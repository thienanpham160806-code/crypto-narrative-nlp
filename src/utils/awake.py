"""Giữ máy không tự ngủ khi đang cắm sạc, chỉ trong lúc tiến trình này chạy (Windows; nơi khác: không làm gì).

Dùng SetThreadExecutionState: hết tiến trình → Windows tự trả lại chế độ ngủ bình thường, không đổi cài đặt nguồn.
Chạy pin → nhả yêu cầu để máy ngủ như thường. Không chặn gập nắp (lid) – đó là cài đặt riêng của Windows.
"""
from __future__ import annotations
import ctypes, sys, threading

ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001


class _Power(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte), ("BatteryLifePercent", ctypes.c_ubyte),
                ("SystemStatusFlag", ctypes.c_ubyte), ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]


def on_ac() -> bool:
    s = _Power()
    return bool(ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))) and s.ACLineStatus == 1


def keep_awake_on_ac(every: int = 60) -> None:
    """Luồng nền: mỗi `every` giây, cắm sạc → giữ thức; rút sạc → cho ngủ."""
    if sys.platform != "win32":
        return

    def loop():
        k = ctypes.windll.kernel32
        while True:
            k.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on_ac() else 0))
            threading.Event().wait(every)

    threading.Thread(target=loop, daemon=True).start()
