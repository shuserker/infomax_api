#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Manager
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import test_config.json
import posco_news_250808_monitor.log
from datetime import datetime
from pathlib import Path

class ReportManager:
    """
    리포트 목록 관리 및 대시보드 업데이트 클래스
    """
    
    def __init__(self):
        self.reports_index_file = Path("reports_index.json")
    
    def add_report(self, filename, news_type, display_name, analysis_summary=None):
        """
        새 리포트를 인덱스에 추가
        
        Args:
            filename (str): 리포트 파일명
            news_type (str): 뉴스 타입
            display_name (str): 표시명
            analysis_summary (dict): 분석 요약 정보
        """
        # 기존 인덱스 로드
        reports_index = self.load_reports_index()
        
        # 새 리포트 정보
        report_info = {
            'filename': filename,
            'news_type': news_type,
            'display_name': display_name,
            'created_at': datetime.now().isoformat(),
            'web_url': f"https:/shuserker.github.io/infomax_api/reports/{filename}",
            'summary': analysis_summary or {}
        }
        
        # 뉴스 타입별로 분류하여 추가
        if news_type not in reports_index:
            reports_index[news_type] = []
        
        reports_index[news_type].insert(0, report_info)  # 최신 순으로 정렬
        
        # 각 타입별로 최대 30개까지만 보존 (너무 많아지지 않도록)
        if len(reports_index[news_type]) > 30:
            reports_index[news_type] = reports_index[news_type][:30]
        
        # 인덱스 저장
        self.save_reports_index(reports_index)
        
        return report_info
    
    def load_reports_index(self):
        """리포트 인덱스 로드"""
        try:
            if self.reports_index_file.exists():
with_open(self.reports_index_file,_'r',_encoding = 'utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 리포트 인덱스 로드 실패: {e}")
        
        return {}
    
    def save_reports_index(self, reports_index):
        """리포트 인덱스 저장"""
        try:
with_open(self.reports_index_file,_'w',_encoding = 'utf-8') as f:
json.dump(reports_index,_f,_ensure_ascii = False, indent=2)
        except Exception as e:
            print(f"⚠️ 리포트 인덱스 저장 실패: {e}")
    
    def get_recent_reports(self, limit=10):
        """최근 리포트 목록 반환"""
        reports_index = self.load_reports_index()
        all_reports = []
        
        for news_type, reports in reports_index.items():
            all_reports.extend(reports)
        
        # 생성 시간순으로 정렬
        all_reports.sort(key=lambda x: x['created_at'], reverse=True)
        
        return all_reports[:limit]
    
    def generate_dashboard_html(self):
        """
        대시보드 HTML 생성 (과거 리포트 목록 포함)
        """
        reports_index = self.load_reports_index()
        recent_reports = self.get_recent_reports(20)
        
        html = f"""<!DOCTYPE html>
<html_lang = "ko">
<head>
<meta_charset = "UTF-8">
<meta_name = "viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 POSCO 뉴스 AI 분석 대시보드</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .reports-section {{
            margin-bottom: 30px;
        }}
        .report-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4facfe;
            transition: transform 0.2s;
        }}
        .report-item:hover {{
            transform: translateX(5px);
        }}
        .report-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .report-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .report-link {{
            color: #4facfe;
            text-decoration: none;
            font-weight: 500;
        }}
        .report-link:hover {{
            text-decoration: underline;
        }}
        .news-type-section {{
            margin-bottom: 40px;
        }}
        .news-type-title {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            color: #495057;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 POSCO 뉴스 AI 분석 대시보드</h1>
            <p>실시간 시장 분석 및 투자 인사이트</p>
            <p>최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="content">
            <div class="reports-section">
                <h2>📋 최근 분석 리포트</h2>
                <div class="recent-reports">
"""
        
        # 최근 리포트 목록 추가
        for report in recent_reports:
            created_date = datetime.fromisoformat(report['created_at']).strftime('%Y-%m-%d %H:%M')
html_+ =  f"""
                    <div class="report-item">
                        <div class="report-title">
<a_href = "{report['web_url']}" class="report-link" target="_blank">
                                📊 {report['display_name']} 분석 리포트
                            </a>
                        </div>
                        <div class="report-meta">
                            생성일: {created_date} | 타입: {report['news_type']}
                        </div>
                    </div>
"""
        
        # 뉴스 타입별 섹션 추가
        for news_type, reports in reports_index.items():
            if reports:
                display_name = reports[0]['display_name']
html_+ =  f"""
            </div>
            </div>
            <div class="news-type-section">
                <div class="news-type-title">📈 {display_name} 분석 히스토리</div>
"""
                
                for report in reports[:10]:  # 각 타입별로 최대 10개
                    created_date = datetime.fromisoformat(report['created_at']).strftime('%Y-%m-%d %H:%M')
html_+ =  f"""
                <div class="report-item">
                    <div class="report-title">
<a_href = "{report['web_url']}" class="report-link" target="_blank">
                            {created_date} 분석 리포트
                        </a>
                    </div>
                </div>
"""
                
html_+ =  "</div>"
        
html_+ =  """
        </div>
    </div>
</body>
</html>"""
        
        return html