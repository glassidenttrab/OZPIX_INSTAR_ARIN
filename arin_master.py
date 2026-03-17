import os
import json
import requests
import datetime
from insta_uploader import InstaUploader

class ArinMasterAgent:
    def __init__(self):
        self.uploader = InstaUploader()
        self.calendar_path = "reports/calendar.json"
        
    def load_calendar(self):
        with open(self.calendar_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save_calendar(self, calendar):
        with open(self.calendar_path, "w", encoding="utf-8") as f:
            json.dump(calendar, f, indent=4, ensure_ascii=False)

    def generate_daily_report(self, date_str, trend, strategy, caption, hashtags):
        report_content = f"""# 📝 Daily Arin Report - {date_str}

## 🔍 오늘의 트렌드 분석
{trend}

## 💡 알고리즘 해킹 전략
{strategy}

## ✍️ 인스타그램 포스팅 문구
{caption}

## #️⃣ 해시태그
{hashtags}

---
*아린 에이전트가 자동 분석 및 생성한 리포트입니다.*
"""
        report_file = f"reports/day_{date_str}_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        return report_file

    def run_daily_task(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        calendar = self.load_calendar()
        
        for item in calendar:
            if item["date"] == today and item["status"] == "scheduled":
                print(f"🚀 {today} 작업을 시작합니다!")
                
                # 실제 이미지 생성은 Agent(나)가 수행해야 하므로 
                # 여기서는 이미 완성된 이미지가 images 폴더에 있다고 가정하거나
                # Agent가 수동으로 생성한 파일을 업로드합니다.
                
                image_file = f"images/day_{today}.png"
                if not os.path.exists(image_file):
                    # 만약 이미지가 없으면 가장 최근 생성된 이미지를 사용하거나 에러 출력
                    print(f"⚠️ {image_file} 파일이 없습니다. 대장님께 이미지 생성을 요청하세요!")
                    return
                
                # 캡션 예시 (실제로는 일일 분석 결과로 대체)
                caption = "오늘의 트렌드 포스팅입니다! #AI #Trend"
                
                # 업로드 실행
                post_id = self.uploader.upload_image(image_file, caption)
                
                if post_id:
                    item["status"] = "completed"
                    item["post_id"] = post_id
                    self.save_calendar(calendar)
                    print(f"✅ {today} 업로드 완료!")
                break

if __name__ == "__main__":
    # 이 스크립트는 매일 특정 시간에 실행되도록 스케줄러(Windows Task Scheduler 등)에 등록할 수 있습니다.
    # arin = ArinMasterAgent()
    # arin.run_daily_task()
    pass
