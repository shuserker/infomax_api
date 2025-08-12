#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated Report Generator
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import test_config.json
from datetime import datetime
from pathlib import Path
import system_functionality_verification.py

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(current_dir))

try:
# REMOVED:     from Monitoring/POSCO_News_250808/github_pages_deployer.py import deploy_report_to_github
except ImportError:
    deploy_report_to_github = None

class IntegratedReportGenerator:
    """
    통합 리포트 생성 클래스
    """
    
    def __init__(self):
        """
        통합 리포트 생성기 초기화
        """
        pass
    
    def generate_integrated_report(self, news_data_dict=None):
        """
        3개 뉴스 타입의 데이터를 통합하여 종합 리포트 생성
        데이터가 불완전한 경우 직전 영업일 데이터 사용
        
        Args:
            news_data_dict (dict, optional): {
                'exchange-rate': {...},
                'kospi-close': {...}, 
                'newyork-market-watch': {...}
            }
            
        Returns:
            dict: 생성된 파일 정보
        """
        # 영업일 헬퍼 사용하여 완전한 데이터 조회
        if news_data_dict is None:
# REMOVED:             from docs/assets/js/utils.js import BusinessDayHelper
            helper = BusinessDayHelper()
            complete_data = helper.get_complete_news_data()
            news_data_dict = complete_data['news_data']
            data_date = complete_data['date']
            is_current_day = complete_data['is_current_day']
        else:
            # 현재 데이터 완성도 체크
            completed_count = sum(1 for data in news_data_dict.values() if data and data.get('title'))
            if completed_count < 3:
                print(f"⚠️ 현재 데이터 불완전 ({completed_count}/3) - 직전 영업일 데이터 조회")
