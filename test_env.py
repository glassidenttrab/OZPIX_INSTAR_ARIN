import os
from dotenv import load_dotenv
import requests

def test_connection():
    load_dotenv()
    acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    
    print(f"🔍 계정 ID: {acc_id}")
    print(f"🔍 토큰 확인 (앞 10자리): {token[:10]}...")
    
    version = "v23.0"
    url = f"https://graph.instagram.com/{version}/me?fields=id,username&access_token={token}"
    
    print(f"🌐 API 요청 중: {url.replace(token, 'TOKEN_HIDDEN')}")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ 연결 성공!")
            print(f"👤 사용자 정보: {data}")
            
            # 실제 계정 ID와 설정된 ID 비교
            if str(data.get('id')) == str(acc_id):
                print("✨ 계정 ID가 일치합니다.")
            else:
                print(f"⚠️ 경고: 설정된 ID({acc_id})와 실제 API 응답 ID({data.get('id')})가 다릅니다.")
        else:
            print(f"❌ 연결 실패 (상태 코드: {response.status_code})")
            print(f"📝 응답 내용: {data}")
            
    except Exception as e:
        print(f"💥 오류 발생: {e}")

if __name__ == "__main__":
    test_connection()
