import time
import random
import datetime
import sys
from insta_interactor import InstaInteractor

def run_scheduler():
    interactor = InstaInteractor()
    
    print("🚀 인스타그램 상호작용 스케줄러를 시작합니다.")
    print("📍 조건: 하루 최대 50개, 간격 5분~30분 랜덤")
    
    if not interactor.login():
        print("❌ 로그인을 완료할 수 없어 종료합니다. .env 설정을 확인해주세요.")
        sys.exit(1)

    while True:
        now = datetime.datetime.now()
        count = interactor.get_daily_count()
        
        if count >= 50:
            print(f"✅ 오늘 할당량(50개)을 모두 채웠습니다. 내일 다시 시작합니다. (현재 시간: {now})")
            # 다음 날 오전 0시 이후까지 대기
            time.sleep(3600) 
            continue
            
        print(f"🔄 현재 오늘 수행 횟수: {count}/50")
        
        # 해시태그 리스트 (다양성을 위해)
        hashtags = ["AIArt", "CinematicArt", "DigitalArtist", "StableDiffusion", "Midjourney"]
        target_tag = random.choice(hashtags)
        
        success = interactor.interact_with_hashtag(target_tag)
        
        if success:
            # 5분(300s) ~ 30분(1800s) 사이 랜덤 대기
            wait_time = random.randint(300, 1800)
            next_run = now + datetime.timedelta(seconds=wait_time)
            print(f"⏳ 대기 중... 다음 실행 예정: {next_run.strftime('%H:%M:%S')} ({wait_time // 60}분 후)")
            time.sleep(wait_time)
        else:
            print("⚠️ 실행 실패. 5분 후 재시도합니다.")
            time.sleep(300)

if __name__ == "__main__":
    run_scheduler()
