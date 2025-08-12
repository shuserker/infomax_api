#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Completion Notifier
POSCO 알림 시스템

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# 설정 파일에서 웹훅 URL 가져오기
try:
# REMOVED:     from .git/config import DOORAY_WEBHOOK_URL, BOT_PROFILE_IMAGE_URL
except ImportError:
    DOORAY_WEBHOOK_URL = "https:/infomax.dooray.com/services/3262462484277387103/4121380745073081229/5FbudzTwTki4wCeBszBrAg"
    BOT_PROFILE_IMAGE_URL = "https:/raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/POSCO News 250808_mini/posco_logo_mini.jpg"

class CompletionNotifier:
    """
    작업 완료 알림 클래스
    """
    
    def __init__(self):
        """초기화"""
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 웹훅 설정
        self.webhook_url = DOORAY_WEBHOOK_URL
        self.bot_image_url = BOT_PROFILE_IMAGE_URL
    
    def send_completion_notification(self, results: Dict[str, Any]) -> bool:
        """
        작업 완료 알림 전송
        
        Args:
            results (Dict[str, Any]): 작업 결과 데이터
            
        Returns:
            bool: 알림 전송 성공 여부
        """
        try:
            # 요약 리포트 생성
            summary = self.generate_summary_report(results)
            
            # 대시보드 링크 생성 (결과 데이터 포함)
            dashboard_links = self.create_dashboard_links(results)
            
            # Dooray 메시지 포맷 생성
            message_payload = self.format_dooray_message(summary, dashboard_links)
            
            # 웹훅 전송
            response = requests.post(
                self.webhook_url, 
                json=message_payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("✅ 완료 알림 전송 성공!")
                return True
            else:
                self.logger.error(f"❌ 알림 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 알림 전송 중 오류: {e}")
            return False
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """
        결과 요약 리포트 생성
        
        Args:
            results (Dict[str, Any]): 작업 결과 데이터
            
        Returns:
            str: 요약 리포트 텍스트
        """
        # 기본 정보 추출
        cleanup_results = results.get('cleanup_results', {})
        generation_results = results.get('generation_results', [])
        metadata_results = results.get('metadata_results', {})
        
        # 성공한 리포트 생성 개수
        successful_reports = [r for r in generation_results if r.get('status') == 'success']
        
        # 제거된 파일 개수
        removed_files = cleanup_results.get('total_removed_files', 0)
        
        # 생성된 리포트 개수
        generated_reports = len(successful_reports)
        
        # 성공률 계산
        total_attempts = len(generation_results)
        success_rate = (generated_reports / total_attempts * 100) if total_attempts > 0 else 0
        
        # 처리 시간 계산
        processing_time = results.get('processing_time', 0)
        
        summary = f"""
🔄 POSCO 리포트 시스템 완전 재구축 완료

📋 작업 완료 내용:
✅ 기존 리포트 완전 제거: {removed_files}개
✅ 새로운 통합 리포트 생성: {generated_reports}개
✅ 메타데이터 시스템 초기화 및 재구성
✅ 개별 리포트 시스템 → 통합 리포트 시스템 전환

📊 시스템 전환 결과:
- 🎯 성공률: {success_rate:.1f}% ({generated_reports}/{total_attempts})
- ⏱️ 처리 시간: {processing_time:.1f}초
- 📅 생성 기간: 2025-07-25 ~ {datetime.now().strftime('%Y-%m-%d')}

🆕 새로운 시스템 특징:
- 🔗 통합 리포트만 생성 (개별 리포트 완전 비활성화)
- 📈 3개 뉴스 타입 통합 분석 (환율/증시/뉴욕)
- 🎨 요일별 현실적인 시장 시나리오 적용
- 📱 개선된 메타데이터 관리 시스템
        """.strip()
        
        # 생성된 리포트 목록 추가
        if successful_reports:
summary_+ =  "/n/n🗓️ 생성된 통합 리포트:"
            for report in successful_reports[:5]:  # 최대 5개만 표시
                date = report.get('date', 'Unknown')
                day = report.get('day', 'Unknown')
                scenario = report.get('scenario', 'Unknown')
summary_+ =  f"/n- 📅 {date} ({day}): {scenario}"
            
            if len(successful_reports) > 5:
summary_+ =  f"/n- ... 외 {len(successful_reports) - 5}개 더"
        
        # 오류 정보 추가
        failed_reports = [r for r in generation_results if r.get('status') == 'failed']
        if failed_reports:
summary_+ =  f"/n/n⚠️ 주의사항: {len(failed_reports)}개 리포트 생성 실패"
        
summary_+ =  f"/n/n⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary
    
    def create_dashboard_links(self, results: Dict[str, Any] = None) -> Dict[str, str]:
        """
        대시보드 링크 생성
        
        Args:
            results: 작업 결과 데이터 (최신 리포트 링크 생성용)
            
        Returns:
            Dict[str, str]: 링크 정보
        """
        base_url = "https:/shuserker.github.io/infomax_api"
        
        # 최신 리포트 링크 생성 - 기본값은 메인 대시보드
        latest_report_url = f"{base_url}/"
        
        if results and results.get('generation_results'):
            successful_reports = [r for r in results['generation_results'] if r.get('status') == 'success']
            if successful_reports:
                latest_report = successful_reports[-1]  # 가장 최근 리포트
                if latest_report.get('filename'):
                    latest_report_url = f"{base_url}/reports/{latest_report['filename']}"
        else:
            # 실제 파일 시스템에서 최신 통합 리포트 찾기
            import posco_news_250808_monitor.log
            import glob
            
            # docs/reports 디렉토리에서 통합 리포트 찾기
            docs_reports_path = "deployment_verification_checklist.md"
            monitoring_reports_path = "Monitoring/POSCO News 250808_mini/reports/posco_integrated_analysis_*.html"
            
            latest_file = None
            
            # docs/reports에서 먼저 찾기
            if os.path.exists("docs/reports"):
                docs_files = glob.glob(docs_reports_path)
                if docs_files:
                    latest_file = max(docs_files, key=os.path.getctime)
            
            # docs에 없으면 monitoring에서 찾기
            if not latest_file:
                monitoring_files = glob.glob(monitoring_reports_path)
                if monitoring_files:
                    latest_file = max(monitoring_files, key=os.path.getctime)
                    # monitoring 파일이면 docs로 복사
                    if latest_file:
                        import shutil
                        filename = os.path.basename(latest_file)
                        dest_path = f"docs/reports/{filename}"
                        try:
os.makedirs("docs/reports",_exist_ok = True)
                            shutil.copy2(latest_file, dest_path)
                            latest_file = dest_path
                        except Exception as e:
                            self.logger.warning(f"파일 복사 실패: {e}")
            
            if latest_file:
                filename = os.path.basename(latest_file)
                latest_report_url = f"{base_url}/reports/{filename}"
        
        return {
            'dashboard': f"{base_url}/",
            'reports_api': f"docs/reports_index.json",
            'latest_report': latest_report_url
        }
    
    def format_dooray_message(self, summary: str, dashboard_links: Dict[str, str]) -> Dict[str, Any]:
        """
        Dooray 메시지 포맷 생성
        
        Args:
            summary (str): 요약 리포트
            dashboard_links (Dict[str, str]): 대시보드 링크들
            
        Returns:
            Dict[str, Any]: Dooray 웹훅 페이로드
        """
        # 타이틀에 최신 리포트 직접 링크 포함
        title = f"🎉 POSCO 리포트 시스템 완전 재구축 완료 | [📊 상세 보기]({dashboard_links['latest_report']})"
        
        payload = {
            "botName": "POSCO 시스템 🔄",
            "botIconImage": self.bot_image_url,
            "text": title,
            "mrkdwn": True,
            "attachments": [
                {
                    "color": "#28a745",  # 성공 색상 (녹색)
                    "text": summary,
                    "mrkdwn_in": ["text"]
                }
            ]
        }
        
        return payload
    
    def send_error_notification(self, error_info: Dict[str, Any]) -> bool:
        """
        오류 알림 전송
        
        Args:
            error_info (Dict[str, Any]): 오류 정보
            
        Returns:
            bool: 알림 전송 성공 여부
        """
        try:
            title = "❌ POSCO 리포트 시스템 재구축 실패"
            
            error_message = f"""
🚨 POSCO 리포트 시스템 재구축 중 오류 발생

❌ 오류 정보:
- 오류 단계: {error_info.get('stage', 'Unknown')}
- 오류 메시지: {error_info.get('error', 'Unknown error')}
- 발생 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 권장 조치:
1. 로그 파일 확인
2. 시스템 상태 점검
3. 수동 복구 고려

⚠️ 시스템 관리자의 확인이 필요합니다.
            """.strip()
            
            payload = {
                "botName": "POSCO 시스템 ⚠️",
                "botIconImage": self.bot_image_url,
                "text": title,
                "mrkdwn": True,
                "attachments": [
                    {
                        "color": "#dc3545",  # 오류 색상 (빨간색)
                        "text": error_message,
                        "mrkdwn_in": ["text"]
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("✅ 오류 알림 전송 성공!")
                return True
            else:
                self.logger.error(f"❌ 오류 알림 전송 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 오류 알림 전송 중 오류: {e}")
            return False
    
    def send_progress_notification(self, stage: str, progress: Dict[str, Any]) -> bool:
        """
        진행 상황 알림 전송
        
        Args:
            stage (str): 현재 단계
            progress (Dict[str, Any]): 진행 상황 정보
            
        Returns:
            bool: 알림 전송 성공 여부
        """
        try:
            stage_names = {
                'cleanup': '🧹 기존 리포트 제거',
                'generation': '📊 통합 리포트 생성',
                'metadata': '📋 메타데이터 업데이트',
                'notification': '📱 완료 알림 준비'
            }
            
            stage_name = stage_names.get(stage, stage)
            
            title = f"🔄 POSCO 리포트 시스템 재구축 진행 중 - {stage_name}"
            
            progress_message = f"""
⏳ 현재 진행 상황: {stage_name}

📊 진행률: {progress.get('percentage', 0):.1f}%
⏱️ 경과 시간: {progress.get('elapsed_time', 0):.1f}초
📝 현재 작업: {progress.get('current_task', 'Processing...')}

{progress.get('details', '')}
            """.strip()
            
            payload = {
                "botName": "POSCO 시스템 ⏳",
                "botIconImage": self.bot_image_url,
                "text": title,
                "mrkdwn": True,
                "attachments": [
                    {
                        "color": "#007bff",  # 진행 색상 (파란색)
                        "text": progress_message,
                        "mrkdwn_in": ["text"]
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                timeout=10
            )
            
return_response.status_code = = 200
            
        except Exception as e:
            self.logger.error(f"❌ 진행 알림 전송 중 오류: {e}")
            return False

def main():
    """테스트 실행 함수"""
    notifier = CompletionNotifier()
    
    # 테스트 결과 데이터
    test_results = {
        'cleanup_results': {
            'total_removed_files': 88,
            'docs_reports_removed': 16,
            'monitoring_reports_removed': 71,
            'root_reports_removed': 1
        },
        'generation_results': [
            {'date': '2025-07-25', 'day': 'Friday', 'status': 'success', 'scenario': '주말 앞 상승'},
            {'date': '2025-07-26', 'day': 'Saturday', 'status': 'success', 'scenario': '주말 안정'},
            {'date': '2025-07-27', 'day': 'Sunday', 'status': 'success', 'scenario': '주말 마감'},
            {'date': '2025-07-28', 'day': 'Monday', 'status': 'success', 'scenario': '주초 상승세'},
            {'date': '2025-07-29', 'day': 'Tuesday', 'status': 'success', 'scenario': '조정 국면'},
            {'date': '2025-07-30', 'day': 'Wednesday', 'status': 'success', 'scenario': '중간 조정'},
            {'date': '2025-07-31', 'day': 'Thursday', 'status': 'success', 'scenario': '회복 신호'},
            {'date': '2025-08-01', 'day': 'Friday', 'status': 'success', 'scenario': '주말 앞 상승'},
            {'date': '2025-08-02', 'day': 'Saturday', 'status': 'success', 'scenario': '주말 안정'},
            {'date': '2025-08-03', 'day': 'Sunday', 'status': 'success', 'scenario': '주말 마감'}
        ],
        'metadata_results': {
            'reset_success': True,
            'registered_reports': 10
        },
        'processing_time': 45.7
    }
    
    # 완료 알림 전송
    success = notifier.send_completion_notification(test_results)
    
    if success:
        print("✅ 테스트 알림 전송 성공!")
    else:
        print("❌ 테스트 알림 전송 실패!")
    
    return success

if __name__ == "__main__":
    main()