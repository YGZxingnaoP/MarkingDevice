@echo off
cd /d %~dp0
env\python.exe -m streamlit run main.py
pause