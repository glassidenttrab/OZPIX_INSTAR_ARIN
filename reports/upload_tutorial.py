from insta_uploader import InstaUploader

def run_upload():
    # 이제 로컬 파일을 바로 업로드할 수 있습니다!
    arin = InstaUploader()
    
    # 우리가 만든 이미지 파일 경로
    local_image_path = "ai_art_tutorial_cover.png"
    
    caption = """🎨 [AI 이미지 생성 꿀팁] 당신도 아티스트가 될 수 있습니다!

인공지능으로 멋진 이미지를 만드는 핵심은 바로 '프롬프트(Prompt)'입니다. 
복잡하게 생각하지 마세요! 아래 3단계 공식만 기억하세요:

1️⃣ 주제 (Subject): 무엇을 그릴 것인가?
2️⃣ 스타일 (Style): 어떤 느낌인가?
3️⃣ 디테일 (Detail): 세부 묘사는?

⭐ 오늘 사용된 프롬프트:
"A futuristic workspace where a high-tech computer screen shows a digital painting created by glowing neural networks, vibrant colors, neon accents."

이제 여러분만의 창의력을 AI와 함께 펼쳐보세요! ✨

#AI아트 #인공지능그림 #프롬프트입문 #디지털아트 #AI학습 #아린에이전트 #인공지능에이전트 #AIArtist #FutureTech
"""

    print("🚀 우리가 직접 만든 이미지를 인스타그램에 업로드합니다!")
    post_id = arin.upload_image(image_source=local_image_path, caption=caption)
    
    if post_id:
        print(f"✅ 드디어 성공! 포스팅 완료되었습니다. (ID: {post_id})")
    else:
        print("❌ 업로드에 실패했습니다. 로그를 확인해 주세요.")

if __name__ == "__main__":
    run_upload()
