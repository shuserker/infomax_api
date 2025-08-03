#!/usr/bin/env python3
"""
간단한 테스트 리포트 생성기
테마 시스템 테스트를 위한 기본 HTML 리포트를 생성합니다.
"""

import os
import json
import random
from datetime import datetime, timedelta

class SimpleTestGenerator:
    def __init__(self):
        self.report_types = {
            'exchange-rate': {
                'title': 'POSCO 서환마감 분석 리포트',
                'color': '#0066cc',
                'icon': 'fas fa-dollar-sign'
            },
            'kospi-close': {
                'title': 'POSCO 증시마감 분석 리포트', 
                'color': '#28a745',
                'icon': 'fas fa-chart-line'
            },
            'newyork-market-watch': {
                'title': 'POSCO 뉴욕마켓워치 분석 리포트',
                'color': '#dc3545',
                'icon': 'fas fa-globe-americas'
            },
            'integrated': {
                'title': 'POSCO 뉴스 통합 분석 리포트',
                'color': '#6f42c1',
                'icon': 'fas fa-chart-pie'
            }
        }

    def generate_test_html(self, report_type):
        """테스트용 HTML 리포트 생성"""
        config = self.report_types[report_type]
        timestamp = datetime.now()
        
        # 랜덤 데이터 생성
        news_count = random.randint(1, 5)
        sentiment_options = ['긍정', '부정', '중립', '상승', '하락', '안정']
        sentiment = random.choice(sentiment_options)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[테스트] {config['title']}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, {config['color']} 0%, {config['color']}dd 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .test-badge {{
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            display: inline-block;
            margin-top: 1rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid {config['color']};
        }}
        
        .stat-card h3 {{
            color: {config['color']};
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }}
        
        .content-section {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }}
        
        .content-section h2 {{
            color: {config['color']};
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #eee;
        }}
        
        .news-item {{
            padding: 1rem;
            border: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}
        
        .news-item:hover {{
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .news-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }}
        
        .news-meta {{
            font-size: 0.9rem;
            color: #666;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .sentiment {{
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        
        .sentiment.positive {{ background: #d4edda; color: #155724; }}
        .sentiment.negative {{ background: #f8d7da; color: #721c24; }}
        .sentiment.neutral {{ background: #e2e3e5; color: #383d41; }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }}
        
        .theme-test-info {{
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .header {{ padding: 1rem; }}
            .header h1 {{ font-size: 1.5rem; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="theme-test-info">
            <i class="fas fa-flask"></i>
            <strong>테마 시스템 테스트 리포트</strong> - 
            다양한 테마에서 이 리포트가 어떻게 보이는지 확인해보세요!
        </div>
        
        <div class="header">
            <h1>
                <i class="{config['icon']}"></i>
                {config['title']}
            </h1>
            <div class="subtitle">
                {timestamp.strftime('%Y년 %m월 %d일 %H:%M:%S')} 생성
            </div>
            <div class="test-badge">
                <i class="fas fa-vial"></i> 테스트 리포트
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>분석 뉴스 수</h3>
                <div class="value">{news_count}</div>
            </div>
            <div class="stat-card">
                <h3>시장 감정</h3>
                <div class="value">{sentiment}</div>
            </div>
            <div class="stat-card">
                <h3>완료율</h3>
                <div class="value">{news_count}/{news_count}</div>
            </div>
            <div class="stat-card">
                <h3>신뢰도</h3>
                <div class="value">{random.randint(85, 99)}%</div>
            </div>
        </div>
        
        <div class="content-section">
            <h2><i class="fas fa-newspaper"></i> 분석된 뉴스</h2>
            {self._generate_news_items(news_count, report_type)}
        </div>
        
        <div class="content-section">
            <h2><i class="fas fa-chart-bar"></i> 주요 인사이트</h2>
            <ul>
                <li>테스트 데이터를 기반으로 한 분석 결과입니다.</li>
                <li>실제 시장 상황과는 무관한 테스트용 데이터입니다.</li>
                <li>테마 시스템의 색상 변화를 확인하기 위한 목적입니다.</li>
                <li>다양한 테마에서 가독성을 테스트할 수 있습니다.</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>
                <i class="fas fa-robot"></i>
                POSCO 뉴스 분석 시스템 | 테스트 리포트 생성기
            </p>
            <p>생성 시간: {timestamp.isoformat()}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content

    def _generate_news_items(self, count, report_type):
        """뉴스 아이템 HTML 생성"""
        items = []
        sentiments = ['positive', 'negative', 'neutral']
        sentiment_labels = ['긍정', '부정', '중립']
        
        for i in range(count):
            sentiment_class = random.choice(sentiments)
            sentiment_label = sentiment_labels[sentiments.index(sentiment_class)]
            
            item = f"""
            <div class="news-item">
                <div class="news-title">
                    [{report_type.upper()}] 테스트 뉴스 제목 {i+1} - {sentiment_label} 감정
                </div>
                <div class="news-meta">
                    <span><i class="fas fa-clock"></i> {random.randint(1, 12)}시간 전</span>
                    <span class="sentiment {sentiment_class}">{sentiment_label}</span>
                    <span><i class="fas fa-eye"></i> {random.randint(100, 999)} 조회</span>
                </div>
            </div>
            """
            items.append(item)
        
        return ''.join(items)

    def create_test_report(self, report_type):
        """테스트 리포트 생성 및 저장"""
        print(f"🧪 {report_type} 테스트 리포트 생성 중...")
        
        # HTML 생성
        html_content = self.generate_test_html(report_type)
        
        # 파일명 생성
        timestamp = datetime.now()
        filename = f"test_{report_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        
        # 파일 저장
        os.makedirs("docs/reports", exist_ok=True)
        filepath = os.path.join("docs/reports", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 메타데이터 업데이트
        self._update_metadata(filename, report_type, timestamp, len(html_content.encode('utf-8')))
        
        print(f"✅ 테스트 리포트 생성 완료: {filename}")
        return filename

    def _update_metadata(self, filename, report_type, timestamp, file_size):
        """reports_index.json 업데이트"""
        index_path = "docs/reports_index.json"
        
        # 기존 데이터 로드
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"lastUpdate": "", "totalReports": 0, "reports": []}
        
        # 새 리포트 메타데이터
        config = self.report_types[report_type]
        report_id = filename.replace('.html', '')
        
        new_report = {
            "id": report_id,
            "filename": filename,
            "title": f"[테스트] {config['title']}",
            "type": report_type,
            "date": timestamp.strftime('%Y-%m-%d'),
            "time": timestamp.strftime('%H:%M:%S'),
            "size": file_size,
            "summary": {
                "newsCount": random.randint(1, 5),
                "completionRate": "100%",
                "marketSentiment": random.choice(['긍정', '부정', '중립']),
                "keyInsights": ["테스트 데이터", "테마 시스템 검증", "UI 확인"]
            },
            "tags": ["테스트", report_type, "테마검증"],
            "url": f"https://shuserker.github.io/infomax_api/reports/{filename}",
            "createdAt": timestamp.isoformat() + 'Z'
        }
        
        # 리포트 추가
        data["reports"].insert(0, new_report)  # 최신 순으로 정렬
        data["totalReports"] = len(data["reports"])
        data["lastUpdate"] = timestamp.isoformat() + 'Z'
        
        # 저장
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_test_suite(self):
        """전체 테스트 스위트 생성"""
        print("🎨 테마 시스템 테스트 스위트 생성 중...")
        
        created_files = []
        for report_type in self.report_types.keys():
            filename = self.create_test_report(report_type)
            created_files.append(filename)
        
        print(f"🎉 테스트 스위트 완료! {len(created_files)}개 리포트 생성:")
        for filename in created_files:
            print(f"  - {filename}")
        
        return created_files

def main():
    generator = SimpleTestGenerator()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'suite':
            generator.create_test_suite()
        elif command in generator.report_types:
            generator.create_test_report(command)
        else:
            print(f"사용법: python simple_test_generator.py [suite|{'/'.join(generator.report_types.keys())}]")
    else:
        generator.create_test_suite()

if __name__ == "__main__":
    main()