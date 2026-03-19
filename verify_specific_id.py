import os
from dotenv import load_dotenv
import requests

def verify_business_id():
    load_dotenv()
    target_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    
    version = "v23.0"
    
    # 해당 ID가 유효한지 직접 조회해봅니다.
    url = f"https://graph.instagram.com/{version}/{target_id}?fields=id,username,name&access_token={token}"
    
    print(f"🔍 사용자 지입 ID({target_id}) 검증 중...")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ ID 유효성 확인 성공!")
            print(f"📝 계정 정보: {data}")
            return True
        else:
            print(f"❌ 해당 ID를 찾을 수 없습니다. (상태 코드: {response.status_code})")
            print(f"📝 오류 내용: {data}")
            
            # /me/accounts 등 대체 경로도 확인해봅니다.
            print("\n🔄 연결된 계정 목록을 다시 확인합니다...")
            me_url = f"https://graph.instagram.com/{version}/me?fields=id,username&access_token={token}"
            me_res = requests.get(me_url).json()
            print(f"👤 현재 토큰의 사용자(/me): {me_res}")
            
            return False
            
    except Exception as e:
        print(f"💥 오류 발생: {e}")
        return False

if __name__ == "__main__":
    verify_business_id()
