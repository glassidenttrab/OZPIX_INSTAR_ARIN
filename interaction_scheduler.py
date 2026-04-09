import time
import random
import datetime
import sys
import os
from datetime import timedelta
from insta_interactor import InstaInteractor

# Windows 터미널 한글/이모지 출력 인코딩 문제 해결
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def log_to_file(message):
    """스케줄러의 작동 상태를 파일에 기록합니다."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    if not os.path.exists("reports"):
        os.makedirs("reports")
    with open("reports/scheduler_status.log", "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def generate_random_schedule(start_time, end_time, count):
    if count <= 0:
        return []
    
    # 작업 시간을 고르게 분포시키기 위해 구간을 나눔
    interval = (end_time - start_time).total_seconds() / count
    
    times = []
    for i in range(count):
        # 각 구간 내에서 무작위 시간 선택
        sec = i * interval + random.uniform(0, interval)
        times.append(start_time + timedelta(seconds=sec))
    
    return sorted(times)

def run_scheduler():
    interactor = InstaInteractor()
    TOTAL_DAILY_TARGET = 30  # 하루 전체 목표
    
    log_to_file("🚀 인스타그램 상호작용 스케줄러를 시작합니다.")
    log_to_file(f"📍 목표: 하루 {TOTAL_DAILY_TARGET}개, 유동적 스케줄링 적용")
    
    current_date = None
    today_schedule = []
    
    while True:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        
        # 현재까지 완료한 횟수 확인
        done_count = interactor.get_daily_count()
        remaining_count = TOTAL_DAILY_TARGET - done_count
        
        # 날짜가 바뀌었거나 스케줄이 비어있으면 새로 생성
        if date_str != current_date:
            current_date = date_str
            log_to_file(f"📅 새로운 날짜({date_str})의 스케줄을 준비합니다. (완료: {done_count}/{TOTAL_DAILY_TARGET})")
            
            # 오후 5시 이후 늦게 시작하는 경우 안전을 위해 개수 제한 (봇 탐지 방지)
            if now.hour >= 17 and remaining_count > 20:
                log_to_file(f"⚠️ 시작 시간이 늦어 안전을 위해 오늘 남은 작업을 20개로 제한합니다. (원본 남은 수: {remaining_count})")
                remaining_count = 20
            
            if remaining_count <= 0:
                log_to_file("✅ 오늘 목표를 이미 모두 달성했습니다.")
                today_schedule = []
            else:
                end_time = now.replace(hour=23, minute=50, second=0, microsecond=0)
                if now < end_time:
                    today_schedule = generate_random_schedule(now, end_time, remaining_count)
                    log_to_file(f"📋 오늘 남은 {len(today_schedule)}개의 작업을 스케줄링했습니다.")
                else:
                    log_to_file("😴 오늘 작업 시간이 종료되었습니다. 내일 08:00에 다시 시작합니다.")
                    today_schedule = []

        # 오늘 할 일이 더 이상 없는 경우
        if not today_schedule:
            # 다음날 08:00까지 대기
            tomorrow_start = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            wait_sec = (tomorrow_start - now).total_seconds()
            log_to_file(f"😴 오늘 일정이 없습니다. 다음 시작까지 대기합니다. (약 {int(wait_sec/3600)}시간 후)")
            time.sleep(min(3600, wait_sec))
            continue

        # 다음 작업 시간 확인
        next_job_time = today_schedule[0]
        wait_seconds = (next_job_time - now).total_seconds()

        if wait_seconds > 0:
            log_to_file(f"⏳ 다음 작업 예정: {next_job_time.strftime('%H:%M:%S')} (약 {int(wait_seconds // 60)}분 후)")
            # 10분마다 체크하면서 대기
            while (next_job_time - datetime.datetime.now()).total_seconds() > 0:
                time.sleep(min(600, (next_job_time - datetime.datetime.now()).total_seconds()))
        
        # 작업 시각이 되면 실행
        log_to_file("🔄 상호작용 작업을 시작합니다...")
        
        login_status = interactor.login()
        if login_status == "CRITICAL_BAN":
            log_to_file("🚨 치명적 차단 감지! 48시간 동안 모든 활동을 정지합니다.")
            time.sleep(48 * 3600)
            continue
        elif not login_status:
            log_to_file("❌ 로그인 실패. 30분 후 재시도합니다.")
            time.sleep(1800)
            continue

        hashtags = ["AIArt", "CinematicArt", "DigitalArtist", "StableDiffusion", "Midjourney", "CharacterDesign"]
        target_tag = random.choice(hashtags)
        
        success = interactor.interact_with_hashtag(target_tag)
        
        if success == "CRITICAL_BAN":
            log_to_file("🚨 실행 중 차단 감지! 48시간 정지합니다.")
            time.sleep(48 * 3600)
        elif success:
            log_to_file(f"✅ 상호작용 성공! (@{target_tag})")
            # 수행한 스케줄 제거
            today_schedule.pop(0)
        else:
            log_to_file("⚠️ 상호작용 실패. 10분 후 재시도합니다.")
            time.sleep(600)

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        log_to_file("⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        log_to_file(f"🔥 치명적 오류 발생: {e}")
        import traceback
        log_to_file(traceback.format_exc())
        time.sleep(300) # 오류 시 잠시 후 재시작 시도 (service_monitor에 의해)
