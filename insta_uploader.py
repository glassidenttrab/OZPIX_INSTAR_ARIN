import sys
import os
import time
import datetime
import requests
import json
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Windows 터미널 한글/이모지 출력 인코딩 문제 해결
# if sys.stdout.encoding != 'utf-8':
#     try:
#         sys.stdout.reconfigure(encoding='utf-8')
#     except AttributeError:
#         # Python 3.7 이전 버전 대응
#         import io
#         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .env 파일 로드
load_dotenv()

class InstaUploader:
    def __init__(self):
        self.acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        
        if not self.acc_id or not self.token:
            # 환경변수가 없으면 직접 전달된 값을 확인하거나 에러를 발생시킵니다.
            pass
            
        self.version = "v23.0"  # 최신 v23.0 규격 적용
        self.base_url = f"https://graph.instagram.com/{self.version}/{self.acc_id}"
        
    def _preprocess_image(self, local_path):
        """이미지를 인스타그램 권장 규격(PNG, 1080x1080)으로 보정합니다."""
        print(f"🎨 이미지 규격 보정 중 (1080x1080 PNG): {os.path.basename(local_path)}")
        try:
            img = Image.open(local_path)
            # 투명도가 있을 경우 배경을 흰색으로 처리하여 RGB로 변환
            if img.mode in ('RGBA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 인스타그램 권장 규격 1:1 리사이즈
            img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
            
            # 임시 파일 경로 설정 (가장 표준적인 PNG로 저장)
            processed_path = local_path.replace(".png", "_insta.png").replace(".jpg", "_insta.png")
            img.save(processed_path, "PNG", optimize=False)
            return processed_path
        except Exception as e:
            print(f"⚠️ 전처리 실패 (원본 시도): {e}")
            return local_path

    def _make_public_url(self, local_path):
        """로컬 이미지를 Catbox를 통해 공용 URL로 변환합니다. (Litterbox 제거하여 안정성 확보)"""
        # 1. 이미지 전처리 수행
        target_path = self._preprocess_image(local_path)
        
        print(f"🌐 Catbox를 통해 공용 URL 변환 시도 중...")
        try:
            with open(target_path, 'rb') as f:
                # 인스타그램의 안정적인 크롤링을 위해 Litterbox(24h)로 우선 시도
                url = "https://litterbox.catbox.moe/resources/internals/api.php"
                files = {"fileToUpload": f}
                data = {"reqtype": "fileupload", "time": "24h"}
                res = requests.post(url, files=files, data=data)
                
                if res.status_code == 200:
                    public_url = res.text.strip()
                    print(f"🌐 임시 공개 URL 생성 완료 (Litterbox): {public_url}")
                    return public_url
                else:
                    # 실패 시 Catbox(영구)로 대안 시도
                    f.seek(0)
                    url = "https://catbox.moe/user/api.php"
                    data = {"reqtype": "fileupload"}
                    res = requests.post(url, files={"fileToUpload": f}, data=data)
                    if res.status_code == 200:
                        public_url = res.text.strip()
                        print(f"🌐 임시 공개 URL 생성 완료 (Catbox): {public_url}")
                        return public_url
                        
        except Exception as e:
            print(f"⚠️ Catbox 업로드 오류: {e}")
                
        return None

    def _verify_url(self, url):
        """생성된 URL이 실제로 유효한 이미지인지 확인합니다."""
        try:
            # 인스타그램 크롤러와 유사한 환경에서 테스트
            headers = {'User-Agent': 'Facebot'} 
            res = requests.head(url, headers=headers, timeout=10)
            if res.status_code == 200:
                content_type = res.headers.get('Content-Type', '')
                if 'image' in content_type or url.lower().endswith(('.jpg', '.jpeg', '.png')):
                    return True
            return False
        except:
            return False

    def upload_image(self, image_source, caption=""):
        """이미지를 인스타그램에 게시합니다. (로컬 경로 또는 URL 모두 지원)"""
        
        # 주소가 로컬 파일 경로인 경우 공용 URL로 변환
        if os.path.exists(image_source):
            image_url = self._make_public_url(image_source)
            if not image_url:
                return None
        else:
            image_url = image_source

        print(f"📸 이미지 업로드 시작 (Instagram): {image_url}")
        
        # 1. 컨테이너 생성
        # Instagram API는 특정 계정 ID(ozpixinstar의 ID)를 사용해야 할 수도 있습니다.
        # 여기서는 초기화 시 설정된 ID를 사용합니다.
        # 만약 계정 ID가 바뀌었다면, /me 엔드포인트를 통해 확인하는 로직이 필요할 수 있습니다.
        
        target_id = self.acc_id
        # 테스트 결과 확인된 실제 유저 ID (필요시 업데이트)
        # target_id = "26673183542267603" 

        res = requests.post(f"https://graph.instagram.com/{self.version}/{target_id}/media", data={
            "image_url": image_url,
            "caption": caption,
            "access_token": self.token
        }).json()
        
        if "id" not in res:
            # 만약 acc_id가 앱 ID라면 실제 유저 ID로 재시도
            if "error" in res and "26673183542267603" not in str(res):
                print("🔄 유저 ID 확인 중...")
                me_res = requests.get(f"https://graph.instagram.com/{self.version}/me?fields=id&access_token={self.token}").json()
                if "id" in me_res:
                    target_id = me_res["id"]
                    res = requests.post(f"https://graph.instagram.com/{self.version}/{target_id}/media", data={
                        "image_url": image_url,
                        "caption": caption,
                        "access_token": self.token
                    }).json()

        if "id" not in res:
            print(f"❌ 컨테이너 생성 실패: {res}")
            import json
            error_data = {
                "step": "container_creation",
                "timestamp": datetime.datetime.now().isoformat(),
                "image_url": image_url,
                "response": res
            }
            with open("graph_err.json", "w", encoding="utf-8") as f:
                json.dump(error_data, f, indent=4, ensure_ascii=False)
            return None
            
        creation_id = res.get("id")
        print(f"⏳ 서버 처리 대기... (컨테이너 ID: {creation_id})")
        
        # 인스타그램 서버 처리를 위해 대기 (안전하게 45초)
        time.sleep(45) 

        # 2. 최종 발행
        publish_res = requests.post(f"https://graph.instagram.com/{self.version}/{target_id}/media_publish", data={
            "creation_id": creation_id,
            "access_token": self.token
        }).json()
        
        if "id" not in publish_res:
            print(f"❌ 최종 발행 실패: {publish_res}")
            # 에러 상세 기록
            import json
            error_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "image_url": image_url,
                "response": publish_res
            }
            with open("graph_err.json", "w", encoding="utf-8") as f:
                json.dump(error_data, f, indent=4, ensure_ascii=False)
            return None
            
        post_id = publish_res.get("id")
        print(f"🚀 포스팅 성공! (포스트 ID: {post_id})")
        return post_id

    def upload_reels(self, video_source, caption=""):
        """릴스(영상)를 인스타그램에 게시합니다. (로컬 경로 지원)"""
        if os.path.exists(video_source):
            video_url = self._make_public_url(video_source)
            if not video_url: return None
        else:
            video_url = video_source

        print(f"🎬 릴스 업로드 시작: {video_url}")
        
        # 1. 컨테이너 생성 (REELS용)
        res = requests.post(f"https://graph.instagram.com/{self.version}/{self.acc_id}/media", data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.token
        }).json()
        
        if "id" not in res:
            print(f"❌ 릴스 컨테이너 생성 실패: {res}")
            return None
            
        creation_id = res.get("id")
        print(f"⏳ 릴스 서버 처리 중... (60초 대기)")
        
        time.sleep(60)

        # 2. 최종 발행
        publish_res = requests.post(f"https://graph.instagram.com/{self.version}/{self.acc_id}/media_publish", data={
            "creation_id": creation_id,
            "access_token": self.token
        }).json()
        
        if "id" not in publish_res:
            print(f"❌ 릴스 발행 실패: {publish_res}")
            return None
            
        return publish_res.get("id")

    def upload_video_url(self, video_url, caption=""):
        """비디오 URL을 직접 인스타그램 릴스로 업로드합니다."""
        return self.upload_reels(video_url, caption)
