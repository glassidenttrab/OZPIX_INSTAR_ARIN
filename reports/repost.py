import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def post_to_insta():
    acc_id = "26673183542267603"
    token = "IGAAUveZA43SlNBZAGJkZAUVVSy1zUnJMYXkwSGNFVDJKc2xPODZAqdEhsN1BHNzh2c2pBYVRUY29weHhac01rME9MUTBGMUlfRlFEaEtpZAENaVEw4Vnh5SHFlVVN4WWJCZAmkwY1ppZAERDLXJoejZA6bXpRWjhZAQzZAhTUhrbmlKM1BYSQZDZD"
    
    # 1. Container
    url = f"https://graph.instagram.com/v23.0/{acc_id}/media"
    caption = """🎨 [AI 이미지 생성 꿀팁] 당신도 아티스트가 될 수 있습니다!

인공지능으로 멋진 이미지를 만드는 핵심은 바로 '프롬프트(Prompt)'입니다. 
복잡하게 생각하지 마세요! 아래 3단계 공식만 기억하세요:

1️⃣ 주제 (Subject): 무엇을 그릴 것인가?
2️⃣ 스타일 (Style): 어떤 느낌인가?
3️⃣ 디테일 (Detail): 세부 묘사는?

⭐ 오늘 사용된 프롬프트:
"A futuristic workspace where a high-tech computer screen shows a digital painting created by glowing neural networks, vibrant colors, neon accents."

이제 여러분만의 창의력을 AI와 함께 펼쳐보세요! ✨

#AI아트 #인공지능그림 #프롬프트입문 #디지털아트 #AI학습 #아린에이전트 #인공지능에이전트 #AIArtist #FutureTech"""

    # We use a high quality Unsplash URL for the demo as requested
    img_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1964&auto=format&fit=crop"

    res = requests.post(url, data={
        "image_url": img_url,
        "caption": caption,
        "access_token": token
    }).json()
    
    print(f"Container Response: {res}")
    
    if "id" in res:
        creation_id = res["id"]
        print(f"Waiting for processing (ID: {creation_id})...")
        time.sleep(10)
        
        # 2. Publish
        pub_url = f"https://graph.instagram.com/v23.0/{acc_id}/media_publish"
        pub_res = requests.post(pub_url, data={
            "creation_id": creation_id,
            "access_token": token
        }).json()
        print(f"Publish Response: {pub_res}")

if __name__ == "__main__":
    post_to_insta()
