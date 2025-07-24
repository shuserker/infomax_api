import requests
from requests.auth import HTTPBasicAuth
import json

def save_json_data():
    URL = "https://dev-global-api.einfomax.co.kr/apis/posco/news"
    USER = "infomax"
    PWD = "infomax!"
    
    try:
        resp = requests.get(URL, auth=HTTPBasicAuth(USER, PWD), timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        # JSON 파일로 저장
        with open('posco_news_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ JSON 데이터가 저장되었습니다: posco_news_data.json")
        print("📂 Kiro에서 파일을 열어 JSON 뷰어로 확인하세요!")
        
        # 간단한 요약도 출력
        print(f"\n📊 뉴스 요약:")
        for news_type, news_data in data.items():
            print(f"  • {news_type}: {news_data['title'][:50]}...")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    save_json_data()