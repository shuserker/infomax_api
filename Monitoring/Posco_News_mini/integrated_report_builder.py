#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 통합 리포트 빌더

7월 25일부터 현재까지 날짜별 통합 리포트를 생성하는 클래스
요일별 현실적인 시장 시나리오를 적용하여 3개 뉴스 타입을 통합
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from reports.integrated_report_generator import IntegratedReportGenerator

class IntegratedReportBuilder:
    """
    통합 리포트 빌더 클래스
    """
    
    def __init__(self):
        """초기화"""
        self.integrated_generator = IntegratedReportGenerator()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 요일별 시장 시나리오 정의
        self.weekday_scenarios = {
            'Monday': {
                'exchange_sentiment': '상승',
                'kospi_sentiment': '상승', 
                'ny_sentiment': '상승',
                'theme': '주초 상승세',
                'market_mood': '긍정적'
            },
            'Tuesday': {
                'exchange_sentiment': '안정',
                'kospi_sentiment': '혼조',
                'ny_sentiment': '하락',
                'theme': '조정 국면',
                'market_mood': '신중함'
            },
            'Wednesday': {
                'exchange_sentiment': '하락',
                'kospi_sentiment': '하락',
                'ny_sentiment': '혼조',
                'theme': '중간 조정',
                'market_mood': '우려'
            },
            'Thursday': {
                'exchange_sentiment': '안정',
                'kospi_sentiment': '상승',
                'ny_sentiment': '상승',
                'theme': '회복 신호',
                'market_mood': '회복세'
            },
            'Friday': {
                'exchange_sentiment': '상승',
                'kospi_sentiment': '상승',
                'ny_sentiment': '상승',
                'theme': '주말 앞 상승',
                'market_mood': '낙관적'
            },
            'Saturday': {
                'exchange_sentiment': '안정',
                'kospi_sentiment': '보합',
                'ny_sentiment': '보합',
                'theme': '주말 안정',
                'market_mood': '안정적'
            },
            'Sunday': {
                'exchange_sentiment': '안정',
                'kospi_sentiment': '보합',
                'ny_sentiment': '보합',
                'theme': '주말 마감',
                'market_mood': '평온함'
            }
        }
    
    def generate_date_range_reports(self, start_date: str = '2025-07-25', end_date: Optional[str] = None) -> List[Dict]:
        """
        날짜 범위별 통합 리포트 생성
        
        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (Optional[str]): 종료 날짜 (None이면 현재 날짜)
            
        Returns:
            List[Dict]: 생성된 리포트 정보 목록
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        self.logger.info(f"📊 {start_date}부터 {end_date}까지 통합 리포트 생성 시작...")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        generated_reports = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%A')
            
            self.logger.info(f"\\n📅 {date_str} ({day_name}) 통합 리포트 생성 중...")
            
            try:
                # 현실적인 뉴스 데이터 생성
                news_data_dict = self.create_realistic_news_data(date_str)
                
                # 통합 리포트 생성
                report_info = self.generate_single_integrated_report(date_str, news_data_dict)
                
                if report_info and not report_info.get('error'):
                    generated_reports.append({
                        'date': date_str,
                        'day': day_name,
                        'filename': report_info['filename'],
                        'local_path': report_info.get('local_path', ''),
                        'github_url': report_info.get('github_url', ''),
                        'status': 'success',
                        'scenario': self.weekday_scenarios[day_name]['theme']
                    })
                    self.logger.info(f"✅ {date_str} ({day_name}) 리포트 생성 완료: {report_info['filename']}")
                else:
                    generated_reports.append({
                        'date': date_str,
                        'day': day_name,
                        'status': 'failed',
                        'error': report_info.get('error', 'Unknown error')
                    })
                    self.logger.error(f"❌ {date_str} ({day_name}) 리포트 생성 실패")
                    
            except Exception as e:
                self.logger.error(f"❌ {date_str} ({day_name}) 리포트 생성 중 오류: {e}")
                generated_reports.append({
                    'date': date_str,
                    'day': day_name,
                    'status': 'failed',
                    'error': str(e)
                })
            
            current_date += timedelta(days=1)
        
        # 결과 요약
        self.log_generation_summary(generated_reports)
        
        return generated_reports
    
    def create_realistic_news_data(self, date: str) -> Dict[str, Dict]:
        """
        현실적인 뉴스 데이터 생성
        
        Args:
            date (str): 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict[str, Dict]: 3개 뉴스 타입별 데이터
        """
        base_date = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = base_date.strftime('%A')
        scenario = self.weekday_scenarios.get(day_of_week, self.weekday_scenarios['Monday'])
        
        # 날짜별 고유 컨텍스트 생성
        month_day = base_date.strftime('%m월 %d일')
        korean_weekday = self.get_korean_weekday(day_of_week)
        
        news_data_dict = {
            'exchange-rate': {
                'title': f'{date} 원/달러 환율 동향 - {scenario["theme"]}',
                'content': self.generate_exchange_content(month_day, korean_weekday, scenario),
                'sentiment': scenario['exchange_sentiment'],
                'keywords': ['환율', '달러', '외환시장', '수출', 'POSCO'],
                'analysis': {
                    'market_impact': '높음' if scenario['exchange_sentiment'] in ['상승', '하락'] else '보통',
                    'key_points': [
                        f'환율 {scenario["exchange_sentiment"]}',
                        'POSCO 수출 영향',
                        '글로벌 요인 반영'
                    ]
                },
                'published_time': f'{date} 15:30:00',
                'source': '연합뉴스',
                'url': f'https://example.com/news/{date}-exchange'
            },
            'kospi-close': {
                'title': f'{date} KOSPI 마감 - {scenario["theme"]}',
                'content': self.generate_kospi_content(month_day, korean_weekday, scenario),
                'sentiment': scenario['kospi_sentiment'],
                'keywords': ['KOSPI', '증시', '외국인', '기관', 'POSCO'],
                'analysis': {
                    'market_impact': '높음',
                    'key_points': [
                        f'KOSPI {scenario["kospi_sentiment"]}',
                        'POSCO 주가 동향',
                        '철강업종 영향'
                    ]
                },
                'published_time': f'{date} 15:40:00',
                'source': '한국경제',
                'url': f'https://example.com/news/{date}-kospi'
            },
            'newyork-market-watch': {
                'title': f'{date} 뉴욕 증시 동향 - {scenario["theme"]}',
                'content': self.generate_newyork_content(month_day, korean_weekday, scenario),
                'sentiment': scenario['ny_sentiment'],
                'keywords': ['뉴욕', '나스닥', 'S&P500', '기업실적', '글로벌'],
                'analysis': {
                    'market_impact': '높음',
                    'key_points': [
                        f'뉴욕증시 {scenario["ny_sentiment"]}',
                        '글로벌 철강 수요',
                        'POSCO 해외 영향'
                    ]
                },
                'published_time': f'{date} 06:30:00',
                'source': 'MarketWatch',
                'url': f'https://example.com/news/{date}-nyse'
            }
        }
        
        return news_data_dict
    
    def generate_exchange_content(self, month_day: str, weekday: str, scenario: Dict) -> str:
        """환율 뉴스 내용 생성"""
        sentiment_desc = {
            '상승': '상승 압력을 받았습니다',
            '하락': '하락세를 보였습니다',
            '안정': '안정적인 흐름을 유지했습니다',
            '혼조': '혼조세를 나타냈습니다'
        }
        
        return f"""
{month_day} ({weekday}) 서울 외환시장에서 원/달러 환율이 {sentiment_desc[scenario['exchange_sentiment']]}. 
{scenario['theme']} 분위기 속에서 글로벌 경제 상황과 국내 수출 실적이 환율 움직임에 주요 영향을 미쳤습니다.

