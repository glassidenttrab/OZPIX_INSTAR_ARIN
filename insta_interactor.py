import os
import json
import time
import random
import datetime
import google.generativeai as genai
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

class InstaInteractor:
    def __init__(self):
        self.cl = Client()
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.session_file = "reports/session.json"
        self.log_file = "reports/interaction_log.json"
        
        # Gemini AI 설정
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            try:
                # 사용 가능한 모델 목록에서 'gemini'와 'flash'가 포함된 모델을 동적으로 선택
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                selected_model = next((m for m in available_models if "gemini" in m.lower() and "flash" in m.lower()), None)
                if not selected_model:
                    selected_model = next((m for m in available_models if "gemini" in m.lower()), None)
                
                if selected_model:
                    self.model = genai.GenerativeModel(selected_model)
                    print(f"✅ Gemini 모델 설정 완료: {selected_model}")
                else:
                    print("⚠️ 적절한 Gemini 모델을 찾을 수 없습니다.")
            except Exception as e:
                print(f"⚠️ Gemini 모델 초기화 실패: {e}")

        if not self.username or not self.password:
            print("⚠️ INSTAGRAM_USERNAME 또는 INSTAGRAM_PASSWORD가 .env에 설정되지 않았습니다.")
            
    def login(self):
        """세션 파일을 사용하여 로그인하거나 새로 로그인합니다."""
        try:
            if os.path.exists(self.session_file):
                self.cl.load_settings(self.session_file)
                self.cl.login(self.username, self.password)
                print(f"✅ 기존 세션으로 로그인 성공: {self.username}")
            else:
                self.cl.login(self.username, self.password)
                self.cl.dump_settings(self.session_file)
                print(f"✅ 새 세션으로 로그인 성공: {self.username}")
        except Exception as e:
            print(f"❌ 로그인 실패: {e}")
            return False
        return True

    def get_daily_count(self):
        """오늘 수행한 상호작용 횟수를 가져옵니다."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(self.log_file):
            return 0
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
                return logs.get(today, {}).get("count", 0)
            except:
                return 0

    def update_log(self, **kwargs):
        """상호작용 횟수를 업데이트합니다."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        logs = {}
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except:
                    pass
        
        day_data = logs.get(today, {"count": 0, "history": [], "friends": []})
        day_data["count"] += 1
        day_data["history"].append(datetime.datetime.now().strftime("%H:%M:%S"))
        
        # 친구 정보가 전달되었을 경우 추가
        if kwargs.get("friend_info"):
            day_data["friends"].append(kwargs["friend_info"])
            self.generate_friends_report(today, day_data["friends"])

        logs[today] = day_data
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)

    def generate_friends_report(self, date_str, friends):
        """오늘 만난 친구들을 Markdown 리포트로 생성합니다."""
        report_path = f"reports/friends_{date_str}.md"
        content = f"# 🤝 오늘의 친구 리스트 ({date_str})\n\n"
        content += f"아린이가 오늘 소통을 나눈 소중한 분들입니다. (총 {len(friends)}명)\n\n"
        content += "| 프로필 | 이름(닉네임) | 소통 시간 | 프로필 / 게시물 |\n"
        content += "| :--- | :--- | :--- | :--- |\n"
        
        for friend in friends:
            username = friend.get("username")
            full_name = friend.get("full_name", "")
            time_str = friend.get("time")
            nationality = friend.get("nationality", "미분석")
            comment = friend.get("comment", "정보 없음")
            post_code = friend.get("post_code", "")
            
            profile_link = f"[프로필](https://www.instagram.com/{username}/)"
            post_link = f"[게시물 확인](https://www.instagram.com/p/{post_code}/)" if post_code else "링크 없음"
            
            content += f"| @{username} | {full_name} | {time_str} | {profile_link} / {post_link} |\n"
            content += f"| **예상 국적** | {nationality} | | |\n"
            content += f"| **작성 댓글** | {comment} | | |\n"
            content += "| --- | --- | --- | --- |\n"
            
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

    def analyze_user_and_generate_comment(self, user_info, hashtag, post_caption=""):
        """Gemini를 사용하여 사용자의 국적을 추측하고 포스트 맥락에 맞는 인간적인 댓글을 생성합니다."""
        if not self.model:
            return "Global", "정말 멋진 작품이네요! 😍"

        prompt = f"""
        You are 'Arin', a 24-year-old female AI artist who loves digital art, cinematic aesthetics, and connecting with other creators on Instagram.
        Your goal is to leave a natural, human-like comment on a post to build a genuine connection. 
        
        **Instructions:**
        1. Analyze the user's Bio and the Post's Caption.
        2. Estimate their likely primary language/nationality.
        3. Write a natural comment in that language (or English if uncertain).
        4. **CRITICAL:** Avoid generic praises like "Amazing art" or "Great work". Instead, be specific about the post's content, ask a friendly question, or mention a detail. Use emojis sparsely and naturally.
        5. Tone: Enthusiastic, friendly, artist-to-artist connection.
        
        **Target Content Info:**
        - Hashtag: #{hashtag}
        - Post Caption: {post_caption}
        
        **User Info:**
        - Username: {user_info.username}
        - Full Name: {user_info.full_name}
        - Bio: {user_info.biography}
        
        Output format (Strict JSON):
        {{
            "nationality": "Estimated country or Global",
            "language": "Estimated primary language",
            "comment": "The natural, specific 1-sentence comment in their language"
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(raw_text)
            return data.get("nationality", "Global"), data.get("comment", "Amazing work! 😍")
        except Exception as e:
            print(f"⚠️ AI 분석 중 오류 발생: {e}")
            return "Unknown", "Wow, amazing art! ✨"

    def interact_with_hashtag(self, hashtag="AIArt"):
        """해시태그를 검색하여 랜덤한 포스트에 좋아요와 댓글을 답니다."""
        try:
            print(f"🔍 #{hashtag} 검색 중...")
            medias = self.cl.hashtag_medias_recent(hashtag, amount=10)
            if not medias:
                print("❌ 검색 결과가 없습니다.")
                return False
            
            target = random.choice(medias)
            
            # 상세 유저 정보 가져오기 (Bio 포함)
            print(f"👤 사용자 정보 분석 중: @{target.user.username}")
            full_user_info = self.cl.user_info(target.user.pk)
            
            # AI 분석 및 댓글 생성 (게시물 캡션 추가)
            nationality, comment_text = self.analyze_user_and_generate_comment(full_user_info, hashtag, target.caption_text)
            print(f"🌍 예상 국적: {nationality}")
            print(f"💬 생성된 댓글: {comment_text}")

            # 좋아요
            print(f"❤️ 좋아요 시도: {target.pk}")
            self.cl.media_like(target.id)
            
            # 댓글
            self.cl.media_comment(target.id, comment_text)
            
            # 팔로우 (친구 추가)
            print(f"✅ 팔로우 시도: @{full_user_info.username}")
            self.cl.user_follow(full_user_info.pk)
            
            # 친구 정보 구성
            friend_info = {
                "username": full_user_info.username,
                "full_name": full_user_info.full_name,
                "pk": full_user_info.pk,
                "nationality": nationality,
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "comment": comment_text,
                "post_code": target.code  # 게시물 고유 코드 저장
            }
            
            self.update_log(friend_info=friend_info)
            return True
        except Exception as e:
            print(f"❌ 상호작용 중 오류 발생: {e}")
            return False

if __name__ == "__main__":
    # 테스트 실행
    interactor = InstaInteractor()
    if interactor.login():
        interactor.interact_with_hashtag()
