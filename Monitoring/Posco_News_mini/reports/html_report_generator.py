# -*- coding: utf-8 -*-
"""
POSCO 뉴스 분석 HTML 리포트 생성기

상세한 분석 결과를 아름다운 HTML 리포트로 생성합니다.
웹훅 메시지는 간단한 요약으로, 상세 분석은 HTML로 제공하는 하이브리드 방식입니다.

주요 기능:
- 반응형 웹 디자인
- 인터랙티브 차트 (Chart.js)
- 섹터별 상세 분석
- 투자 전략 가이드
- 리스크 관리 포인트

작성자: AI Assistant
최종 수정: 2025-07-28
"""

import os
import json
from datetime import datetime
from pathlib import Path

class HTMLReportGenerator:
    """
    HTML 리포트 생성 클래스
    """
    
    def __init__(self):
        """
        HTML 리포트 생성기 초기화 (GitHub Pages 전용)
        """
        pass
    
    def generate_report(self, analysis_result, news_type, display_name):
        """
        HTML 리포트 생성 (GitHub Actions 배포 방식)
        
        Args:
            analysis_result (dict): 분석 결과
            news_type (str): 뉴스 타입
            display_name (str): 표시명
            
        Returns:
            dict: 생성된 파일 정보
        """
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"posco_analysis_{news_type}_{timestamp}.html"
        
        # HTML 템플릿 생성
        html_content = self._create_html_template(analysis_result, news_type, display_name)
        
        # reports 디렉토리에 파일 저장
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / filename
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 리포트 생성 완료: {filename}")
        
        # GitHub Pages 배포 시도
        github_url = None
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from github_pages_deployer import deploy_report_to_github
            github_url = deploy_report_to_github(filename)
            if github_url:
                print(f"🌐 GitHub Pages 배포 완료: {github_url}")
        except Exception as e:
            print(f"⚠️ GitHub Pages 배포 실패: {e}")
        
        # GitHub URL이 None인 경우 기본 URL 사용
        if github_url is None:
            github_url = f"https://shuserker.github.io/infomax_api/reports/{filename}"
            print(f"⚠️ GitHub 배포 실패, 기본 URL 사용: {github_url}")
        
        return {
            'filename': filename,
            'local_path': str(report_file),
            'github_url': github_url,
            'web_url': github_url,
            'display_name': display_name
        }
    
    def _create_html_template(self, analysis_result, news_type, display_name):
        """
        HTML 템플릿 생성
        
        Args:
            analysis_result (dict): 분석 결과
            news_type (str): 뉴스 타입
            display_name (str): 표시명
            
        Returns:
            str: HTML 콘텐츠
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POSCO {display_name} AI 분석 리포트</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            background: #f8f9fa;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-bottom: 2px solid #e9ecef;
            padding: 20px 0;
            margin-bottom: 20px;
            text-align: center;
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
        
        .content-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .card h2 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .sector-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .sector-name {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .sector-status {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status-positive {{
            color: #27ae60;
        }}
        
        .status-negative {{
            color: #e74c3c;
        }}
        
        .status-neutral {{
            color: #95a5a6;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        
        .insight-box {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
        }}
        
        .strategy-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .strategy-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .risk-item {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        
        .risk-high {{
            background: #f8d7da;
            border-color: #f5c6cb;
        }}
        
        .risk-medium {{
            background: #fff3cd;
            border-color: #ffeaa7;
        }}
        
        .risk-low {{
            background: #d1ecf1;
            border-color: #bee5eb;
        }}
        
        .footer {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #7f8c8d;
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
            <h1>📊 POSCO {display_name} AI 분석 리포트</h1>
            <div class="subtitle">고급 AI 분석을 통한 시장 인사이트</div>
            <div class="timestamp">생성 시간: {current_time}</div>
        </div>
        
        <div class="content-grid">
            {self._generate_basic_info_card(analysis_result)}
            {self._generate_sector_analysis_card(analysis_result)}
            {self._generate_market_insights_card(analysis_result)}
            {self._generate_investment_strategy_card(analysis_result)}
            {self._generate_risk_management_card(analysis_result)}
            {self._generate_global_impact_card(analysis_result)}
        </div>
        
        <div class="footer">
            <p>© 2025 POSCO 뉴스 AI 분석 시스템 | 실시간 시장 모니터링</p>
        </div>
    </div>
    
    <script>
        // 섹터별 성과 차트
        const sectorCtx = document.getElementById('sectorChart');
        if (sectorCtx) {{
            new Chart(sectorCtx, {{
                type: 'bar',
                data: {{
                    labels: {self._get_sector_labels(analysis_result)},
                    datasets: [{{
                        label: '언급 횟수',
                        data: {self._get_sector_data(analysis_result)},
                        backgroundColor: [
                            '#3498db',
                            '#e74c3c',
                            '#2ecc71',
                            '#f39c12',
                            '#9b59b6',
                            '#1abc9c'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{
                                color: 'rgba(0,0,0,0.1)'
                            }}
                        }},
                        x: {{
                            grid: {{
                                display: false
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // 감정 분석 차트
        const sentimentCtx = document.getElementById('sentimentChart');
        if (sentimentCtx) {{
            new Chart(sentimentCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['긍정', '부정', '중립'],
                    datasets: [{{
                        data: {self._get_sentiment_data(analysis_result)},
                        backgroundColor: [
                            '#2ecc71',
                            '#e74c3c',
                            '#95a5a6'
                        ],
                        borderWidth: 3,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_basic_info_card(self, analysis_result):
        """기본 정보 카드 생성"""
        current_news = analysis_result.get('current_news', {})
        total_articles = analysis_result.get('total_articles', 0)
        
        return f"""
        <div class="card">
            <h2>📊 기본 정보</h2>
            <div class="insight-box">
                <h3>분석 범위</h3>
                <p>최근 30일간 총 {total_articles}건의 뉴스 분석</p>
            </div>
            <div style="margin-top: 20px;">
                <h4>최신 뉴스</h4>
                <p style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    {current_news.get('title', 'N/A')}
                </p>
            </div>
        </div>
        """
    
    def _generate_sector_analysis_card(self, analysis_result):
        """섹터 분석 카드 생성"""
        sector_analysis = analysis_result.get('sector_analysis', {})
        sectors_html = ""
        
        for sector, data in sector_analysis.items():
            if data['mentions'] > 0:
                sentiment_emoji = "📈" if data['sentiment'] == "긍정" else "📉" if data['sentiment'] == "부정" else "➡️"
                status_class = "status-positive" if data['sentiment'] == "긍정" else "status-negative" if data['sentiment'] == "부정" else "status-neutral"
                
                prediction_html = ""
                if 'prediction' in data:
                    pred = data['prediction']
                    if pred['next_day_prediction'] != "중립":
                        pred_emoji = "🔮" if pred['next_day_prediction'] == "긍정" else "⚠️"
                        prediction_html = f"<br><small>{pred_emoji} 내일 {pred['next_day_prediction']} 예상 (신뢰도: {pred['prediction_confidence']:.0%})</small>"
                
                sectors_html += f"""
                <div class="sector-item">
                    <div class="sector-name">{sector}</div>
                    <div class="sector-status">
                        <span class="{status_class}">{sentiment_emoji} {data['sentiment']}</span>
                        <span>({data['mentions']}회)</span>
                    </div>
                </div>
                {prediction_html}
                """
        
        return f"""
        <div class="card">
            <h2>🏭 섹터별 성과 분석</h2>
            <div class="chart-container">
                <canvas id="sectorChart"></canvas>
            </div>
            <div style="margin-top: 20px;">
                {sectors_html}
            </div>
        </div>
        """
    
    def _generate_market_insights_card(self, analysis_result):
        """시장 인사이트 카드 생성"""
        # 실제 데이터 기반 인사이트 생성
        insights = self._generate_data_driven_insights(analysis_result)
        
        return f"""
        <div class="card">
            <h2>🧠 데이터 기반 시장 인사이트</h2>
            <div class="chart-container">
                <canvas id="sentimentChart"></canvas>
            </div>
            <div class="insight-box">
                <h3>🔍 핵심 발견사항</h3>
                {insights}
            </div>
        </div>
        """
    
    def _generate_investment_strategy_card(self, analysis_result):
        """투자 전략 카드 생성"""
        # 데이터 기반 투자 전략 생성
        strategies = self._generate_data_driven_strategies(analysis_result)
        
        return f"""
        <div class="card">
            <h2>💼 데이터 기반 투자 전략</h2>
            {strategies}
        </div>
        """
    
    def _generate_risk_management_card(self, analysis_result):
        """리스크 관리 카드 생성"""
        # 데이터 기반 리스크 분석
        risks = self._generate_data_driven_risks(analysis_result)
        
        return f"""
        <div class="card">
            <h2>⚠️ 데이터 기반 리스크 분석</h2>
            {risks}
        </div>
        """
    
    def _generate_global_impact_card(self, analysis_result):
        """글로벌 영향도 카드 생성"""
        global_impact = analysis_result.get('global_impact', {})
        regions_html = ""
        
        for region, data in global_impact.items():
            if data['total_impact'] > 0:
                trend_emoji = "📈" if data['trend'] == "증가" else "📉" if data['trend'] == "감소" else "➡️"
                regions_html += f"""
                <div class="sector-item">
                    <div class="sector-name">{region}</div>
                    <div class="sector-status">
                        <span>{trend_emoji} {data['trend']}</span>
                        <span>({data['total_impact']}회)</span>
                    </div>
                </div>
                """
        
        return f"""
        <div class="card">
            <h2>🌍 글로벌 영향도 분석</h2>
            <div style="margin-top: 20px;">
                {regions_html}
            </div>
        </div>
        """
    
    def _get_sector_labels(self, analysis_result):
        """섹터 라벨 데이터 추출"""
        sector_analysis = analysis_result.get('sector_analysis', {})
        return [sector for sector in sector_analysis.keys() if sector_analysis[sector]['mentions'] > 0]
    
    def _get_sector_data(self, analysis_result):
        """섹터 데이터 추출"""
        sector_analysis = analysis_result.get('sector_analysis', {})
        return [sector_analysis[sector]['mentions'] for sector in sector_analysis.keys() if sector_analysis[sector]['mentions'] > 0]
    
    def _get_sentiment_data(self, analysis_result):
        """감정 분석 데이터 추출"""
        sector_analysis = analysis_result.get('sector_analysis', {})
        positive = len([s for s in sector_analysis.values() if s['sentiment'] == '긍정'])
        negative = len([s for s in sector_analysis.values() if s['sentiment'] == '부정'])
        neutral = len([s for s in sector_analysis.values() if s['sentiment'] == '중립'])
        return [positive, negative, neutral]
    
    def _generate_data_driven_insights(self, analysis_result):
        """
        실제 데이터 기반 인사이트 생성
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            str: HTML 형태의 인사이트
        """
        sector_analysis = analysis_result.get('sector_analysis', {})
        total_articles = analysis_result.get('total_articles', 0)
        
        insights = []
        
        if not sector_analysis or total_articles == 0:
            return "<p>분석할 데이터가 충분하지 않습니다.</p>"
        
        # 1. 시장 동향 인사이트
        market_trend = self._analyze_market_trend(sector_analysis)
        if market_trend:
            insights.append(f"<div class='insight-box'><h4>📊 시장 동향</h4>{market_trend}</div>")
        
        # 2. 투자 기회 인사이트
        investment_opportunity = self._analyze_investment_opportunity(sector_analysis)
        if investment_opportunity:
            insights.append(f"<div class='insight-box'><h4>💡 투자 기회</h4>{investment_opportunity}</div>")
        
        # 3. 리스크 인사이트
        risk_insight = self._analyze_risk_insight(sector_analysis)
        if risk_insight:
            insights.append(f"<div class='insight-box'><h4>⚠️ 리스크 포인트</h4>{risk_insight}</div>")
        
        # 4. 시장 패턴 인사이트
        pattern_insight = self._analyze_market_pattern(sector_analysis)
        if pattern_insight:
            insights.append(f"<div class='insight-box'><h4>🔍 시장 패턴</h4>{pattern_insight}</div>")
        
        return '\n'.join(insights) if insights else "<p>현재 데이터에서 특별한 인사이트를 발견하지 못했습니다.</p>"
    
    def _analyze_market_trend(self, sector_analysis):
        """시장 동향 분석"""
        positive_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '긍정']
        negative_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '부정']
        neutral_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '중립']
        
        total_sectors = len(sector_analysis)
        if total_sectors == 0:
            return None
        
        positive_ratio = len(positive_sectors) / total_sectors
        negative_ratio = len(negative_sectors) / total_sectors
        
        if positive_ratio >= 0.6:
            return f"<p>시장이 <strong>강한 상승세</strong>를 보이고 있습니다. {len(positive_sectors)}개 섹터가 긍정적 감정을 보이며, 이는 시장 전체의 낙관적 분위기를 반영합니다.</p>"
        elif negative_ratio >= 0.6:
            return f"<p>시장이 <strong>강한 하락세</strong>를 보이고 있습니다. {len(negative_sectors)}개 섹터가 부정적 감정을 보이며, 이는 시장 전체의 비관적 분위기를 반영합니다.</p>"
        elif positive_ratio > negative_ratio:
            return f"<p>시장이 <strong>약한 상승세</strong>를 보이고 있습니다. 긍정적 섹터({len(positive_sectors)}개)가 부정적 섹터({len(negative_sectors)}개)보다 많아 점진적 개선이 예상됩니다.</p>"
        elif negative_ratio > positive_ratio:
            return f"<p>시장이 <strong>약한 하락세</strong>를 보이고 있습니다. 부정적 섹터({len(negative_sectors)}개)가 긍정적 섹터({len(positive_sectors)}개)보다 많아 주의가 필요합니다.</p>"
        else:
            return f"<p>시장이 <strong>혼조세</strong>를 보이고 있습니다. 긍정/부정/중립 섹터가 고르게 분포되어 있어 방향성이 불분명합니다.</p>"
    
    def _analyze_investment_opportunity(self, sector_analysis):
        """투자 기회 분석"""
        opportunities = []
        
        # 고신뢰도 긍정 예측 섹터
        high_confidence_positive = []
        for sector, data in sector_analysis.items():
            if 'prediction' in data:
                pred = data['prediction']
                if pred['next_day_prediction'] == '긍정' and pred['prediction_confidence'] >= 0.8:
                    high_confidence_positive.append({
                        'sector': sector,
                        'confidence': pred['prediction_confidence'],
                        'mentions': data['mentions']
                    })
        
        if high_confidence_positive:
            best_opportunity = max(high_confidence_positive, key=lambda x: x['confidence'])
            opportunities.append(f"<p><strong>최고 기회:</strong> {best_opportunity['sector']} - {best_opportunity['confidence']:.0%} 신뢰도로 내일 긍정 전망</p>")
        
        # 언급 급증 섹터
        mention_counts = [data['mentions'] for data in sector_analysis.values()]
        if mention_counts:
            avg_mentions = sum(mention_counts) / len(mention_counts)
            high_mention_sectors = [s for s in sector_analysis.items() if s[1]['mentions'] > avg_mentions * 2]
            
            if high_mention_sectors:
                most_mentioned = max(high_mention_sectors, key=lambda x: x[1]['mentions'])
                opportunities.append(f"<p><strong>관심 집중:</strong> {most_mentioned[0]} - 평균 대비 {most_mentioned[1]['mentions']/avg_mentions:.1f}배 높은 언급</p>")
        
        return '\n'.join(opportunities) if opportunities else "<p>현재 명확한 투자 기회가 보이지 않습니다.</p>"
    
    def _analyze_risk_insight(self, sector_analysis):
        """리스크 인사이트 분석"""
        risks = []
        
        # 전면적 부정 리스크
        negative_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '부정']
        if len(negative_sectors) == len(sector_analysis) and len(sector_analysis) > 0:
            risks.append("<p><strong>전면적 하락 위험:</strong> 모든 섹터가 부정적 감정을 보여 시장 전체의 하락 가능성이 높습니다.</p>")
        
        # 예측 불확실성
        low_confidence_count = 0
        for sector, data in sector_analysis.items():
            if 'prediction' in data and data['prediction']['prediction_confidence'] < 0.6:
                low_confidence_count += 1
        
        if low_confidence_count >= len(sector_analysis) * 0.5:
            risks.append(f"<p><strong>예측 불확실성:</strong> {low_confidence_count}개 섹터의 신뢰도가 낮아 투자 결정에 주의가 필요합니다.</p>")
        
        # 섹터 집중 리스크
        mention_counts = [data['mentions'] for data in sector_analysis.values()]
        if mention_counts:
            max_mentions = max(mention_counts)
            total_mentions = sum(mention_counts)
            concentration_ratio = max_mentions / total_mentions if total_mentions > 0 else 0
            
            if concentration_ratio > 0.6:
                most_concentrated = max(sector_analysis.items(), key=lambda x: x[1]['mentions'])
                risks.append(f"<p><strong>섹터 집중 리스크:</strong> {most_concentrated[0]}에 {concentration_ratio:.0%} 집중되어 분산 투자가 시급합니다.</p>")
        
        return '\n'.join(risks) if risks else "<p>현재 특별한 리스크 요인이 발견되지 않았습니다.</p>"
    
    def _analyze_market_pattern(self, sector_analysis):
        """시장 패턴 분석"""
        patterns = []
        
        # 섹터별 성과 분포
        sentiment_distribution = {}
        for sector, data in sector_analysis.items():
            sentiment = data['sentiment']
            if sentiment not in sentiment_distribution:
                sentiment_distribution[sentiment] = []
            sentiment_distribution[sentiment].append(sector)
        
        if len(sentiment_distribution.get('긍정', [])) >= 3:
            patterns.append("<p><strong>다양한 성장 동력:</strong> 여러 섹터가 동시에 긍정적 성과를 보여 시장의 견고한 성장 기반을 형성하고 있습니다.</p>")
        
        # 언급 패턴
        mention_counts = [data['mentions'] for data in sector_analysis.values()]
        if mention_counts:
            mention_variance = sum((x - sum(mention_counts)/len(mention_counts))**2 for x in mention_counts) / len(mention_counts)
            if mention_variance > 10:
                patterns.append("<p><strong>섹터 간 관심도 차이:</strong> 특정 섹터에 관심이 집중되어 있어 시장의 선택적 투자가 이루어지고 있습니다.</p>")
            else:
                patterns.append("<p><strong>균등한 관심 분포:</strong> 섹터별 관심도가 고르게 분포되어 있어 안정적인 시장 환경을 보여줍니다.</p>")
        
        return '\n'.join(patterns) if patterns else "<p>현재 특별한 시장 패턴이 발견되지 않았습니다.</p>"
    
    def _generate_data_driven_strategies(self, analysis_result):
        """
        데이터 기반 투자 전략 생성
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            str: HTML 형태의 전략
        """
        sector_analysis = analysis_result.get('sector_analysis', {})
        if not sector_analysis:
            return "<p>전략 수립을 위한 데이터가 부족합니다.</p>"
        
        strategies = []
        
        # 1. 즉시 실행 전략
        immediate_actions = self._generate_immediate_actions(sector_analysis)
        if immediate_actions:
            strategies.append(f"<div class='insight-box'><h4>🚀 즉시 실행 전략</h4>{immediate_actions}</div>")
        
        # 2. 포트폴리오 조정 전략
        portfolio_strategy = self._generate_portfolio_strategy(sector_analysis)
        if portfolio_strategy:
            strategies.append(f"<div class='insight-box'><h4>⚖️ 포트폴리오 조정</h4>{portfolio_strategy}</div>")
        
        # 3. 리스크 관리 전략
        risk_strategy = self._generate_risk_strategy(sector_analysis)
        if risk_strategy:
            strategies.append(f"<div class='insight-box'><h4>🛡️ 리스크 관리</h4>{risk_strategy}</div>")
        
        return '\n'.join(strategies) if strategies else "<p>현재 특별한 투자 전략이 필요하지 않습니다.</p>"
    
    def _generate_immediate_actions(self, sector_analysis):
        """즉시 실행 전략 생성"""
        actions = []
        
        # 최고 기회 섹터
        best_opportunities = []
        for sector, data in sector_analysis.items():
            if 'prediction' in data:
                pred = data['prediction']
                if pred['next_day_prediction'] == '긍정' and pred['prediction_confidence'] >= 0.8:
                    best_opportunities.append({
                        'sector': sector,
                        'confidence': pred['prediction_confidence'],
                        'mentions': data['mentions']
                    })
        
        if best_opportunities:
            best = max(best_opportunities, key=lambda x: x['confidence'])
            actions.append(f"<p><strong>매수 우선순위:</strong> {best['sector']} - {best['confidence']:.0%} 신뢰도로 내일 긍정 전망이 확실합니다.</p>")
        
        # 긴급 매도 섹터
        urgent_sells = []
        for sector, data in sector_analysis.items():
            if 'prediction' in data:
                pred = data['prediction']
                if pred['next_day_prediction'] == '부정' and pred['prediction_confidence'] >= 0.8:
                    urgent_sells.append({
                        'sector': sector,
                        'confidence': pred['prediction_confidence']
                    })
        
        if urgent_sells:
            worst = max(urgent_sells, key=lambda x: x['confidence'])
            actions.append(f"<p><strong>매도 우선순위:</strong> {worst['sector']} - {worst['confidence']:.0%} 신뢰도로 내일 부정 전망이 확실합니다.</p>")
        
        return '\n'.join(actions) if actions else "<p>현재 즉시 실행할 특별한 전략이 없습니다.</p>"
    
    def _generate_portfolio_strategy(self, sector_analysis):
        """포트폴리오 조정 전략"""
        positive_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '긍정']
        negative_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '부정']
        total_sectors = len(sector_analysis)
        
        if total_sectors == 0:
            return None
        
        positive_ratio = len(positive_sectors) / total_sectors
        negative_ratio = len(negative_sectors) / total_sectors
        
        if positive_ratio >= 0.7:
            return "<p><strong>공격적 성장 전략:</strong> 시장이 강한 상승세를 보이므로 긍정적 섹터 비중을 80%까지 확대하고, 나머지는 현금 보유하세요.</p>"
        elif positive_ratio >= 0.5:
            return "<p><strong>균형 성장 전략:</strong> 긍정적 섹터 비중을 60%로 설정하고, 중립/부정 섹터는 40%로 제한하세요.</p>"
        elif negative_ratio >= 0.7:
            return "<p><strong>보수적 방어 전략:</strong> 시장이 강한 하락세를 보이므로 현금 비중을 70%로 확대하고, 긍정적 섹터만 30%로 제한하세요.</p>"
        elif negative_ratio >= 0.5:
            return "<p><strong>안정적 방어 전략:</strong> 현금 비중을 50%로 설정하고, 긍정적 섹터 30%, 중립 섹터 20%로 배분하세요.</p>"
        else:
            return "<p><strong>관망 전략:</strong> 시장 방향성이 불분명하므로 현재 포트폴리오를 유지하고 추가 관찰하세요.</p>"
    
    def _generate_risk_strategy(self, sector_analysis):
        """리스크 관리 전략"""
        strategies = []
        
        # 예측 불확실성 대응
        low_confidence_count = 0
        for sector, data in sector_analysis.items():
            if 'prediction' in data and data['prediction']['prediction_confidence'] < 0.6:
                low_confidence_count += 1
        
        if low_confidence_count >= len(sector_analysis) * 0.5:
            strategies.append("<p><strong>예측 불확실성 대응:</strong> 신뢰도가 낮은 섹터가 많으므로 포지션 크기를 줄이고 현금 비중을 확대하세요.</p>")
        
        # 섹터 집중 리스크 대응
        mention_counts = [data['mentions'] for data in sector_analysis.values()]
        if mention_counts:
            max_mentions = max(mention_counts)
            total_mentions = sum(mention_counts)
            concentration_ratio = max_mentions / total_mentions if total_mentions > 0 else 0
            
            if concentration_ratio > 0.6:
                strategies.append("<p><strong>분산 투자 강화:</strong> 한 섹터에 과도하게 집중되어 있으므로 다른 섹터로 분산 투자하세요.</p>")
        
        return '\n'.join(strategies) if strategies else "<p>현재 특별한 리스크 관리 전략이 필요하지 않습니다.</p>"
    
    def _generate_data_driven_risks(self, analysis_result):
        """
        데이터 기반 리스크 분석
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            str: HTML 형태의 리스크 분석
        """
        sector_analysis = analysis_result.get('sector_analysis', {})
        if not sector_analysis:
            return "<p>리스크 분석을 위한 데이터가 부족합니다.</p>"
        
        risks = []
        
        # 1. 시장 리스크
        market_risk = self._analyze_market_risk(sector_analysis)
        if market_risk:
            risks.append(f"<div class='insight-box'><h4>📊 시장 리스크</h4>{market_risk}</div>")
        
        # 2. 투자 리스크
        investment_risk = self._analyze_investment_risk(sector_analysis)
        if investment_risk:
            risks.append(f"<div class='insight-box'><h4>💼 투자 리스크</h4>{investment_risk}</div>")
        
        # 3. 데이터 리스크
        data_risk = self._analyze_data_risk(analysis_result)
        if data_risk:
            risks.append(f"<div class='insight-box'><h4>📈 데이터 리스크</h4>{data_risk}</div>")
        
        return '\n'.join(risks) if risks else "<p>현재 특별한 리스크 요인이 발견되지 않았습니다.</p>"
    
    def _analyze_market_risk(self, sector_analysis):
        """시장 리스크 분석"""
        risks = []
        
        # 전면적 부정 리스크
        negative_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '부정']
        if len(negative_sectors) == len(sector_analysis):
            risks.append("<p><strong>전면적 하락 위험:</strong> 모든 섹터가 부정적 감정을 보여 시장 전체의 하락 가능성이 매우 높습니다.</p>")
        
        # 과열 리스크
        positive_sectors = [s for s in sector_analysis.items() if s[1]['sentiment'] == '긍정']
        if len(positive_sectors) == len(sector_analysis):
            risks.append("<p><strong>시장 과열 위험:</strong> 모든 섹터가 긍정적 감정을 보여 시장 과열 가능성이 있습니다.</p>")
        
        # 섹터 간 극화 리스크
        if len(positive_sectors) > 0 and len(negative_sectors) > 0:
            if abs(len(positive_sectors) - len(negative_sectors)) >= 3:
                risks.append("<p><strong>섹터 간 극화:</strong> 긍정/부정 섹터 간 큰 차이로 시장 불균형이 심화될 수 있습니다.</p>")
        
        return '\n'.join(risks) if risks else "<p>현재 특별한 시장 리스크가 발견되지 않았습니다.</p>"
    
    def _analyze_investment_risk(self, sector_analysis):
        """투자 리스크 분석"""
        risks = []
        
        # 예측 불확실성
        low_confidence_count = 0
        for sector, data in sector_analysis.items():
            if 'prediction' in data and data['prediction']['prediction_confidence'] < 0.6:
                low_confidence_count += 1
        
        if low_confidence_count >= len(sector_analysis) * 0.6:
            risks.append(f"<p><strong>높은 예측 불확실성:</strong> {low_confidence_count}개 섹터의 신뢰도가 낮아 투자 결정에 큰 위험이 따릅니다.</p>")
        elif low_confidence_count >= len(sector_analysis) * 0.3:
            risks.append(f"<p><strong>중간 예측 불확실성:</strong> {low_confidence_count}개 섹터의 신뢰도가 낮아 투자 결정에 주의가 필요합니다.</p>")
        
        # 섹터 집중 리스크
        mention_counts = [data['mentions'] for data in sector_analysis.values()]
        if mention_counts:
            max_mentions = max(mention_counts)
            total_mentions = sum(mention_counts)
            concentration_ratio = max_mentions / total_mentions if total_mentions > 0 else 0
            
            if concentration_ratio > 0.7:
                most_concentrated = max(sector_analysis.items(), key=lambda x: x[1]['mentions'])
                risks.append(f"<p><strong>극도 집중 리스크:</strong> {most_concentrated[0]}에 {concentration_ratio:.0%} 집중되어 있어 즉시 분산 투자가 필요합니다.</p>")
            elif concentration_ratio > 0.5:
                most_concentrated = max(sector_analysis.items(), key=lambda x: x[1]['mentions'])
                risks.append(f"<p><strong>높은 집중 리스크:</strong> {most_concentrated[0]}에 {concentration_ratio:.0%} 집중되어 분산 투자를 고려하세요.</p>")
        
        return '\n'.join(risks) if risks else "<p>현재 특별한 투자 리스크가 발견되지 않았습니다.</p>"
    
    def _analyze_data_risk(self, analysis_result):
        """데이터 리스크 분석"""
        risks = []
        
        total_articles = analysis_result.get('total_articles', 0)
        if total_articles < 5:
            risks.append("<p><strong>극도 데이터 부족:</strong> 분석 데이터가 매우 부족하여 신뢰할 수 있는 결론을 도출하기 어렵습니다.</p>")
        elif total_articles < 15:
            risks.append("<p><strong>데이터 부족:</strong> 분석 데이터가 부족하여 결론의 신뢰도가 떨어질 수 있습니다.</p>")
        
        # 글로벌 데이터 리스크
        global_impact = analysis_result.get('global_impact', {})
        if global_impact:
            low_impact_regions = [r for r, d in global_impact.items() if d['total_impact'] < 10]
            if len(low_impact_regions) >= 2:
                risks.append(f"<p><strong>글로벌 데이터 부족:</strong> {', '.join(low_impact_regions)} 지역의 데이터가 부족하여 글로벌 분석의 정확도가 떨어집니다.</p>")
        
        return '\n'.join(risks) if risks else "<p>현재 특별한 데이터 리스크가 발견되지 않았습니다.</p>"
    
    def _update_dashboard(self, analysis_result, news_type, display_name, filename):
        """
        대시보드 업데이트
        
        Args:
            analysis_result (dict): 분석 결과
            news_type (str): 뉴스 타입
            display_name (str): 표시명
            filename (str): 생성된 파일명
        """
        try:
            # 대시보드 데이터 파일 생성
            dashboard_data = {
                'last_update': datetime.now().isoformat(),
                'reports': []
            }
            
            # 기존 리포트 목록 읽기
            dashboard_file = self.docs_dir / "dashboard_data.json"
            if dashboard_file.exists():
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    dashboard_data['reports'] = existing_data.get('reports', [])
            
            # 새 리포트 추가
            new_report = {
                'title': f"{display_name} 분석",
                'type': news_type.upper(),
                'date': datetime.now().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime("%H:%M"),
                'url': f"reports/{filename}",
                'filename': filename
            }
            
            # 중복 제거 (같은 타입의 최신 리포트만 유지)
            dashboard_data['reports'] = [r for r in dashboard_data['reports'] if r['type'] != news_type.upper()]
            dashboard_data['reports'].insert(0, new_report)
            
            # 최대 10개까지만 유지
            dashboard_data['reports'] = dashboard_data['reports'][:10]
            
            # 대시보드 데이터 저장
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"대시보드 업데이트 실패: {e}")
    
    def _update_report_list(self):
        """리포트 목록 업데이트"""
        try:
            # generate_report_list.py 스크립트 실행
            import subprocess
            import sys
            import os
            
            # 현재 작업 디렉토리를 docs로 변경
            original_cwd = os.getcwd()
            os.chdir(str(self.docs_dir))
            
            script_path = "generate_report_list.py"
            if os.path.exists(script_path):
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    print("✅ 리포트 목록 업데이트 완료")
                else:
                    print(f"⚠️ 리포트 목록 업데이트 실패: {result.stderr}")
            else:
                print("⚠️ generate_report_list.py 스크립트를 찾을 수 없습니다.")
            
            # 원래 디렉토리로 복원
            os.chdir(original_cwd)
                
        except Exception as e:
            print(f"리포트 목록 업데이트 실패: {e}")
    
    def _deploy_to_github_pages(self, analysis_result, news_type, display_name, filename):
        """
        GitHub Pages 자동 배포 (간단한 방식)
        """
        try:
            import subprocess
            import threading
            
            def deploy():
                try:
                    # HTML 템플릿 생성
                    html_content = self._create_html_template(analysis_result, news_type, display_name)
                    
                    # 현재 브랜치 저장
                    current_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                                  capture_output=True, text=True).stdout.strip()
                    
                    # publish 브랜치로 전환
                    subprocess.run(['git', 'checkout', 'publish'], capture_output=True)
                    
                    # reports 디렉토리 생성 (없으면)
                    reports_dir = Path('reports')
                    reports_dir.mkdir(exist_ok=True)
                    
                    # HTML 파일 저장
                    report_file = reports_dir / filename
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    # Git 커밋 및 푸시
                    subprocess.run(['git', 'add', '.'], capture_output=True)
                    subprocess.run(['git', 'commit', '-m', f'🚀 자동 배포: {filename}'], capture_output=True)
                    subprocess.run(['git', 'push', 'origin', 'publish'], capture_output=True)
                    
                    # 원래 브랜치로 복귀
                    subprocess.run(['git', 'checkout', current_branch], capture_output=True)
                    
                    print("✅ GitHub Pages 자동 배포 완료")
                        
                except Exception as e:
                    print(f"⚠️ GitHub Pages 자동 배포 실패: {e}")
                    # 오류 시 main 브랜치로 복귀
                    try:
                        subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                    except:
                        pass
            
            # 백그라운드에서 실행
            thread = threading.Thread(target=deploy)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"⚠️ 자동 배포 스레드 생성 실패: {e}")