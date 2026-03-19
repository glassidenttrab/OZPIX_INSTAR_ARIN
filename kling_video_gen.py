import os
import sys
import time
import jwt
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def encode_jwt_token(ak, sk):
    """Kling AI 인증을 위한 JWT 토큰 생성"""
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 3600, # 1시간 유효
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, sk, algorithm="HS256", headers=headers)
    return token

import base64

def get_image_base64(image_path):
    """로컬 이미지를 Base64 문자열로 변환"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_image(image_path):
    """이미지를 Kling AI 서버에 업로드하고 URL을 획득합니다."""
    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    token = encode_jwt_token(ak, sk)
    
    url = "https://api-singapore.klingai.com/v1/images/upload"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, headers=headers, files=files)
        
    try:
        res_data = response.json()
        if "data" in res_data and "url" in res_data["data"]:
            return res_data["data"]["url"]
        else:
            print(f"❌ 이미지 업로드 실패: {res_data}")
            return None
    except:
        print(f"DEBUG - Upload Response Text: {response.text}")
        return None

def create_video_task(image_path, prompt):
    """Kling AI 비디오 생성 작업 요청 (Image-to-Video, v2.6 규격)"""
    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    token = encode_jwt_token(ak, sk)
    
    # 1. 이미지 먼저 업로드하여 URL 획득
    print(f"📤 이미지 업로드 중: {image_path}")
    image_url = upload_image(image_path)
    if not image_url:
        return {"error": "Upload failed"}
    
    print(f"🔗 이미지 URL 획득: {image_url}")
    
    # 2. 비디오 생성 요청
    url = "https://api-singapore.klingai.com/v1/videos/image2video"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "model_name": "kling-v2-6",
        "image": image_url, # 업로드된 URL 사용
        "prompt": prompt,
        "negative_prompt": "",
        "duration": "5",
        "mode": "pro",
        "sound": "off",
        "callback_url": "",
        "external_task_id": ""
    }
    
    response = requests.post(url, headers=headers, json=data)
    try:
        return response.json()
    except:
        print(f"DEBUG - Response Text: {response.text}")
        return {"error": "JSON Decode Error", "text": response.text}

def get_task_status(task_id):
    """작업 상태 조회 (싱가포르 리전)"""
    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    token = encode_jwt_token(ak, sk)
    
    url = f"https://api-singapore.klingai.com/v1/videos/image2video/{task_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python kling_video_gen.py <이미지경로> [프롬프트]")
    else:
        img_p = sys.argv[1]
        prmpt = sys.argv[2] if len(sys.argv) > 2 else "Subtle breathing, wind blowing hair"
        
        print(f"🎬 Kling AI 비디오 생성 요청 프로세스 시작: {img_p}")
        result = create_video_task(img_p, prmpt)
        
        if "data" in result and "task_id" in result["data"]:
            task_id = result["data"]["task_id"]
            print(f"✅ 작업 생성 성공! Task ID: {task_id}")
            print("⏳ 생성 대기 중 (인공지능 소요 시간 약 1~5분)...")
            
            start_time = time.time()
            timeout = 600 # 10분 타임아웃
            
            while True:
                if time.time() - start_time > timeout:
                    print("⌛ 타임아웃: 비디오 생성 시간이 너무 오래 걸립니다.")
                    break
                    
                status_res = get_task_status(task_id)
                data = status_res.get("data", {})
                task_status = data.get("task_status")
                
                if task_status == "succeed":
                    video_resource = data.get("video_resource", {})
                    video_url = video_resource.get("url")
                    print(f"🎉 생성 완료! 비디오 URL: {video_url}")
                    break
                elif task_status == "failed":
                    print(f"❌ 생성 실패: {data.get('task_status_msg')}")
                    break
                else:
                    # 진행률이 있는 경우 출력 (API 버전에 따라 다를 수 있음)
                    progress = data.get("task_progress", "unknown")
                    print(f"🔄 처리 중... (상태: {task_status}, 진행률: {progress})")
                    time.sleep(10) # 20초에서 10초로 단축
        else:
            print(f"❌ 작업 생성 실패: {result}")
