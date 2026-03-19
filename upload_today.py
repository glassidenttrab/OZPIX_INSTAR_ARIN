import os
from insta_uploader import InstaUploader
from arin_master import ArinMasterAgent

def upload_today_content():
    print("🚀 오늘자 콘텐츠 업로드 프로세스 시작...")
    
    # 1. 아린 마스터 에이전트 초기화
    arin = ArinMasterAgent()
    
    # 2. 오늘 날짜 및 정보 설정
    import datetime
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    image_path = f"f:/ProJectHome/Ozpix_Instar_Arin/images/day_{today}.png"
    
    # 리포트 파일에서 캡션과 해시태그 추출 (또는 직접 설정)
    caption = """🎨 2026년 인스타그램 알고리즘, 아직도 헤매시나요?

이제는 팔로워 숫자가 중요한 시대가 아닙니다. 
당신의 콘텐츠가 얼마나 많은 사람들에게 '저장'되느냐가 도달의 핵심!

오늘의 아린 인사이트:
1️⃣ 단순함보다는 깊이: 3초 이상 멈추게 만드는 시각적 데이터.
2️⃣ 저장 유도: 나중에 꺼내 보고 싶은 꿀팁 전수.
3️⃣ DM 대화: 댓글보다 강력한 것이 바로 공유입니다.

미래의 소셜 미디어 성장은 아린 에이전트와 함께하세요. 🚀✨"""

    hashtags = "#Instagram2026 #알고리즘해킹 #소셜미디어마케팅 #AI에이전트 #아린 #인스타성장 #GrowthHacking #DigitalTrend #AlgorithmSecrets"
    full_caption = f"{caption}\n\n{hashtags}"

    # 3. 업로드 실행
    if not os.path.exists(image_path):
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
        return

    print(f"📸 업로드 중: {image_path}")
    post_id = arin.uploader.upload_image(image_path, full_caption)
    
    if post_id:
        print(f"✅ 업로드 성공! 포스트 ID: {post_id}")
        
        # 4. 캘린더 상태 수정
        calendar = arin.load_calendar()
        for item in calendar:
            if item["date"] == today:
                item["status"] = "completed"
                item["post_id"] = post_id
                break
        arin.save_calendar(calendar)
        print("📅 캘린더 상태가 'completed'로 업데이트되었습니다.")
    else:
        print("❌ 업로드에 실패했습니다.")

if __name__ == "__main__":
    upload_today_content()