POSCO를 비롯한 주요 수출 기업들의 실적에도 환율 변동이 직접적인 영향을 줄 것으로 예상됩니다. 
특히 철강 제품의 해외 수출 경쟁력과 원자재 수입 비용 측면에서 {scenario['market_mood']} 전망이 나오고 있습니다.

시장 전문가들은 "{scenario['theme']} 흐름이 당분간 지속될 것"이라며 "수출 기업들의 환헤지 전략이 중요한 시점"이라고 분석했습니다.
        """.strip()
    
    def generate_kospi_content(self, month_day: str, weekday: str, scenario: Dict) -> str:
        """증시 뉴스 내용 생성"""
        sentiment_desc = {
            '상승': '상승 마감했습니다',
            '하락': '하락 마감했습니다',
            '안정': '보합권에서 마감했습니다',
            '혼조': '혼조세로 마감했습니다',
            '보합': '보합권에서 거래를 마쳤습니다'
        }
        
        return f"""
{month_day} ({weekday}) 코스피 지수가 {sentiment_desc[scenario['kospi_sentiment']]}. 
{scenario['theme']} 장세 속에서 외국인과 기관 투자자들의 매매 동향이 지수 움직임에 주요 영향을 미쳤습니다.

철강업종에서는 POSCO홀딩스를 중심으로 {scenario['market_mood']} 흐름을 보였습니다. 
글로벌 철강 수요 전망과 원자재 가격 동향이 업종 전체의 투자심리에 영향을 주었습니다.

