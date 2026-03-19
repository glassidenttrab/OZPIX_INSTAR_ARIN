import os
import sys
from moviepy.editor import ImageClip, VideoClip
from PIL import Image

def generate_zoom_video(image_path, output_path, duration=7, zoom_ratio=1.2):
    """이미지를 줌인 효과가 있는 동영상으로 변환합니다 (노이즈 방지 로직 적용)."""
    print(f"🎬 동영상 생성 시작: {image_path}")
    
    # 이미지 로드 및 Instagram 표준 비율(1080x1350 또는 1080x1920)로 리사이즈 준비
    clip = ImageClip(image_path).set_duration(duration)
    w, h = clip.size
    
    # 짝수 크기로 조정 (코덱 호환성 위해 필수)
    if w % 2 != 0: w -= 1
    if h % 2 != 0: h -= 1
    clip = clip.resize(newsize=(w, h))

    # 줌 효과: 각 프레임을 수동으로 크롭하여 줌 효과 구현 (더 안정적임)
    def make_frame(t):
        # 1.0(시작) -> zoom_ratio(끝)
        scale = 1 + (zoom_ratio - 1) * (t / duration)
        
        # 확대된 크기 계산
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # 이미지 확대
        # get_frame(t)는 numpy array를 반환함
        frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        resized_img = img.resize((new_w, new_h), Image.LANCZOS)
        
        # 중앙 크롭 (원래 크기 w, h로 유지)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        right = left + w
        bottom = top + h
        
        cropped_img = resized_img.crop((left, top, right, bottom))
        import numpy as np
        return np.array(cropped_img)

    # 새로운 비디오 클립 생성
    new_clip = VideoClip(make_frame, duration=duration)
    
    # 동영상 파일로 저장 (FPS 30, libx264, yuv420p로 호환성 극대화)
    new_clip.write_videofile(output_path, fps=30, codec="libx264", audio=False, 
                             ffmpeg_params=["-pix_fmt", "yuv420p"])
    print(f"✅ 동영상 생성 완료: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python image_to_video.py <이미지경로> [출력경로]")
    else:
        img_path = sys.argv[1]
        out_path = sys.argv[2] if len(sys.argv) > 2 else "output_video.mp4"
        generate_zoom_video(img_path, out_path)
