import json
import os
from datetime import datetime, timedelta

def initialize_calendar():
    calendar_path = "reports/calendar.json"
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    start_date = datetime.now()
    calendar = []
    
    # 30일치 기본 계획 수립 (일 3회 업로드)
    times = ["10:00", "16:00", "22:00"]
    for i in range(30):
        target_date = start_date + timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        
        for upload_time in times:
            time_suffix = upload_time.replace(":", "")
            calendar.append({
                "date": date_str,
                "time": upload_time,
                "status": "scheduled",
                "topic": f"Day {i+1} AI Trend Content ({upload_time})",
                "report_file": f"reports/day_{date_str}_{time_suffix}_plan.md",
                "image_path": f"images/day_{date_str}_{time_suffix}.png"
            })
        
    with open(calendar_path, "w", encoding="utf-8") as f:
        json.dump(calendar, f, indent=4, ensure_ascii=False)
    
    print(f"📅 30일 달력 생성 완료: {calendar_path}")

if __name__ == "__main__":
    initialize_calendar()
