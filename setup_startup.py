import os
import sys

def create_startup_script():
    # 1. pythonw.exe 경로 찾기 (콘솔창을 숨기고 백그라운드 실행하기 위함)
    python_dir = os.path.dirname(sys.executable)
    pythonw_exe = os.path.join(python_dir, "pythonw.exe")
    
    if not os.path.exists(pythonw_exe):
        # pythonw.exe를 찾을 수 없으면 일반 python.exe를 사용하되 창을 숨기는 옵션 적용
        pythonw_exe = sys.executable
    
    # 2. 작업 디렉토리 및 실행할 스크립트 경로 설정
    project_dir = os.path.abspath(os.path.dirname(__file__))
    target_script = "interaction_scheduler.py"
    
    # 3. 윈도우 시작프로그램(Startup) 폴더 경로 알아내기
    appdata = os.environ.get("APPDATA")
    startup_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    
    # 4. 시작프로그램 폴더에 생성할 VBScript 파일 경로
    vbs_path = os.path.join(startup_dir, "Arin_Interaction_Scheduler.vbs")
    
    # 5. VBScript 코드 작성 (현재 디렉토리를 프로젝트 폴더로 지정하고 창을 숨긴 채 0번 옵션으로 실행)
    vbs_code = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{project_dir}"
WshShell.Run "{pythonw_exe} {target_script}", 0, False
"""

    # 6. 파일 저장
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_code)
        
        print(f"✅ 부팅 시 스케줄러가 백그라운드 자동 실행되도록 설정 완료했습니다!")
        print(f"📍 생성된 파일 위치: {vbs_path}")
        print(f"📍 실행 프로그램: {pythonw_exe} {target_script}")
        print("\n▶️ 재부팅을 하지 않고 [지금 바로 백그라운드에서 실행] 하려면 윈도우 콘솔에서 아래 명령어를 1회 입력해 주세요:")
        print(f"wscript.exe \"{vbs_path}\"")
        
        # 만약 스케줄러 중단용 배치 파일도 함께 만들어 주면 좋습니다.
        kill_bat_path = os.path.join(project_dir, "stop_scheduler.bat")
        with open(kill_bat_path, "w", encoding="utf-8") as bf:
            # pythonw.exe로 돌아가는 interaction_scheduler만 안전하게 종료하기 위해 wmic 이용 추적 종료
            bf.write('@echo off\n')
            bf.write('echo 스케줄러(interaction_scheduler.py)를 종료합니다...\n')
            bf.write('wmic process where "name=\'pythonw.exe\' and commandline like \'%%interaction_scheduler.py%%\'" call terminate\n')
            bf.write('echo 종료 완료.\n')
            bf.write('pause\n')
            
        print(f"\n⏹️ (참고) 백그라운드에서 도는 스케줄러를 강제로 끄고 싶을 때는 새로 생성된 '{kill_bat_path}' 파일을 더블클릭하시면 됩니다.")
        
    except Exception as e:
        print(f"❌ 설정 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    create_startup_script()
