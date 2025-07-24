import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

def generate_html_report():
    URL = "https://dev-global-api.einfomax.co.kr/apis/posco/news"
    USER = "infomax"
    PWD = "infomax!"
    
    try:
        resp = requests.get(URL, auth=HTTPBasicAuth(USER, PWD), timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        # HTML 생성
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POSCO 뉴스 리포트</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .news-item {{
            margin-bottom: 40px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        .news-header {{
            background: linear-gradient(135deg, #0066cc, #004499);
            color: white;
            padding: 15px 20px;
        }}
        .news-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .news-meta {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .news-content {{
            padding: 20px;
            white-space: pre-line;
            line-height: 1.8;
        }}
        .json-section {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 20px;
            margin-top: 30px;
        }}
        .json-content {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .category-tag {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 POSCO 뉴스 리포트</h1>
            <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
        
        # 각 뉴스 항목 처리
        for news_type, news_data in data.items():
            categories = ''.join([f'<span class="category-tag">{cat}</span>' for cat in news_data['category']])
            
            html_content += f"""
        <div class="news-item">
            <div class="news-header">
                <div class="news-title">{news_data['title']}</div>
                <div class="news-meta">
                    📅 {news_data['date']} {news_data['time']} | 
                    ✍️ {', '.join(news_data['writer'])} | 
                    {categories}
                </div>
            </div>
            <div class="news-content">{news_data['content']}</div>
        </div>
"""
        
        # JSON 원본 데이터 섹션
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        html_content += f"""
        <div class="json-section">
            <h3>🔧 원본 JSON 데이터</h3>
            <div class="json-content">{json_str}</div>
        </div>
    </div>
</body>
</html>
"""
        
        # HTML 파일 저장
        with open('posco_news_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML 리포트가 생성되었습니다: posco_news_report.html")
        print("📂 파일을 브라우저에서 열어보세요!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    generate_html_report()