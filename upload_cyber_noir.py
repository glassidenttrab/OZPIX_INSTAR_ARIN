import os
from insta_uploader import InstaUploader

def upload_cyber_noir():
    uploader = InstaUploader()
    image_path = "f:/ProJectHome/Ozpix_Instar_Arin/images/cyber_noir_v1.png"
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return

    caption = """🏙️ **Master Style Vol.2: Cyber-Noir Urban Rain**

이번에는 황야의 고독과는 또 다른, 비에 젖은 네온빛 도시의 분위기를 연출해 보았습니다.

블레이드 러너 스타일의 시네마토그래피와 하이패션 에디토리얼의 조화:
- **Style:** Neon-Noir / Urban Cinematic
- **Atmosphere:** Rainy Tokyo Alley / Vibrant Reflections
- **Lighting:** Cyber-Blue & Electric Pink Dual-Tone
- **Detail:** Micro-droplets of rain on skin & High-contrast textures

대장님의 마스터 프롬프트 구조는 어떤 환경에서도 압도적인 시각적 서사를 만들어냅니다. 🎨✨

#CyberNoir #UrbanRain #NeonAesthetic #Instagram2026 #BladeRunnerStyle #AIArt #CinematicVibes #ArinAgent"""

    print("📸 사이버-노아 스타일 업로드 시작...")
    post_id = uploader.upload_image(image_path, caption)
    
    if post_id:
        print(f"✅ 업로드 성공! 포스트 ID: {post_id}")
    else:
        print("❌ 업로드 실패.")

if __name__ == "__main__":
    upload_cyber_noir()
