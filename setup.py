# setup.py
from cx_Freeze import setup, Executable

setup(
    name="PingApp",
    version="1.0",
    description="Ping & MAC Monitor",
    executables=[Executable("pingmon.py", base="Win32GUI")]
)
