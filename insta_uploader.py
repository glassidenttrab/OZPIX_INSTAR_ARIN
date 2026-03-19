import os
import time
import requests
from dotenv import load_dotenv

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
        
    def _make_public_url(self, local_path):
        """로컬 파일을 인스타그램 서버가 접근할 수 있도록 일시적으로 공용 URL로 변환합니다."""
        print(f"🌐 로컬 파일을 공용 URL로 변환 중: {os.path.basename(local_path)}")
        try:
            with open(local_path, 'rb') as f:
                files = {'fileToUpload': f}
                data = {'reqtype': 'fileupload'}
                # Catbox.moe 서비스를 이용한 일시적 호스팅
                response = requests.post('https://catbox.moe/user/api.php', data=data, files=files)
                if response.status_code == 200:
                    public_url = response.text.strip()
                    print(f"✅ 변환 완료: {public_url}")
                    return public_url
                else:
                    print(f"❌ URL 변환 실패 (상태 코드: {response.status_code})")
                    return None
        except Exception as e:
            print(f"❌ URL 변환 중 오류 발생: {e}")
            return None

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
            return None
            
        creation_id = res.get("id")
        print(f"⏳ 서버 처리 대기... (컨테이너 ID: {creation_id})")
        
        # 인스타그램 서버 처리를 위해 대기
        time.sleep(30) 

        # 2. 최종 발행
        publish_res = requests.post(f"https://graph.instagram.com/{self.version}/{target_id}/media_publish", data={
            "creation_id": creation_id,
            "access_token": self.token
        }).json()
        
        if "id" not in publish_res:
            print(f"❌ 최종 발행 실패: {publish_res}")
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
