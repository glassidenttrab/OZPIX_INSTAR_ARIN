from insta_uploader import InstaUploader

def run_cinematic_upload():
    # 아린 에이전트 초기화
    arin = InstaUploader()
    
    # 이미지 파일 경로
    local_image_path = "mysterious_woman_motorcycle.png"
    
    # 포스팅 내용 구성
    caption = """🌵 Beauty in Isolation: A Forgotten Crossing

황량한 황야의 끝, 잊혀진 버스 정류장에서 만난 신비로운 분위기. 
붉은 빈티지 바이크와 그녀의 고요하지만 자신감 넘치는 시선을 느껴보세요. 🛵✨

🎨 Cinematic Specs:
- Style: Neo-Cinematic with Analog Film Texture
- Palette: Dusty earth tones & Golden hour glow
- Inspiration: Denis Villeneuve desert cinematography

이번 이미지는 '고립 속의 아름다움'을 테마로, 극도의 하이퍼리얼리즘과 아날로그적인 불완전함을 담아냈습니다.

#AI아트 #하이퍼리얼리즘 #시네마틱 #빈티지바이크 #인공지능그림 #아린에이전트 #CinematicArt #8kMasterpiece #GoldenHour #DesertSolitude #ModernCyborgWestern
"""

    print("🚀 시네마틱 포트레이트 포스팅을 시작합니다...")
    post_id = arin.upload_image(image_source=local_image_path, caption=caption)
    
    if post_id:
        print(f"✅ 포스팅 완료! (ID: {post_id})")
    else:
        print("❌ 업로드에 실패했습니다.")

if __name__ == "__main__":
    run_cinematic_upload()
