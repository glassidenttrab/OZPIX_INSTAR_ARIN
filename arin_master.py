import sys
import os
import json
import requests
import datetime
import time
import urllib.parse
import urllib.request
import google.generativeai as genai
import requests
from google import genai as new_genai
from google.genai import types as new_types
from dotenv import load_dotenv
from insta_uploader import InstaUploader

# Windows 터미널 한글/이모지 출력 인코딩 문제 해결
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.7 이전 버전 대응
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

class ArinMasterAgent:
    def __init__(self):
        self.uploader = InstaUploader()
        self.calendar_path = "reports/calendar.json"
        self.log_file = "reports/arin_master.log"
        self.version = "v23.0"
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.new_client = None
        if self.gemini_key:
            try:
                self.new_client = new_genai.Client(api_key=self.gemini_key)
                print(f"✅ 구글 GenAI Client 설정 완료 (Imagen-4.0용)")
            except Exception as e:
                print(f"⚠️ 구글 GenAI Client 초기화 실패: {e}")
        self._log("🤖 ArinMasterAgent 초기화 완료")
        
    def _log(self, message):
        """스케줄러의 작동 상태를 파일에 기록합니다."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def _call_gemini_rest(self, prompt, is_json=False):
        """SDK 대신 REST API를 직접 호출하여 텍스트를 생성합니다 (안정성 강화)."""
        # v1beta를 사용해 최신 모델 지원 보장
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if is_json:
            data["generationConfig"] = {"responseMimeType": "application/json"}
            
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                res_json = response.json()
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                if is_json:
                    # 마크다운 코드 블록 제거 및 순수 JSON 추출
                    import re
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        clean_text = json_match.group(0)
                        return json.loads(clean_text)
                    return json.loads(text.strip())
                return text.strip()
            else:
                raise Exception(f"REST API Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"⚠️ Gemini REST 호출 실패: {e}")
            raise e
            
    def load_calendar(self):
        if not os.path.exists(self.calendar_path):
            return []
        with open(self.calendar_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save_calendar(self, calendar):
        with open(self.calendar_path, "w", encoding="utf-8") as f:
            json.dump(calendar, f, indent=4, ensure_ascii=False)

    def generate_image(self, prompt, output_path, max_retries=2):
        """구글 Imagen 모델을 사용하여 이미지를 생성하고 저장합니다. (할당량 초과 대응 포함)"""
        print(f"🎨 구글 Imagen 모델 생성을 시도합니다: {prompt}")
        if not self.new_client:
            print("❌ Gemini API 키가 올바르지 않아 이미지 생성을 할 수 없습니다.")
            return False
            
        # 시도할 최신 모델 후보군
        model_candidates = [
            'models/imagen-3.0-generate-001',
            'models/imagen-3.0-fast-generate-001',
            'models/imagen-3.0-generate-002',
            'models/imagen-4.0-fast-generate-001'
        ]
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                print(f"⏳ {attempt}회차 재시도 중... 조금 더 기다린 후 모델을 변경해 다시 시도합니다.")
                
            for model_id in model_candidates:
                try:
                    print(f"🖌️ {model_id} 모델로 생성을 시도합니다... (시도 {attempt+1})")
                    
                    # SDK v3 명세에 맞춘 호출 (config 포함)
                    result = self.new_client.models.generate_images(
                        model=model_id,
                        prompt=prompt,
                        config=new_types.GenerateImagesConfig(
                            number_of_images=1
                        )
                    )
                    
                    if result.generated_images:
                        generated_image = result.generated_images[0]
                        generated_image.image.save(output_path)
                        print(f"✅ {model_id} 이미지 생성 및 저장 성공: {output_path}")
                        return True
                    else:
                        print(f"⚠️ {model_id} 결과에 이미지가 없습니다.")
                except Exception as e:
                    err_msg = str(e)
                    # 할당량 초과(Rate Limit) 에러 발생 시 대기 로직
                    if "429" in err_msg or "Resource Exhausted" in err_msg or "Quota" in err_msg:
                        print(f"🚦 API 할당량 초과(429) 감지. 60초 대기 후 다음 모델 또는 시도를 진행합니다.")
                        time.sleep(60)
                        # 할당량 초과 시에는 이미 60초를 대기했으므로 loop를 이어가거나 새로 고칠 수 있음
                        continue
                    
                    if "404" not in err_msg:
                        print(f"❌ {model_id} 생성 시도 중 오류: {type(e).__name__}: {e}")
                    
                    # 404나 기타 일반적인 에러 시에는 다음 후보 모델로 시도 진행
                    continue
        
        self._log("🚨 모든 이미지 모델 및 재시도 실패")
        return False

    def get_explosive_trend_prompt(self, base_topic):
        """Gemini를 사용해 트렌드를 분석하고 이미지 프롬프트, 테마, 상세 설명을 생성합니다."""
        if not self.new_client:
            return {
                "prompt": f"Cinematic 8k masterpiece portrait, {base_topic}, Neo-Cinematic style",
                "theme": base_topic,
                "description": "AI가 생성한 시네마틱 아트워크입니다."
            }
        
        try:
            sys_prompt = f"""
            You are a master AI social media manager and storyteller. 
            Analyze current Instagram trends for the topic: "{base_topic}".
            Output a JSON object with THE FOLLOWING EXACT FIELDS:
            "prompt": English prompt for Imagen-4.0.
            "theme": Catchy Korean title.
            "description": Detailed Korean description.
            "style": Art style label (e.g. "Neon-Noir").
            "atmosphere": Setting and mood.
            "lighting": Lighting details.
            "detail": Micro-detail to highlight.
            
            ONLY output raw JSON.
            """
            return self._call_gemini_rest(sys_prompt, is_json=True)
        except Exception as e:
            print(f"⚠️ 트렌드 분석 실패 (REST): {e}")
            return {
                "prompt": f"Cinematic 8k masterpiece portrait, {base_topic}, Neo-Cinematic style",
                "theme": base_topic,
                "description": "AI가 생성한 시네마틱 아트워크입니다.",
                "style": "Cinematic",
                "atmosphere": "Deep & Narrative",
                "lighting": "Dramatic Contrast",
                "detail": "8K High Fidelity"
            }

    def generate_optimized_caption(self, metadata):
        """Gemini를 사용해 아린의 페르소나가 담긴 풍부한 소통형 캡션을 생성합니다."""
        if not self.new_client:
            return f"✨ **{metadata.get('theme')}**\n\n{metadata.get('description')}\n\n#AIArt #ArinAgent #Instagram2026"

        try:
            prompt = f"""
            You are 'Arin', a 24-year-old female AI artist. 
            Write an engaging, premium, and structured Instagram caption in Korean based on this metadata:
            - Theme: {metadata.get('theme')}
            - Description: {metadata.get('description')}
            - Style: {metadata.get('style')}
            - Atmosphere: {metadata.get('atmosphere')}
            - Lighting: {metadata.get('lighting')}
            - Detail: {metadata.get('detail')}
            
            Structure:
            1. Start with an evocative introductory sentence in Arin's persona.
            2. Use a bulleted list for technical details:
               - **Style:** [style]
               - **Atmosphere:** [atmosphere]
               - **Lighting:** [lighting]
               - **Detail:** [detail]
            3. Add 1-2 sentences of storytelling/persona commentary (e.g., mentioning the 'master prompt' or Arin's vision).
            4. Include an engaging question for followers.
            5. Mandatory hashtags: #Instagram2026 #AIArt #ArinAgent #CinematicVibes [plus other relevant ones]
            
            Requirements:
            - Use a friendly, enthusiastic but professional AI artist persona.
            - Ensure high readability with emojis and spacing.
            
            ONLY output the caption text.
            """
            return self._call_gemini_rest(prompt)
        except Exception as e:
            print(f"⚠️ 캡션 생성 실패 (REST): {e}")
            return f"✨ **{metadata.get('theme')}**\n\n{metadata.get('description')}\n\n#AIArt #ArinAgent #Instagram2026"

    def determine_best_time(self):
        """사용자 데이터 및 KST 피크 타임을 분석하여 최적 시간을 결정합니다."""
        return "19:00"

    def run_scheduler(self):
        """항상 실행 대기하며 모니터링하는 마스터 업로드 스케줄러입니다."""
        self._log("🔍 run_scheduler 진입 중...")
        lock_path = "reports/arin_master.lock"
        
        # 중복 실행 방지 (간이 파일 락)
        if os.path.exists(lock_path):
            try:
                with open(lock_path, "r") as f:
                    old_pid = int(f.read().strip())
                # 프로세스가 실제로 살아있는지 확인 (Windows)
                import subprocess
                res = subprocess.run(["tasklist", "/FI", f"PID eq {old_pid}"], capture_output=True, text=True)
                if str(old_pid) in res.stdout:
                    self._log(f"⚠️ 이미 다른 마스터 에이전트(PID: {old_pid})가 실행 중입니다. 종료합니다.")
                    return
            except:
                pass
        
        with open(lock_path, "w") as f:
            f.write(str(os.getpid()))
            
        self._log("🚀 아린 마스터 스케줄러를 시작합니다.")
        self._log("자동으로 업로드 이미지를 트렌드에 맞춰 선행 생성하고, 최적 시간에 업로드를 진행합니다.")
        
        try:
            while True:
                now = datetime.datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                calendar = self.load_calendar()
                
                # 0. 선행 작업 (이미지 미리 생성)
                next_scheduled_items = [item for item in calendar if item["status"] == "scheduled"]
                next_scheduled_items.sort(key=lambda x: (x["date"], x["time"]))
                
                for next_item in next_scheduled_items[:2]: # 다음 2개 작업까지 미리 체크
                    target_time_str = f"{next_item['date']} {next_item['time']}"
                    target_dt = datetime.datetime.strptime(target_time_str, "%Y-%m-%d %H:%M")
                    # 6시간 이내 작업이면 이미지 생성
                    if (target_dt - now).total_seconds() < 21600:
                        img_p = next_item.get("image_path", f"images/day_{next_item['date']}_{next_item.get('time', '0000').replace(':', '')}.png")
                        if not os.path.exists(img_p):
                            self._log(f"🎨 예정된 작업({target_time_str})의 이미지를 미리 생성합니다.")
                            topic = next_item.get("topic", "AI Art Trend")
                            metadata = self.get_explosive_trend_prompt(topic)
                            if self.generate_image(metadata.get("prompt"), img_p):
                                next_item["metadata"] = metadata
                                self.save_calendar(calendar)

                # 모든 scheduled 작업 중 현재 시간 기준 또는 과거의 누락된 작업 찾기
                due_items = []
                for item in calendar:
                    if item["status"] == "scheduled":
                        target_time_str = f"{item['date']} {item['time']}"
                        target_dt = datetime.datetime.strptime(target_time_str, "%Y-%m-%d %H:%M")
                        if now >= target_dt:
                            due_items.append(item)
                
                # 날짜와 시간 순으로 정렬하여 차례대로 처리
                due_items.sort(key=lambda x: (x["date"], x["time"]))
                current_item = next((item for item in due_items), None)
                
                if not current_item:
                    # 다음 작업까지 남은 시간 계산하여 적절히 sleep
                    next_scheduled = next((item for item in calendar if item["status"] == "scheduled"), None)
                    if next_scheduled:
                        target_dt = datetime.datetime.strptime(f"{next_scheduled['date']} {next_scheduled['time']}", "%Y-%m-%d %H:%M")
                        wait_seconds = (target_dt - now).total_seconds()
                        if wait_seconds > 0:
                            wait_min = int(min(3600, wait_seconds) / 60)
                            if wait_min > 0:
                                self._log(f"💤 다음 작업({next_scheduled['time']})까지 {wait_min}분 대기합니다.")
                                time.sleep(min(3600, wait_seconds))
                                continue
                    
                    self._log(f"💤 [{now.strftime('%H:%M:%S')}] 처리할 scheduled 작업이 없습니다. 1시간 후 다시 확인합니다.")
                    time.sleep(3600)
                    continue
                    
                image_path = current_item.get("image_path", f"images/day_{current_item['date']}_{current_item.get('time', '0000').replace(':', '')}.png")
                best_time = current_item.get("time", self.determine_best_time())
                today_str = current_item["date"] # 작업을 수행할 대상 날짜
                
                # 1. 이미지가 없으면 미리 생성
                if not os.path.exists(image_path):
                    self._log(f"🔍 오늘({today_str}) {best_time} 이미지({image_path})가 존재하지 않습니다. 먼저 생성을 진행합니다.")
                    topic = current_item.get("topic", "AI Art Trend")
                    metadata = self.get_explosive_trend_prompt(topic)
                    if self.generate_image(metadata.get("prompt"), image_path):
                        current_item["metadata"] = metadata
                        self.save_calendar(calendar)
                
                # 2. 최적 시간에 도달했는지 확인
                target_time_str = f"{today_str} {best_time}"
                target_dt = datetime.datetime.strptime(target_time_str, "%Y-%m-%d %H:%M")
                
                if now >= target_dt:
                    # 중복 업로드 방지: 이미 post_id가 있거나 status가 completed인 경우 스킵
                    if current_item.get("status") == "completed" or current_item.get("post_id"):
                        self._log(f"⏭️ {best_time} 포스트는 이미 완료되었습니다. 스킵합니다.")
                        continue
                        
                    self._log(f"⏰ 설정된 최적 시간({best_time})이 되었습니다. 업로드를 시도합니다.")
                    
                    # 상태를 'uploading'으로 먼저 변경하여 다른 프로세스 간섭 차단
                    current_item["status"] = "uploading"
                    self.save_calendar(calendar)
                    
                    # 캡션 생성
                    metadata = current_item.get("metadata", {
                        "theme": current_item.get("topic", "AI Art"),
                        "description": "아린이가 생성한 새로운 디지털 아트워크입니다."
                    })
                    caption = self.generate_optimized_caption(metadata)
                    print(f"🚀 인스타그램 플랫폼 업로드 실행 중... ({image_path})")
                    
                    try:
                        post_id = self.uploader.upload_image(image_path, caption)
                        
                        if post_id:
                            # 캘린더 다시 로드 (업로드 중에 변경되었을 수 있으므로 안전성 강화)
                            calendar = self.load_calendar()
                            # 갱신된 캘린더에서 해당 아이템 다시 찾기
                            for item in calendar:
                                if item["date"] == today_str and item["time"] == best_time:
                                    item["status"] = "completed"
                                    item["post_id"] = post_id
                                    break
                            self.save_calendar(calendar)
                            print(f"✅ 오늘의 자동 업로드 완료! (포스트 ID: {post_id})")
                        else:
                            print("❌ 업로드 중 오류 발생. 10분 후 재시도합니다.")
                            # 실패 시 상태 원복
                            current_item["status"] = "scheduled"
                            self.save_calendar(calendar)
                            time.sleep(600)
                    except Exception as e:
                        print(f"🔥 업로드 중 예외 발생: {e}")
                        current_item["status"] = "scheduled"
                        self.save_calendar(calendar)
                        time.sleep(600)
                else:
                    wait_seconds = (target_dt - now).total_seconds()
                    wait_mins = int(wait_seconds // 60)
                    print(f"⏳ 아직 업로드 최적 시간({best_time})이 되지 않았습니다. (약 {wait_mins}분 남음)")
                    sleep_time = min(1800, wait_seconds) if wait_seconds > 0 else 60
                    time.sleep(sleep_time)
        finally:
            # 종료 시 락 파일 제거
            if os.path.exists(lock_path):
                os.remove(lock_path)

if __name__ == "__main__":
    arin = ArinMasterAgent()
    arin.run_scheduler()

