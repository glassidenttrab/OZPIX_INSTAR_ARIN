@echo off
echo 스케줄러(interaction_scheduler.py)를 종료합니다...
wmic process where "name='pythonw.exe' and commandline like '%%interaction_scheduler.py%%'" call terminate
echo 종료 완료.
pause
