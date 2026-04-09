import time
import subprocess
import os
import sys

# 감시할 스크립트 목록
TARGET_SCRIPTS = [
    "arin_master.py",
    "interaction_scheduler.py"
]

LOG_FILE = "reports/service_monitor.log"

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def is_process_running(script_name):
    try:
        # Windows tasklist 명령을 사용해 해당 스크립트가 실행 중인지 확인
        # (주의: command line 인자에 스크립트 이름이 포함되어 있어야 함)
        cmd = f'wmic process where "name=\'python.exe\'" get CommandLine'
        output = subprocess.check_output(cmd, shell=True).decode('cp949', errors='ignore')
        return script_name in output
    except:
        return False

def start_script(script_name):
    log(f"🚀 {script_name} 재시작 시도 중...")
    try:
        # 창 없이(No Window) 백그라운드 프로세스로 실행
        # Windows 전용 플래그인 CREATE_NO_WINDOW(0x08000000)를 사용합니다.
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen([sys.executable, script_name], 
                         creationflags=CREATE_NO_WINDOW)
        log(f"✅ {script_name}를 백그라운드 모드로 시작했습니다.")
    except Exception as e:
        log(f"❌ {script_name} 시작 중 오류 발생: {e}")

def monitor():
    log("📡 서비스 모니터링을 시작합니다.")
    while True:
        for script in TARGET_SCRIPTS:
            if not is_process_running(script):
                log(f"⚠️ {script}가 실행 중이지 않습니다.")
                start_script(script)
            else:
                # 너무 잦은 로그 방지 (선택 사항)
                pass
        
        # 5분마다 상태 확인
        time.sleep(300)

if __name__ == "__main__":
    # reports 폴더가 없으면 생성
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    # 중복 실행 방지 기능은 생략 (필요 시 추가)
    monitor()
