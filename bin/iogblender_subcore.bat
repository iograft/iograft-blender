@echo off

:: Start blender in the background and execute the given Python script.
blender.exe --background --python-use-system-env --python "%~dp0\iogblenderpy_subcore.py" -- %*
