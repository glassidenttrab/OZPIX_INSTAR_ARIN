import os
import json
import requests
import datetime
import time
from insta_uploader import InstaUploader

class ArinMasterAgent:
    def __init__(self):
        self.uploader = InstaUploader()
        self.calendar_path = "reports/calendar.json"
        self.version = "v23.0"
        
    def load_calendar(self):
        if not os.path.exists(self.calendar_path):
            return []
        with open(self.calendar_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save_calendar(self, calendar):
        with open(self.calendar_path, "w", encoding="utf-8") as f:
            json.dump(calendar, f, indent=4, ensure_ascii=False)

    def analyze_trending_strategy(self, day):
        """2026년 알고리즘 트렌드 기반의 전략을 수립합니다."""
        strategies = [
            "Share-Cento: DM 공유를 유도하는 공감 기반 시네마틱 아트",
            "Save-Stack: 기술적 튜토리얼 질감을 담은 정보성 인포그래픽",
            "Human-Connect: 인간적인 감수성과 AI의 정교함이 결합된 포트레이트",
            "Algorithm-Hacker: 스크롤을 멈추게 하는 강렬한 시각적 대비",
            "Emotional-Depth: 깊은 서사를 담은 정적인 분위기"
        ]
        return strategies[day % len(strategies)]

    def get_master_prompt(self, goal, strategy):
        """마스터 프롬프트 구조에 따른 정교한 프롬프트를 구성합니다."""
        # 이 메서드는 실제 생성 시 Agent(나)가 참조하는 가이드라인 역할을 합니다.
        template = {
            "image_request": {
                "goal": goal,
                "meta": {
                    "image_type": "Cinematic",
                    "quality": "8k Masterpiece",
                    "style_mode": "Neo-Cinematic",
                    "aspect_ratio": "4:5"
                },
                "creative_style": f"Combined with {strategy}",
                "mood_vibe": "Atmospheric, Professional, Premium",
                "style_keywords": ["analog grain", "hyperreal skin", "cinematic depth"]
            }
        }
        return json.dumps(template, indent=4, ensure_ascii=False)

    def generate_optimized_caption(self, topic, strategy):
        """알고리즘 해킹(공유/저장 유도)이 포함된 캡션을 생성합니다."""
        return f"""✨ **오늘의 아린 인사이트: {topic}**

{strategy} 전략이 적용된 오늘의 콘텐츠입니다.

2026년 알고리즘 핵심 요약:
✅ 단순 좋아요보다 '공유(DM)'가 도달율을 결정합니다.
✅ '저장'은 당신의 전문성을 증명하는 지표입니다.

이 정보가 도움이 되셨다면 친구에게 공유하거나, 나중에 다시 보기 위해 저장해두세요! 🚀

#AI #ArinAgent #InstagramGrowth #AlgorithmHacking #DigitalTrend"""

    def determine_best_time(self):
        """사용자 데이터 및 KST 피크 타임을 분석하여 최적 시간을 결정합니다."""
        # 현재는 19:00(저녁 시간대)를 최적 타임으로 고정 분석
        return "19:00"

    def process_daily(self):
        """일일 전체 프로세스를 자동 실행합니다."""
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        calendar = self.load_calendar()
        
        for item in calendar:
            if item["date"] == today_str and item["status"] == "scheduled":
                print(f"📅 [{today_str}] 작업을 시작합니다.")
                
                # 1. 전략 분석
                strategy = self.analyze_trending_strategy(now.day)
                item["strategy"] = strategy
                
                # 2. 업로드 시간 결정
                best_time = self.determine_best_time()
                item["time"] = best_time
                print(f"⏰ 최적 업로드 시간 분석 완료: {best_time}")

                # 3. 이미지 생성 프롬프트 구성
                prompt_structure = self.get_master_prompt(item["topic"], strategy)
                print(f"🎨 이미지 생성 프롬프트 준비 완료.")
                
                # ⚠️ 주의: 실제 이미지 생성(generate_image)은 Agent 도구를 통해서만 가능하므로, 
                # 이 스크립트는 프롬프트를 확정한 후 이미지 생성을 대기하는 구조로 설계됩니다.
                
                image_path = f"images/day_{today_str}.png"
                if not os.path.exists(image_path):
                    print(f"⚠️ 이미지가 아직 생성되지 않았습니다. {image_path}를 생성해 주세요!")
                    return
                
                # 4. 캡션 생성
                caption = self.generate_optimized_caption(item["topic"], strategy)
                
                # 5. 최종 업로드
                print(f"🚀 인스타그램 업로드 시도 중...")
                post_id = self.uploader.upload_image(image_path, caption)
                
                if post_id:
                    item["status"] = "completed"
                    item["post_id"] = post_id
                    self.save_calendar(calendar)
                    print(f"✅ 오늘의 업로드 완료! (ID: {post_id})")
                break

if __name__ == "__main__":
    arin = ArinMasterAgent()
    arin.process_daily() # 자동화 실행 명령
