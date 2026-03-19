import os
from insta_uploader import InstaUploader

def test_master_style_upload():
    uploader = InstaUploader()
    image_path = "f:/ProJectHome/Ozpix_Instar_Arin/images/master_style_test.png"
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return

    caption = """🎭 **Master Style Test: Beauty in Isolation**

대장님이 전해주신 정교한 '마스터 프롬프트 구조'를 아린의 스킬에 완벽하게 박제했습니다. 

이제 매일 생성될 이미지는 이와 같은 극사실주의 시네마틱 퀄리티를 지향합니다.
- **Style:** Neo-Cinematic / Analog Texture
- **Atmosphere:** Golden Hour / Wilderness Solitude
- **Detail:** Hyper-real Skin & Chrome Reflections

새로운 아린의 모습을 기대해 주세요. 🎨✨

#NeoCinematic #AIArt #MasterPrompt #Instagram2026 #HyperRealism #ArinAgent #AnalogVibes"""

    print("📸 마스터 스타일 테스트 업로드 시작...")
    post_id = uploader.upload_image(image_path, caption)
    
    if post_id:
        print(f"✅ 테스트 성공! 포스트 ID: {post_id}")
    else:
        print("❌ 업로드 실패.")

if __name__ == "__main__":
    test_master_style_upload()