증권가에서는 "POSCO그룹의 2차전지 소재 사업 확장과 수소 사업 진출이 중장기 성장 동력"이라며 
"{scenario['theme']} 국면에서도 펀더멘털 개선 기대감이 유지되고 있다"고 평가했습니다.
        """.strip()
    
    def generate_newyork_content(self, month_day: str, weekday: str, scenario: Dict) -> str:
        """뉴욕 증시 뉴스 내용 생성"""
        sentiment_desc = {
            '상승': '상승세를 보였습니다',
            '하락': '하락세를 나타냈습니다',
            '안정': '안정적인 흐름을 유지했습니다',
            '혼조': '혼조세를 보였습니다',
            '보합': '보합권에서 거래되었습니다'
        }
        
        return f"""
{month_day} ({weekday}) 뉴욕 증시가 {sentiment_desc[scenario['ny_sentiment']]}. 
{scenario['theme']} 분위기 속에서 주요 경제 지표와 기업 실적 발표가 시장 분위기를 좌우했습니다.

글로벌 철강 관련 기업들의 주가 동향이 주목받았으며, 이는 POSCO를 비롯한 국내 철강업계에도 
간접적인 영향을 미칠 것으로 분석됩니다. 특히 미국의 인프라 투자 정책과 제조업 회복세가 
철강 수요 전망에 {scenario['market_mood']} 신호를 보내고 있습니다.

월스트리트 애널리스트들은 "글로벌 공급망 재편과 친환경 철강 수요 증가가 
아시아 철강업체들에게 새로운 기회를 제공할 것"이라며 "POSCO의 그린스틸 기술력이 
경쟁 우위 요소로 작용할 것"이라고 전망했습니다.
        """.strip()
    
    def get_korean_weekday(self, english_weekday: str) -> str:
        """영어 요일을 한국어로 변환"""
        weekday_map = {
            'Monday': '월요일',
            'Tuesday': '화요일',
            'Wednesday': '수요일',
            'Thursday': '목요일',
            'Friday': '금요일',
            'Saturday': '토요일',
            'Sunday': '일요일'
        }
        return weekday_map.get(english_weekday, '월요일')
    
    def generate_single_integrated_report(self, date: str, news_data_dict: Dict) -> Dict:
        """
        단일 날짜의 통합 리포트 생성
        
        Args:
            date (str): 날짜
            news_data_dict (Dict): 뉴스 데이터
            
        Returns:
            Dict: 생성된 리포트 정보
        """
        try:
            # 기존 IntegratedReportGenerator 사용
            report_info = self.integrated_generator.generate_integrated_report(news_data_dict)
            
            # 날짜 정보 추가
            if report_info:
                report_info['target_date'] = date
                report_info['news_types_count'] = len([k for k, v in news_data_dict.items() if v])
            
            return report_info
            
        except Exception as e:
            self.logger.error(f"❌ {date} 리포트 생성 실패: {e}")
            return {'error': str(e)}
    
    def log_generation_summary(self, generated_reports: List[Dict]):
        """
        생성 결과 요약 로깅
        
        Args:
            generated_reports (List[Dict]): 생성된 리포트 목록
        """
        success_reports = [r for r in generated_reports if r['status'] == 'success']
        failed_reports = [r for r in generated_reports if r['status'] == 'failed']
        
        self.logger.info("\\n" + "="*60)
        self.logger.info("📋 통합 리포트 생성 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"✅ 성공: {len(success_reports)}/{len(generated_reports)}")
        self.logger.info(f"📊 성공률: {len(success_reports)/len(generated_reports)*100:.1f}%")
        
        if success_reports:
            self.logger.info("\\n📁 생성된 통합 리포트:")
            for report in success_reports:
                self.logger.info(f"  📅 {report['date']} ({report['day']}): {report['filename']}")
                self.logger.info(f"      🎯 시나리오: {report['scenario']}")
                if report.get('github_url'):
                    self.logger.info(f"      🔗 {report['github_url']}")
        
        if failed_reports:
            self.logger.warning("\\n❌ 실패한 리포트:")
            for report in failed_reports:
                self.logger.warning(f"  📅 {report['date']} ({report['day']}): {report.get('error', 'Unknown error')}")
        
        if success_reports:
            self.logger.info(f"\\n🎉 총 {len(success_reports)}개의 새로운 통합 리포트가 생성되었습니다!")
        else:
            self.logger.error("\\n❌ 생성된 리포트가 없습니다. 오류를 확인해주세요.")

def main():
    """메인 실행 함수"""
    builder = IntegratedReportBuilder()
    
    # 7월 25일부터 현재까지 리포트 생성
    results = builder.generate_date_range_reports('2025-07-25')
    
    return results

if __name__ == "__main__":
    main()