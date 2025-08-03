#!/usr/bin/env python3
"""
과거 날짜 통합 리포트 생성기
2025-07-25부터 2025-07-30까지 통합 리포트를 생성합니다.
"""

import os
import json
from datetime import datetime, timedelta
from reports.integrated_report_generator import IntegratedReportGenerator
from reports.metadata_manager import ReportMetadataManager

class HistoricalReportGenerator:
    def __init__(self):
        self.integrated_generator = IntegratedReportGenerator()
        self.metadata_manager = ReportMetadataManager()
        
    def generate_sample_news_data(self, date_str, report_type):
        """샘플 뉴스 데이터 생성 (딕셔너리 형태)"""
        base_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # 날짜별 다양한 뉴스 데이터 (딕셔너리 형태로 반환)
        news_templates = {
            'exchange-rate': {
                'title': f'{date_str} 원/달러 환율 동향',
                'content': f'{base_date.strftime("%m월 %d일")} 서울 외환시장에서 원/달러 환율이 전일 대비 소폭 상승했습니다.',
                'sentiment': '안정',
                'keywords': ['환율', '달러', '외환시장'],
                'analysis': {
                    'market_impact': '보통',
                    'key_points': ['환율 안정세', '수출 기업 영향']
                },
                'published_time': base_date.strftime('%Y-%m-%d %H:%M:%S'),
                'source': '연합뉴스',
                'url': f'https://example.com/news/{date_str}-exchange'
            },
            'kospi-close': {
                'title': f'{date_str} KOSPI 마감 현황',
                'content': f'{base_date.strftime("%m월 %d일")} 코스피 지수가 외국인 매수세에 힘입어 상승 마감했습니다.',
                'sentiment': '상승',
                'keywords': ['KOSPI', '증시', '외국인'],
                'analysis': {
                    'market_impact': '높음',
                    'key_points': ['외국인 순매수', '기관 매도']
                },
                'published_time': base_date.strftime('%Y-%m-%d %H:%M:%S'),
                'source': '한국경제',
                'url': f'https://example.com/news/{date_str}-kospi'
            },
            'newyork-market-watch': {
                'title': f'{date_str} 뉴욕 증시 동향',
                'content': f'{base_date.strftime("%m월 %d일")} 뉴욕 증시가 기술주 중심으로 상승세를 보였습니다.',
                'sentiment': '상승',
                'keywords': ['뉴욕', '나스닥', '기술주'],
                'analysis': {
                    'market_impact': '높음',
                    'key_points': ['기술주 강세', 'Fed 정책 기대']
                },
                'published_time': base_date.strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'MarketWatch',
                'url': f'https://example.com/news/{date_str}-nyse'
            }
        }
        
        return news_templates.get(report_type, {})
    
    def generate_integrated_news_data(self, date_str):
        """통합 뉴스 데이터 생성"""
        all_news = []
        
        # 각 타입별 뉴스 수집
        for news_type in ['exchange-rate', 'kospi-close', 'newyork-market-watch']:
            news_data = self.generate_sample_news_data(date_str, news_type)
            all_news.extend(news_data)
        
        return all_news
    
    def generate_historical_reports(self, start_date='2025-07-25', end_date='2025-07-30'):
        """과거 날짜 통합 리포트 생성"""
        print(f"📅 {start_date}부터 {end_date}까지 통합 리포트 생성 시작...")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current_date = start
        generated_reports = []
        
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"\n📊 {date_str} 통합 리포트 생성 중...")
            
            # 통합 뉴스 데이터 생성
            integrated_news = self.generate_integrated_news_data(date_str)
            
            if integrated_news:
                # 통합 리포트 생성
                news_data_dict = {
                    'exchange-rate': self.generate_sample_news_data(date_str, 'exchange-rate'),
                    'kospi-close': self.generate_sample_news_data(date_str, 'kospi-close'),
                    'newyork-market-watch': self.generate_sample_news_data(date_str, 'newyork-market-watch')
                }
                
                report_info = self.integrated_generator.generate_integrated_report(news_data_dict)
                
                if report_info and not report_info.get('error'):
                    # 메타데이터에 추가
                    self.metadata_manager.add_report(
                        report_info['filename'],
                        report_info.get('local_path')
                    )
                    
                    generated_reports.append({
                        'date': date_str,
                        'filename': report_info['filename'],
                        'status': 'success'
                    })
                    
                    print(f"✅ {date_str} 리포트 생성 완료: {report_info['filename']}")
                else:
                    print(f"❌ {date_str} 리포트 생성 실패")
                    generated_reports.append({
                        'date': date_str,
                        'status': 'failed'
                    })
            
            current_date += timedelta(days=1)
        
        # 결과 요약
        print(f"\n📋 생성 결과 요약:")
        success_count = len([r for r in generated_reports if r['status'] == 'success'])
        total_count = len(generated_reports)
        
        print(f"✅ 성공: {success_count}/{total_count}")
        print(f"📁 생성된 리포트:")
        
        for report in generated_reports:
            if report['status'] == 'success':
                print(f"  - {report['date']}: {report['filename']}")
        
        return generated_reports
    
    def cleanup_old_individual_reports(self):
        """기존 개별 리포트 정리"""
        print("🧹 기존 개별 리포트 정리 중...")
        
        # reports_index.json 읽기 (상위 디렉토리)
        index_path = "../docs/reports_index.json"
        if not os.path.exists(index_path):
            print("❌ reports_index.json 파일을 찾을 수 없습니다.")
            return
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data['reports'])
        
        # 2025-07-25 이후의 개별 리포트 제거
        filtered_reports = []
        removed_files = []
        
        for report in data['reports']:
            # 테스트 리포트는 유지
            if report['id'].startswith('test_'):
                filtered_reports.append(report)
                continue
            
            # 2025-07-25 이후의 개별 exchange-rate 리포트 제거
            if (report['type'] == 'exchange-rate' and 
                report['date'] >= '2025-07-25' and
                'posco_analysis_exchange-rate' in report['id']):
                removed_files.append(report['filename'])
                continue
            
            # 나머지는 유지
            filtered_reports.append(report)
        
        # 업데이트된 데이터 저장
        data['reports'] = filtered_reports
        data['totalReports'] = len(filtered_reports)
        data['lastUpdate'] = datetime.now().isoformat() + 'Z'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        removed_count = original_count - len(filtered_reports)
        print(f"✅ {removed_count}개 개별 리포트 메타데이터 제거 완료")
        print(f"📊 남은 리포트: {len(filtered_reports)}개")
        
        # 실제 파일도 제거
        reports_dir = "../docs/reports"
        if os.path.exists(reports_dir):
            actual_removed = 0
            for filename in removed_files:
                file_path = os.path.join(reports_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    actual_removed += 1
            
            print(f"🗑️ {actual_removed}개 개별 리포트 파일 제거 완료")

def main():
    generator = HistoricalReportGenerator()
    
    # 1. 기존 개별 리포트 정리
    generator.cleanup_old_individual_reports()
    
    # 2. 새로운 통합 리포트 생성
    generator.generate_historical_reports('2025-07-25', '2025-07-30')
    
    print("\n🎉 과거 통합 리포트 생성 완료!")

if __name__ == "__main__":
    main()