# REMOVED:                 from docs/assets/js/utils.js import BusinessDayHelper
                helper = BusinessDayHelper()
                complete_data = helper.get_complete_news_data()
                news_data_dict = complete_data['news_data']
                data_date = complete_data['date']
                is_current_day = complete_data['is_current_day']
            else:
                data_date = datetime.now()
                is_current_day = True
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deployment_verification_checklist.md"
        
        # 통합 분석 데이터 준비
        integrated_analysis = self._prepare_integrated_analysis(news_data_dict, data_date, is_current_day)
        
        # HTML 템플릿 생성
        html_content = self._create_integrated_html_template(integrated_analysis)
        
        # reports 디렉토리에 파일 저장
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / filename
with_open(report_file,_'w',_encoding = 'utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 통합 리포트 생성 완료: {filename}")
        
        # 메타데이터 자동 업데이트
        try:
# REMOVED:             from Monitoring/POSCO_News_250808/reports/metadata_manager.py import add_report_metadata
            add_report_metadata(filename, report_file)
            print(f"📊 메타데이터 업데이트 완료: {filename}")
        except Exception as e:
            print(f"⚠️ 메타데이터 업데이트 실패: {e}")
        
        # GitHub Pages 배포 시도
        github_url = None
        try:
            if deploy_report_to_github:
                github_url = deploy_report_to_github(filename)
                if github_url:
                    print(f"🌐 GitHub Pages 배포 완료: {github_url}")
        except Exception as e:
            print(f"⚠️ GitHub Pages 배포 실패: {e}")
        
        # GitHub URL이 None인 경우 기본 URL 사용
        if github_url is None:
            github_url = f"https:/shuserker.github.io/infomax_api/reports/{filename}"
            print(f"⚠️ GitHub 배포 실패, 기본 URL 사용: {github_url}")
        
        return {
            'filename': filename,
            'local_path': str(report_file),
            'github_url': github_url,
            'web_url': github_url,
            'display_name': '통합 분석 리포트'
        }
    
    def _prepare_integrated_analysis(self, news_data_dict, data_date, is_current_day):
        """
        통합 분석 데이터 준비
        
        Args:
            news_data_dict (dict): 3개 뉴스 타입 데이터
            data_date (datetime): 데이터 기준 날짜
            is_current_day (bool): 현재일 데이터 여부
            
        Returns:
            dict: 통합 분석 결과
        """
        current_time = datetime.now()
        
        # 각 뉴스 타입별 상태 확인
        news_status = {}
        total_published = 0
        
        for news_type, data in news_data_dict.items():
            if data and data.get('title'):
                news_status[news_type] = {
                    'published': True,
                    'title': data.get('title', ''),
                    'publish_time': data.get('publish_time', ''),
                    'content': data.get('content', '')
                }
total_published_+ =  1
            else:
                news_status[news_type] = {
                    'published': False,
                    'title': '',
                    'publish_time': '',
                    'content': ''
                }
        
        # 종합 시장 분석
        market_analysis = self._analyze_integrated_market(news_data_dict)
        
        # 투자 전략 통합
        investment_strategy = self._generate_integrated_strategy(news_data_dict)
        
        # 리스크 분석 통합
        risk_analysis = self._generate_integrated_risk_analysis(news_data_dict)
        
        return {
            'generation_time': current_time.strftime("%Y-%m-%d %H:%M:%S"),
            'data_date': data_date.strftime("%Y-%m-%d"),
            'is_current_day': is_current_day,
            'news_status': news_status,
            'total_published': total_published,
            'market_analysis': market_analysis,
            'investment_strategy': investment_strategy,
            'risk_analysis': risk_analysis,
            'summary': self._generate_daily_summary(news_status, market_analysis, data_date, is_current_day)
        }
    
    def _analyze_integrated_market(self, news_data_dict):
        """통합 시장 분석"""
        analysis = {
            'overall_sentiment': '중립',
            'key_insights': [],
            'sector_performance': {},
            'global_impact': {}
        }
        
        positive_signals = 0
        negative_signals = 0
        total_signals = 0
        
        # 각 뉴스별 시장 신호 분석
        for news_type, data in news_data_dict.items():
            if not data or not data.get('title'):
                continue
                
            title = data.get('title', '').lower()
            content = data.get('content', '').lower()
            
            # 긍정적 키워드
            positive_keywords = ['상승', '증가', '호조', '개선', '성장', '확대', '강세']
            # 부정적 키워드  
            negative_keywords = ['하락', '감소', '부진', '악화', '위축', '축소', '약세']
            
            for keyword in positive_keywords:
                if keyword in title or keyword in content:
positive_signals_+ =  1
total_signals_+ =  1
                    break
            
            for keyword in negative_keywords:
                if keyword in title or keyword in content:
negative_signals_+ =  1
total_signals_+ =  1
                    break
        
        # 전체 감정 판단
        if total_signals > 0:
            positive_ratio = positive_signals / total_signals
            if positive_ratio >= 0.6:
                analysis['overall_sentiment'] = '긍정'
            elif positive_ratio <= 0.4:
                analysis['overall_sentiment'] = '부정'
        
        # 핵심 인사이트 생성
        if news_data_dict.get('exchange-rate'):
            analysis['key_insights'].append('💱 환율 동향이 시장에 영향을 미치고 있습니다')
        
        if news_data_dict.get('kospi-close'):
            analysis['key_insights'].append('📈 국내 증시 마감 상황을 주목해야 합니다')
            
        if news_data_dict.get('newyork-market-watch'):
            analysis['key_insights'].append('🌆 뉴욕 시장 동향이 글로벌 영향을 주고 있습니다')
        
        return analysis
    
    def _generate_integrated_strategy(self, news_data_dict):
        """통합 투자 전략 생성"""
        strategies = {
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }
        
        published_count = sum(1 for data in news_data_dict.values() if data and data.get('title'))
        
        if published_count >= 3:
            strategies['short_term'].append('모든 뉴스가 발행되어 종합적 판단이 가능합니다')
            strategies['medium_term'].append('다양한 시장 신호를 종합하여 포트폴리오를 조정하세요')
        elif published_count >= 2:
            strategies['short_term'].append('주요 뉴스가 발행되어 부분적 판단이 가능합니다')
            strategies['medium_term'].append('추가 뉴스 발행을 기다려 전체적 판단을 하세요')
        else:
            strategies['short_term'].append('뉴스 발행이 부족하여 신중한 접근이 필요합니다')
            strategies['medium_term'].append('추가 정보 수집 후 투자 결정을 하세요')
        
        strategies['long_term'].append('장기적으로는 POSCO 관련 뉴스 트렌드를 지속 모니터링하세요')
        
        return strategies
    
    def _generate_integrated_risk_analysis(self, news_data_dict):
        """통합 리스크 분석"""
        risks = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        published_count = sum(1 for data in news_data_dict.values() if data and data.get('title'))
        
        if published_count < 2:
            risks['high'].append('정보 부족으로 인한 투자 판단 리스크')
        
        if published_count < 3:
            risks['medium'].append('일부 뉴스 미발행으로 인한 불완전한 시장 분석')
        
        # 각 뉴스별 리스크 요소 확인
        for news_type, data in news_data_dict.items():
            if data and data.get('title'):
                title = data.get('title', '').lower()
                if any(word in title for word in ['급락', '폭락', '위기', '충격']):
                    risks['high'].append(f'{news_type} 관련 급격한 시장 변동 위험')
        
        if not risks['high'] and not risks['medium']:
            risks['low'].append('현재 특별한 리스크 요인이 발견되지 않았습니다')
        
        return risks
    
    def _generate_daily_summary(self, news_status, market_analysis, data_date, is_current_day):
        """일일 종합 요약 생성"""
        published_count = sum(1 for status in news_status.values() if status['published'])
        total_count = len(news_status)
        
        summary = {
            'completion_rate': f"{published_count}/{total_count}",
            'overall_status': '완료' if published_count == total_count else '진행중',
            'market_sentiment': market_analysis['overall_sentiment'],
            'key_message': '',
            'data_source': '당일 데이터' if is_current_day else f"{data_date.strftime('%Y-%m-%d')} 데이터"
        }
        
        if not is_current_day:
            summary['key_message'] = f"{data_date.strftime('%Y-%m-%d')} 완전한 뉴스 데이터를 기반으로 분석했습니다. 전체적으로 {market_analysis['overall_sentiment']} 분위기였습니다."
        elif published_count == total_count:
            summary['key_message'] = f"오늘의 모든 뉴스가 발행 완료되었습니다. 전체적으로 {market_analysis['overall_sentiment']} 분위기입니다."
        else:
            summary['key_message'] = f"현재 {published_count}개 뉴스가 발행되었습니다. 추가 뉴스를 기다리고 있습니다."
        
        return summary
    
    def _create_integrated_html_template(self, analysis):
        """통합 HTML 템플릿 생성"""
        current_time = analysis['generation_time']
        
        # 뉴스 상태 HTML 생성
        news_status_html = self._generate_news_status_html(analysis['news_status'])
        
        # 시장 분석 HTML 생성
        market_analysis_html = self._generate_market_analysis_html(analysis['market_analysis'])
        
        # 투자 전략 HTML 생성
        strategy_html = self._generate_strategy_html(analysis['investment_strategy'])
        
        # 리스크 분석 HTML 생성
        risk_html = self._generate_risk_html(analysis['risk_analysis'])
        
        html = f"""
<!DOCTYPE html>
<html_lang = "ko">
<head>
<meta_charset = "UTF-8">
<meta_name = "viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 POSCO 뉴스 통합 분석 리포트</title>
<script_src = "https:/cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        
        .header .timestamp {{
            color: #95a5a6;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .summary-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .news-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .news-published {{
            border-left-color: #27ae60;
        }}
        
        .news-pending {{
            border-left-color: #e74c3c;
        }}
        
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .status-published {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-pending {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .insight-box {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        
        .strategy-item {{
            background: #e8f5e8;
            border-left: 4px solid #28a745;
            padding: 12px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .risk-item {{
            padding: 12px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        
        .risk-high {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .risk-medium {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        
        .risk-low {{
            background: #d1ecf1;
            border-left-color: #17a2b8;
        }}
        
        .footer {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
        }}
        
        @media (max-width: 768px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 POSCO 뉴스 통합 분석 리포트</h1>
            <div class="subtitle">일일 종합 시장 분석 및 투자 인사이트</div>
            <div class="timestamp">생성 시간: {current_time}</div>
        </div>
        
        <div class="summary-card">
            <h2>📋 종합 요약</h2>
            <div class="insight-box">
                <h3>📊 발행 현황: {analysis['summary']['completion_rate']} ({analysis['summary']['overall_status']})</h3>
                <h3>📈 시장 분위기: {analysis['summary']['market_sentiment']}</h3>
                <h3>📅 데이터 기준: {analysis['summary']['data_source']}</h3>
                <p>{analysis['summary']['key_message']}</p>
            </div>
        </div>
        
        <div class="content-grid">
            {news_status_html}
            {market_analysis_html}
            {strategy_html}
            {risk_html}
        </div>
        
        <div class="footer">
            <p>© 2025 POSCO 뉴스 AI 분석 시스템 | 통합 리포트 v1.0</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_news_status_html(self, news_status):
        """뉴스 상태 HTML 생성"""
        news_names = {
            'exchange-rate': '💱 서환마감',
            'kospi-close': '📈 증시마감', 
            'newyork-market-watch': '🌆 뉴욕마켓워치'
        }
        
        items_html = ""
        for news_type, status in news_status.items():
            name = news_names.get(news_type, news_type)
            if status['published']:
items_html_+ =  f"""
                <div class="news-item news-published">
                    <div>
<div_style = "font-weight: bold;">{name}</div>
<div_style = "font-size: 0.9em; color: #666;">{status['publish_time']}</div>
                    </div>
                    <span class="status-badge status-published">✅ 발행완료</span>
                </div>
                """
            else:
items_html_+ =  f"""
                <div class="news-item news-pending">
                    <div>
<div_style = "font-weight: bold;">{name}</div>
<div_style = "font-size: 0.9em; color: #666;">발행 대기중</div>
                    </div>
                    <span class="status-badge status-pending">⏳ 대기중</span>
                </div>
                """
        
        return f"""
        <div class="card">
            <h2>📰 뉴스 발행 현황</h2>
            {items_html}
        </div>
        """
    
    def _generate_market_analysis_html(self, market_analysis):
        """시장 분석 HTML 생성"""
        insights_html = ""
        for insight in market_analysis['key_insights']:
insights_html_+ =  f"<div class='insight-box'>{insight}</div>"
        
        return f"""
        <div class="card">
            <h2>📊 통합 시장 분석</h2>
            <div class="insight-box">
                <h3>📈 전체 시장 분위기: {market_analysis['overall_sentiment']}</h3>
            </div>
            {insights_html}
        </div>
        """
    
    def _generate_strategy_html(self, strategy):
        """투자 전략 HTML 생성"""
        strategy_html = ""
        
        for term, strategies in strategy.items():
            term_name = {'short_term': '단기', 'medium_term': '중기', 'long_term': '장기'}[term]
            for s in strategies:
strategy_html_+ =  f"<div class='strategy-item'><strong>📊 {term_name}:</strong> {s}</div>"
        
        return f"""
        <div class="card">
            <h2>💼 통합 투자 전략</h2>
            {strategy_html}
        </div>
        """
    
    def _generate_risk_html(self, risk_analysis):
        """리스크 분석 HTML 생성"""
        risk_html = ""
        
        for level, risks in risk_analysis.items():
            level_name = {'high': '🔴 높음', 'medium': '🟡 보통', 'low': '🟢 낮음'}[level]
            for risk in risks:
risk_html_+ =  f"<div class='risk-item risk-{level}'><strong>{level_name}:</strong> {risk}</div>"
        
        return f"""
        <div class="card">
            <h2>⚠️ 통합 리스크 분석</h2>
            {risk_html}
        </div>
        """

if __name__ == "__main__":
    # 테스트 실행
    generator = IntegratedReportGenerator()
    
    # 테스트 데이터
    test_data = {
        'exchange-rate': {
            'title': '달러-원 환율 1,350원대 마감',
            'publish_time': '17:30',
            'content': '환율이 상승세를 보였습니다.'
        },
        'kospi-close': {
            'title': 'KOSPI 2,500선 회복',
            'publish_time': '15:30', 
            'content': '증시가 강세를 보였습니다.'
        },
        'newyork-market-watch': None
    }
    
    result = generator.generate_integrated_report(test_data)
    print("테스트 완료:", result)