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
        self.cl.request_timeout = 30
        self.cl.delay_range = [2, 5]
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.log_file = "reports/interactor.log"
        self.stats_file = "reports/daily_stats.json"
        self.session_file = "reports/session.json"
        self._ensure_log_dir()

        # Gemini AI 설정
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
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

    def _ensure_log_dir(self):
        if not os.path.exists("reports"):
            os.makedirs("reports")

    def _log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def login(self):
        """세션 파일을 사용하여 로그인하거나 새로 로그인합니다. login_required 방지 로직 탑재"""
        try:
            if os.path.exists(self.session_file):
                self.cl.load_settings(self.session_file)
                try:
                    self.cl.get_timeline_feed()
                    print(f"✅ 기존 세션으로 로그인 유효성 확인 완료: {self.username if self.username else 'Unknown'}")
                    return True
                except Exception as eval_e:
                    print(f"⚠️ 기존 세션 유효하지 않음({eval_e}). 재로그인 시도...")
                    if not self.username or not self.password:
                        self._log("❌ INSTAGRAM_USERNAME 또는 INSTAGRAM_PASSWORD가 .env에 설정되지 않아 재로그인할 수 없습니다.")
                        return False
                    self.cl.login(self.username, self.password)
                    self.cl.dump_settings(self.session_file)
                    print(f"✅ 새 세션으로 로그인 성공: {self.username}")
                    return True
            else:
                if not self.username or not self.password:
                    self._log("❌ INSTAGRAM_USERNAME 또는 INSTAGRAM_PASSWORD가 .env에 설정되지 않았습니다.")
                    return False
                self.cl.login(self.username, self.password)
                self.cl.dump_settings(self.session_file)
                print(f"✅ 첫 로그인 성공: {self.username}")
                return True
        except Exception as e:
            if "login_required" in str(e).lower() or "challenge" in str(e).lower() or "feedback_required" in str(e).lower():
                print(f"🚨 치명적 봇 탐지 오류 발생: {e}")
                return "CRITICAL_BAN"
            print(f"❌ 로그인 실패: {e}")
            return False

    def get_daily_count(self):
        """오늘 수행한 상호작용 횟수를 가져옵니다."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(self.stats_file):
            return 0
        
        with open(self.stats_file, "r", encoding="utf-8") as f:
            try:
                stats = json.load(f)
                return stats.get(today, {}).get("count", 0)
            except Exception as e:
                print(f"⚠️ 통계 파일 읽기 실패: {e}")
                return 0

    def update_log(self, **kwargs):
        """상호작용 횟수를 업데이트합니다."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        stats = {}
        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r", encoding="utf-8") as f:
                try:
                    stats = json.load(f)
                except:
                    pass
        
        day_data = stats.get(today, {"count": 0, "history": [], "friends": []})
        day_data["count"] += 1
        day_data["history"].append(datetime.datetime.now().strftime("%H:%M:%S"))
        
        # 친구 정보가 전달되었을 경우 추가
        if kwargs.get("friend_info"):
            day_data["friends"].append(kwargs["friend_info"])
            self.generate_friends_report(today, day_data["friends"])

        stats[today] = day_data
        
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

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

            # 1. 대상 피드 스크롤 및 읽기 시뮬레이션 (30~60초)
            print("⏳ 대상 피드 스크롤 시뮬레이션 중 (30~60초 대기)...")
            time.sleep(random.uniform(30, 60))

            # 좋아요
            print(f"❤️ 좋아요 시도: {target.pk}")
            self.cl.media_like(target.id)
            
            # 2. 고스트 타이핑 대기 (타자 치는 시간 시뮬레이션: 댓글 길이 / 2.5 타수 기준 + 랜덤 알파)
            typing_time = (len(comment_text) / 2.5) + random.uniform(5, 15)
            print(f"⏳ 댓글 입력 타이핑 시뮬레이션 중... 예상 소요 시간: {int(typing_time)}초")
            time.sleep(typing_time)
            
            # 댓글
            print(f"💬 댓글 작성 시도: {target.pk}")
            self.cl.media_comment(target.id, comment_text)
            
            # 팔로우 (친구 추가) - 의심 방지를 위해 주석 처리
            # print(f"✅ 팔로우 시도: @{full_user_info.username}")
            # self.cl.user_follow(full_user_info.pk)
            
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
            if "login_required" in str(e).lower() or "challenge" in str(e).lower() or "feedback_required" in str(e).lower():
                print(f"🚨 상호작용 중 치명적 봇 탐지 오류: {e}")
                return "CRITICAL_BAN"
            print(f"❌ 상호작용 중 오류 발생: {e}")
            return False

if __name__ == "__main__":
    # 테스트 실행
    interactor = InstaInteractor()
    if interactor.login():
        interactor.interact_with_hashtag()
