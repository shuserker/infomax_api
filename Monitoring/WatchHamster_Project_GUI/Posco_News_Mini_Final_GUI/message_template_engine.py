#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 메시지 템플릿 엔진 (스탠드얼론)
실제 포스코 뉴스 형태의 메시지 템플릿 시스템

주요 기능:
- 📰 포스코 뉴스 스타일 메시지 템플릿
- 🎨 고객 친화적 메시지 형식 변환
- 📊 동적 데이터 기반 메시지 생성
- 👀 GUI 메시지 미리보기 지원

Requirements: 2.1, 2.3 구현
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

try:
    from .dynamic_data_manager import DynamicDataManager, MarketData
except ImportError:
    from dynamic_data_manager import DynamicDataManager, MarketData


class MessageType(Enum):
    """메시지 타입 정의"""
    DEPLOYMENT_SUCCESS = "deployment_success"
    DEPLOYMENT_FAILURE = "deployment_failure"
    DEPLOYMENT_START = "deployment_start"
    SYSTEM_STATUS = "system_status"
    DATA_UPDATE = "data_update"
    ERROR_ALERT = "error_alert"
    MAINTENANCE = "maintenance"


class MessagePriority(Enum):
    """메시지 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageTemplateEngine:
    """POSCO 메시지 템플릿 엔진 클래스"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """메시지 템플릿 엔진 초기화"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = config_dir or os.path.join(self.script_dir, "../config")
        
        # 템플릿 설정 파일
        self.template_config_file = os.path.join(self.config_dir, "message_templates.json")
        
        # 동적 데이터 관리자 초기화
        self.data_manager = DynamicDataManager(os.path.join(self.script_dir, "../data"))
        
        # 기본 템플릿 로드
        self.templates = self._load_default_templates()
        
        # 사용자 정의 템플릿 로드 (있는 경우)
        self._load_custom_templates()
        
        # POSCO 브랜딩 설정
        self.brand_config = {
            "company_name": "POSCO",
            "system_name": "POSCO 통합 분석 시스템",
            "brand_emoji": "🏭",
            "success_emoji": "✅",
            "warning_emoji": "⚠️",
            "error_emoji": "❌",
            "info_emoji": "ℹ️",
            "chart_emoji": "📊",
            "web_emoji": "🌐",
            "time_emoji": "⏰"
        }
        
        print(f"🎨 POSCO 메시지 템플릿 엔진 초기화 완료 (동적 데이터 연동)")
    
    def _load_default_templates(self) -> Dict[str, Dict]:
        """기본 메시지 템플릿 로드"""
        return {
            MessageType.DEPLOYMENT_SUCCESS.value: {
                "title": "{brand_emoji} {company_name} 분석 리포트 업데이트 완료",
                "body": """
{success_emoji} **배포 성공 알림**

**{system_name}**에서 최신 분석 리포트가 성공적으로 업데이트되었습니다.

{chart_emoji} **업데이트 정보**
• 배포 ID: `{deployment_id}`
• 완료 시간: {completion_time}
• 처리 단계: {steps_completed}단계 완료
• 소요 시간: {duration}

{web_emoji} **접속 정보**
• 리포트 URL: {report_url}
• 상태: {status_message}

{info_emoji} **주요 내용**
{content_summary}

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                "priority": MessagePriority.NORMAL.value,
                "color": "#28a745"  # 성공 색상 (녹색)
            },
            
            MessageType.DEPLOYMENT_FAILURE.value: {
                "title": "{brand_emoji} {company_name} 시스템 배포 실패 알림",
                "body": """
{error_emoji} **배포 실패 알림**

**{system_name}**에서 리포트 배포 중 문제가 발생했습니다.

{chart_emoji} **실패 정보**
• 배포 ID: `{deployment_id}`
• 실패 시간: {failure_time}
• 오류 단계: {failed_step}
• 롤백 상태: {rollback_status}

{warning_emoji} **오류 내용**
```
{error_message}
```

{info_emoji} **조치 사항**
• 시스템 관리자가 자동으로 알림을 받았습니다
• 문제 해결 후 자동으로 재배포됩니다
• 긴급한 경우 시스템 관리자에게 연락하세요

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                "priority": MessagePriority.HIGH.value,
                "color": "#dc3545"  # 실패 색상 (빨간색)
            },
            
            MessageType.DEPLOYMENT_START.value: {
                "title": "{brand_emoji} {company_name} 분석 리포트 업데이트 시작",
                "body": """
{info_emoji} **배포 시작 알림**

**{system_name}**에서 새로운 분석 리포트 업데이트를 시작합니다.

{chart_emoji} **배포 정보**
• 배포 ID: `{deployment_id}`
• 시작 시간: {start_time}
• 예상 소요 시간: 약 {estimated_duration}분

{time_emoji} **진행 상황**
업데이트가 완료되면 자동으로 알림을 보내드립니다.

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                "priority": MessagePriority.LOW.value,
                "color": "#17a2b8"  # 정보 색상 (파란색)
            },
            
            MessageType.SYSTEM_STATUS.value: {
                "title": "{brand_emoji} {company_name} 시스템 상태 리포트",
                "body": """
{info_emoji} **시스템 상태 리포트**

**{system_name}** 운영 상태를 알려드립니다.

{chart_emoji} **운영 통계**
• 총 배포 횟수: {total_deployments}회
• 성공률: {success_rate}%
• 마지막 성공: {last_success}
• 평균 배포 시간: {avg_deployment_time}분

{web_emoji} **서비스 상태**
• GitHub Pages: {github_status}
• 데이터 수집: {data_collection_status}
• 웹훅 서비스: {webhook_status}

{time_emoji} **다음 업데이트**
예정 시간: {next_update_time}

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                "priority": MessagePriority.LOW.value,
                "color": "#6c757d"  # 중성 색상 (회색)
            },
            
            MessageType.DATA_UPDATE.value: {
                "title": "{brand_emoji} {company_name} 데이터 업데이트 알림 ({data_freshness})",
                "body": """
{chart_emoji} **실시간 시장 데이터 업데이트**

**{system_name}**에서 최신 시장 데이터가 업데이트되었습니다.

{info_emoji} **주요 지표 현황**
• **KOSPI 지수**: {kospi} ({kospi_change_percent}) - {kospi_trend}
• **환율 (USD/KRW)**: {exchange_rate} ({exchange_change_percent}) - {exchange_trend}  
• **POSCO 주가**: {posco_stock} ({posco_change_percent}) - {posco_trend}
• **시장 감정**: {news_sentiment} (뉴스 {news_count}건 분석)

{chart_emoji} **시장 분석 요약**
{market_summary}

{time_emoji} **데이터 품질 정보**
• 전체 신뢰도: {data_reliability} ({overall_quality:.1%})
• 데이터 신선도: {data_freshness}
• 신뢰도 지표: {reliability_indicator}

{quality_warning}

{web_emoji} **상세 분석**
전체 분석 리포트는 {report_url}에서 확인하실 수 있습니다.

---
*본 메시지는 {system_name}에서 실시간 데이터를 기반으로 자동 생성되었습니다.*
""",
                "priority": MessagePriority.NORMAL.value,
                "color": "#007bff"  # 데이터 색상 (파란색)
            },
            
            MessageType.ERROR_ALERT.value: {
                "title": "{brand_emoji} {company_name} 시스템 오류 알림",
                "body": """
{error_emoji} **시스템 오류 알림**

**{system_name}**에서 오류가 감지되었습니다.

{warning_emoji} **오류 정보**
• 발생 시간: {error_time}
• 오류 유형: {error_type}
• 영향 범위: {impact_scope}

{info_emoji} **오류 내용**
```
{error_details}
```

{time_emoji} **조치 상황**
• 자동 복구 시도: {auto_recovery_status}
• 관리자 알림: 전송 완료
• 예상 복구 시간: {estimated_recovery_time}

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                "priority": MessagePriority.CRITICAL.value,
                "color": "#dc3545"  # 오류 색상 (빨간색)
            },
            
            MessageType.MAINTENANCE.value: {
                "title": "{brand_emoji} {company_name} 시스템 점검 안내",
                "body": """
{warning_emoji} **시스템 점검 안내**

**{system_name}** 정기 점검을 실시합니다.

{time_emoji} **점검 일정**
• 시작 시간: {maintenance_start}
• 종료 시간: {maintenance_end}
• 예상 소요 시간: {maintenance_duration}

{info_emoji} **점검 내용**
{maintenance_details}

{chart_emoji} **서비스 영향**
• 리포트 업데이트: 일시 중단
• 기존 리포트 조회: 정상 서비스
• 데이터 수집: 백그라운드 진행

점검 완료 후 자동으로 서비스가 재개됩니다.

---
*본 메시지는 {system_name}에서 자동 생성되었습니다.*
""",
                "priority": MessagePriority.NORMAL.value,
                "color": "#ffc107"  # 주의 색상 (노란색)
            }
        }
    
    def _load_custom_templates(self):
        """사용자 정의 템플릿 로드"""
        try:
            if os.path.exists(self.template_config_file):
                with open(self.template_config_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                    
                # 기본 템플릿과 병합
                for template_type, template_data in custom_templates.items():
                    if template_type in self.templates:
                        self.templates[template_type].update(template_data)
                    else:
                        self.templates[template_type] = template_data
                
                print(f"✅ 사용자 정의 템플릿 로드 완료: {len(custom_templates)}개")
        except Exception as e:
            print(f"⚠️ 사용자 정의 템플릿 로드 실패: {e}")
    
    def save_custom_templates(self, templates: Dict[str, Dict]):
        """사용자 정의 템플릿 저장"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.template_config_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            print(f"✅ 사용자 정의 템플릿 저장 완료")
        except Exception as e:
            print(f"❌ 사용자 정의 템플릿 저장 실패: {e}")
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """템플릿 렌더링 (테스트용)"""
        try:
            if template_name in self.templates:
                template = self.templates[template_name]
                if 'body' in template:
                    return template['body'].format(**data)
            return f"템플릿 '{template_name}' 렌더링 완료"
        except Exception as e:
            return f"템플릿 렌더링 오류: {e}"
    
    def generate_message(self, message_type: MessageType, data: Dict[str, Any]) -> Dict[str, str]:
        """메시지 생성"""
        try:
            template = self.templates.get(message_type.value)
            if not template:
                raise ValueError(f"템플릿을 찾을 수 없습니다: {message_type.value}")
            
            # 브랜딩 정보와 데이터 병합
            format_data = {**self.brand_config, **data}
            
            # 기본값 설정
            format_data.setdefault('completion_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            format_data.setdefault('system_name', self.brand_config['system_name'])
            
            # 제목과 본문 포맷팅
            title = template['title'].format(**format_data)
            body = template['body'].format(**format_data)
            
            return {
                'title': title,
                'body': body.strip(),
                'priority': template.get('priority', MessagePriority.NORMAL.value),
                'color': template.get('color', '#6c757d'),
                'message_type': message_type.value,
                'timestamp': datetime.now().isoformat()
            }
            
        except KeyError as e:
            error_msg = f"템플릿 변수 누락: {e}"
            print(f"❌ {error_msg}")
            return self._generate_error_message(error_msg, data)
        except Exception as e:
            error_msg = f"메시지 생성 실패: {str(e)}"
            print(f"❌ {error_msg}")
            return self._generate_error_message(error_msg, data)
    
    def _generate_error_message(self, error: str, data: Dict[str, Any]) -> Dict[str, str]:
        """오류 발생 시 기본 메시지 생성"""
        return {
            'title': f"{self.brand_config['error_emoji']} 메시지 생성 오류",
            'body': f"메시지 템플릿 처리 중 오류가 발생했습니다.\n\n오류 내용: {error}\n\n원본 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}",
            'priority': MessagePriority.HIGH.value,
            'color': '#dc3545',
            'message_type': 'error',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_deployment_success_message(self, deployment_result: Dict[str, Any], 
                                          include_market_data: bool = True) -> Dict[str, str]:
        """배포 성공 메시지 생성 (동적 데이터 포함 옵션)"""
        # 배포 결과에서 필요한 정보 추출
        deployment_id = deployment_result.get('deployment_id', 'Unknown')
        steps_completed = len(deployment_result.get('steps_completed', []))
        
        # 소요 시간 계산
        start_time = deployment_result.get('start_time')
        end_time = deployment_result.get('end_time')
        duration = "계산 불가"
        
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration_seconds = (end_dt - start_dt).total_seconds()
                duration = f"{duration_seconds:.1f}초"
            except:
                duration = "계산 불가"
        
        # GitHub Pages 상태
        github_accessible = deployment_result.get('github_pages_accessible', False)
        status_message = "정상 접근 가능" if github_accessible else "접근 확인 중"
        
        # 콘텐츠 요약 생성
        content_summary = self._generate_content_summary(deployment_result)
        
        # 기본 배포 데이터
        data = {
            'deployment_id': deployment_id,
            'steps_completed': steps_completed,
            'duration': duration,
            'report_url': 'https://shuserker.github.io/infomax_api',
            'status_message': status_message,
            'content_summary': content_summary
        }
        
        # 동적 시장 데이터 포함 (옵션)
        if include_market_data:
            try:
                print("📊 배포 성공 메시지에 동적 시장 데이터 포함...")
                market_data = self.data_manager.get_market_data()
                dynamic_data = self.data_manager.generate_dynamic_message_data(market_data)
                
                # 시장 데이터를 배포 메시지에 추가
                data.update({
                    'market_summary': dynamic_data.get('market_summary', '시장 데이터 없음'),
                    'data_quality': dynamic_data.get('data_reliability', '알 수 없음'),
                    'kospi_current': dynamic_data.get('kospi', 'N/A'),
                    'posco_current': dynamic_data.get('posco_stock', 'N/A')
                })
                
                # 배포 성공 메시지에 시장 현황 추가
                enhanced_content = f"{content_summary}\n\n📊 **현재 시장 현황**\n{dynamic_data.get('market_summary', '시장 데이터 없음')}"
                data['content_summary'] = enhanced_content
                
                print("✅ 동적 시장 데이터가 배포 메시지에 포함됨")
                
            except Exception as e:
                print(f"⚠️ 배포 메시지에 시장 데이터 포함 실패: {e}")
                # 실패해도 기본 배포 메시지는 생성
        
        return self.generate_message(MessageType.DEPLOYMENT_SUCCESS, data)
    
    def generate_deployment_failure_message(self, deployment_result: Dict[str, Any]) -> Dict[str, str]:
        """배포 실패 메시지 생성"""
        deployment_id = deployment_result.get('deployment_id', 'Unknown')
        error_message = deployment_result.get('error_message', '알 수 없는 오류')
        rollback_performed = deployment_result.get('rollback_performed', False)
        failed_step = self._identify_failed_step(deployment_result)
        
        data = {
            'deployment_id': deployment_id,
            'failure_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'failed_step': failed_step,
            'rollback_status': '완료' if rollback_performed else '미실행',
            'error_message': error_message
        }
        
        return self.generate_message(MessageType.DEPLOYMENT_FAILURE, data)
    
    def generate_deployment_start_message(self, deployment_id: str) -> Dict[str, str]:
        """배포 시작 메시지 생성"""
        data = {
            'deployment_id': deployment_id,
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estimated_duration': '2-3'
        }
        
        return self.generate_message(MessageType.DEPLOYMENT_START, data)
    
    def generate_data_update_message(self, market_data: Optional[Dict[str, Any]] = None, 
                                   use_dynamic_data: bool = True) -> Dict[str, str]:
        """데이터 업데이트 메시지 생성 (동적 데이터 기반)"""
        try:
            if use_dynamic_data:
                # 동적 데이터 관리자에서 최신 시장 데이터 수집
                print("📊 동적 시장 데이터 수집 중...")
                dynamic_market_data = self.data_manager.get_market_data()
                message_data = self.data_manager.generate_dynamic_message_data(dynamic_market_data)
                
                # 추가 필드 설정
                message_data.update({
                    'report_url': 'https://shuserker.github.io/infomax_api',
                    'overall_quality': dynamic_market_data.overall_quality
                })
                
                print(f"✅ 동적 데이터 기반 메시지 생성 (품질: {dynamic_market_data.overall_quality:.1%})")
                
            else:
                # 기존 방식 (하드코딩된 데이터 사용)
                print("⚠️ 정적 데이터 기반 메시지 생성")
                if not market_data:
                    market_data = {}
                
                # 시장 데이터 포맷팅 (기존 방식)
                kospi_value = market_data.get('kospi', 'N/A')
                kospi_change = self._format_change(market_data.get('kospi_change'))
                
                exchange_rate = market_data.get('exchange_rate', 'N/A')
                exchange_change = self._format_change(market_data.get('exchange_change'))
                
                posco_stock = market_data.get('posco_stock', 'N/A')
                posco_change = self._format_change(market_data.get('posco_change'))
                
                message_data = {
                    'kospi': kospi_value,
                    'kospi_change': kospi_change,
                    'kospi_change_percent': 'N/A',
                    'kospi_trend': '데이터 없음',
                    'exchange_rate': exchange_rate,
                    'exchange_change': exchange_change,
                    'exchange_change_percent': 'N/A',
                    'exchange_trend': '데이터 없음',
                    'posco_stock': posco_stock,
                    'posco_change': posco_change,
                    'posco_change_percent': 'N/A',
                    'posco_trend': '데이터 없음',
                    'news_sentiment': '중립',
                    'news_count': 0,
                    'market_summary': '시장 데이터가 제한적입니다.',
                    'data_reliability': '낮음',
                    'data_freshness': '알 수 없음',
                    'reliability_indicator': '🔴 신뢰도 낮음',
                    'quality_warning': '⚠️ 정적 데이터를 사용하고 있습니다.',
                    'overall_quality': 0.3,
                    'timestamp': market_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'report_url': 'https://shuserker.github.io/infomax_api'
                }
            
            return self.generate_message(MessageType.DATA_UPDATE, message_data)
            
        except Exception as e:
            print(f"❌ 데이터 업데이트 메시지 생성 실패: {e}")
            # 오류 시 기본 메시지 반환
            error_data = {
                'kospi': 'N/A',
                'kospi_change_percent': 'N/A',
                'kospi_trend': '데이터 오류',
                'exchange_rate': 'N/A',
                'exchange_change_percent': 'N/A',
                'exchange_trend': '데이터 오류',
                'posco_stock': 'N/A',
                'posco_change_percent': 'N/A',
                'posco_trend': '데이터 오류',
                'news_sentiment': '알 수 없음',
                'news_count': 0,
                'market_summary': '데이터 수집 중 오류가 발생했습니다.',
                'data_reliability': '매우 낮음',
                'data_freshness': '오류',
                'reliability_indicator': '🔴 데이터 오류',
                'quality_warning': f'❌ 데이터 수집 오류: {str(e)}',
                'overall_quality': 0.0,
                'report_url': 'https://shuserker.github.io/infomax_api'
            }
            return self.generate_message(MessageType.DATA_UPDATE, error_data)
    
    def generate_system_status_message(self, status_data: Dict[str, Any]) -> Dict[str, str]:
        """시스템 상태 메시지 생성"""
        data = {
            'total_deployments': status_data.get('total_deployments', 0),
            'success_rate': status_data.get('success_rate', 0),
            'last_success': status_data.get('last_success', 'N/A'),
            'avg_deployment_time': status_data.get('avg_deployment_time', 'N/A'),
            'github_status': '정상' if status_data.get('github_accessible', True) else '점검 중',
            'data_collection_status': '정상' if status_data.get('data_collection_active', True) else '중단',
            'webhook_status': '정상' if status_data.get('webhook_active', True) else '오류',
            'next_update_time': status_data.get('next_update', '미정')
        }
        
        return self.generate_message(MessageType.SYSTEM_STATUS, data)
    
    def _generate_content_summary(self, deployment_result: Dict[str, Any]) -> str:
        """배포 콘텐츠 요약 생성"""
        steps = deployment_result.get('steps_completed', [])
        
        summary_items = []
        if 'status_check' in steps:
            summary_items.append("• Git 저장소 상태 확인 완료")
        if 'backup_creation' in steps:
            summary_items.append("• 안전 백업 생성 완료")
        if 'branch_switch' in steps:
            summary_items.append("• 배포 브랜치 전환 완료")
        if 'merge_main' in steps:
            summary_items.append("• 최신 변경사항 병합 완료")
        if 'commit_changes' in steps:
            summary_items.append("• 변경사항 커밋 완료")
        if 'push_remote' in steps:
            summary_items.append("• 원격 저장소 업로드 완료")
        if 'pages_verification' in steps:
            summary_items.append("• GitHub Pages 접근성 확인 완료")
        
        if not summary_items:
            return "• 기본 배포 프로세스 완료"
        
        return "\n".join(summary_items)
    
    def _identify_failed_step(self, deployment_result: Dict[str, Any]) -> str:
        """실패한 단계 식별"""
        steps_completed = deployment_result.get('steps_completed', [])
        
        step_names = {
            'status_check': 'Git 상태 확인',
            'backup_creation': '백업 생성',
            'branch_switch': '브랜치 전환',
            'merge_main': '변경사항 병합',
            'commit_changes': '변경사항 커밋',
            'push_remote': '원격 저장소 푸시',
            'pages_verification': 'GitHub Pages 확인',
            'branch_return': '원래 브랜치 복귀'
        }
        
        all_steps = list(step_names.keys())
        
        for i, step in enumerate(all_steps):
            if step not in steps_completed:
                return step_names.get(step, f"단계 {i+1}")
        
        return "알 수 없는 단계"
    
    def _format_change(self, change_value: Any) -> str:
        """변화량 포맷팅"""
        if change_value is None:
            return "변화 없음"
        
        try:
            change = float(change_value)
            if change > 0:
                return f"▲ +{change:.2f}"
            elif change < 0:
                return f"▼ {change:.2f}"
            else:
                return "→ 0.00"
        except (ValueError, TypeError):
            return str(change_value) if change_value else "N/A"
    
    def preview_message(self, message_type: MessageType, data: Dict[str, Any]) -> str:
        """메시지 미리보기 생성 (GUI용)"""
        try:
            # 메시지 타입에 따라 적절한 메서드 사용
            if message_type == MessageType.DEPLOYMENT_SUCCESS:
                message = self.generate_deployment_success_message(data)
            elif message_type == MessageType.DEPLOYMENT_FAILURE:
                message = self.generate_deployment_failure_message(data)
            elif message_type == MessageType.DEPLOYMENT_START:
                deployment_id = data.get('deployment_id', 'preview_test')
                message = self.generate_deployment_start_message(deployment_id)
            elif message_type == MessageType.DATA_UPDATE:
                message = self.generate_data_update_message(data)
            elif message_type == MessageType.SYSTEM_STATUS:
                message = self.generate_system_status_message(data)
            else:
                # 기타 메시지 타입은 일반 메서드 사용
                message = self.generate_message(message_type, data)
            
            preview = f"""
=== 메시지 미리보기 ===
제목: {message['title']}
우선순위: {message['priority']}
색상: {message['color']}
생성 시간: {message['timestamp']}

--- 메시지 내용 ---
{message['body']}

=== 미리보기 끝 ===
"""
            return preview.strip()
            
        except Exception as e:
            return f"❌ 미리보기 생성 실패: {str(e)}"
    
    def get_available_templates(self) -> List[str]:
        """사용 가능한 템플릿 목록 반환"""
        return list(self.templates.keys())
    
    def get_template_info(self, message_type: MessageType) -> Dict[str, Any]:
        """템플릿 정보 반환"""
        template = self.templates.get(message_type.value, {})
        return {
            'type': message_type.value,
            'priority': template.get('priority', MessagePriority.NORMAL.value),
            'color': template.get('color', '#6c757d'),
            'has_title': 'title' in template,
            'has_body': 'body' in template,
            'required_fields': self._extract_required_fields(template)
        }
    
    def _extract_required_fields(self, template: Dict[str, str]) -> List[str]:
        """템플릿에서 필수 필드 추출"""
        import re
        
        required_fields = set()
        
        for content in [template.get('title', ''), template.get('body', '')]:
            # {field_name} 패턴 찾기
            fields = re.findall(r'\{([^}]+)\}', content)
            required_fields.update(fields)
        
        # 브랜딩 필드 제외
        brand_fields = set(self.brand_config.keys())
        required_fields = required_fields - brand_fields
        
        return sorted(list(required_fields))
    
    def generate_enhanced_dynamic_message(self, message_type: MessageType, 
                                        custom_data: Optional[Dict[str, Any]] = None,
                                        force_refresh: bool = False) -> Dict[str, str]:
        """향상된 동적 메시지 생성 (완전 실시간 데이터 기반)"""
        try:
            print(f"🚀 향상된 동적 메시지 생성 시작 (타입: {message_type.value})")
            
            # 최신 시장 데이터 수집
            market_data = self.data_manager.get_market_data(force_refresh=force_refresh)
            dynamic_data = self.data_manager.generate_dynamic_message_data(market_data)
            
            # 사용자 정의 데이터와 병합
            if custom_data:
                dynamic_data.update(custom_data)
            
            # 메시지 타입별 특별 처리
            if message_type == MessageType.DATA_UPDATE:
                # 데이터 업데이트 메시지는 항상 최신 데이터 사용
                return self.generate_data_update_message(use_dynamic_data=True)
                
            elif message_type == MessageType.DEPLOYMENT_SUCCESS:
                # 배포 성공 메시지에 시장 현황 포함
                deployment_data = custom_data or {}
                return self.generate_deployment_success_message(deployment_data, include_market_data=True)
                
            elif message_type == MessageType.SYSTEM_STATUS:
                # 시스템 상태에 데이터 품질 정보 포함
                quality_stats = self.data_manager.get_quality_statistics()
                
                status_data = {
                    'total_deployments': custom_data.get('total_deployments', 0) if custom_data else 0,
                    'success_rate': custom_data.get('success_rate', 95.0) if custom_data else 95.0,
                    'last_success': custom_data.get('last_success', 'N/A') if custom_data else 'N/A',
                    'avg_deployment_time': custom_data.get('avg_deployment_time', '2.5') if custom_data else '2.5',
                    'github_accessible': True,
                    'data_collection_active': market_data.overall_quality > 0.5,
                    'webhook_active': True,
                    'next_update': '다음 정시',
                    'data_quality_avg': quality_stats.get('average_quality', 0.0),
                    'data_quality_trend': quality_stats.get('quality_trend', '알 수 없음'),
                    'market_summary': dynamic_data.get('market_summary', '시장 데이터 없음')
                }
                
                # 시스템 상태 메시지에 데이터 품질 정보 추가
                enhanced_data = {**dynamic_data, **status_data}
                return self.generate_system_status_message(enhanced_data)
                
            else:
                # 기타 메시지 타입은 일반 생성 + 동적 데이터
                return self.generate_message(message_type, dynamic_data)
            
        except Exception as e:
            print(f"❌ 향상된 동적 메시지 생성 실패: {e}")
            # 오류 시 기본 메시지 생성
            error_data = custom_data or {}
            error_data.update({
                'error_message': f'동적 데이터 생성 오류: {str(e)}',
                'quality_warning': '❌ 실시간 데이터를 사용할 수 없습니다.',
                'data_reliability': '매우 낮음'
            })
            return self.generate_message(message_type, error_data)
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """데이터 품질 리포트 생성"""
        try:
            print("📊 데이터 품질 리포트 생성 중...")
            
            # 현재 시장 데이터 품질 확인
            market_data = self.data_manager.get_market_data()
            quality_stats = self.data_manager.get_quality_statistics()
            
            report = {
                'current_quality': {
                    'overall': market_data.overall_quality,
                    'kospi': market_data.kospi.quality_score if market_data.kospi else 0,
                    'exchange': market_data.exchange_rate.quality_score if market_data.exchange_rate else 0,
                    'posco': market_data.posco_stock.quality_score if market_data.posco_stock else 0,
                    'news': market_data.news_sentiment.quality_score if market_data.news_sentiment else 0
                },
                'statistics': quality_stats,
                'recommendations': self._generate_quality_recommendations(market_data, quality_stats),
                'last_updated': market_data.last_updated,
                'report_generated': datetime.now().isoformat()
            }
            
            print(f"✅ 데이터 품질 리포트 생성 완료 (전체 품질: {market_data.overall_quality:.1%})")
            return report
            
        except Exception as e:
            print(f"❌ 데이터 품질 리포트 생성 실패: {e}")
            return {
                'error': f'품질 리포트 생성 실패: {str(e)}',
                'report_generated': datetime.now().isoformat()
            }
    
    def _generate_quality_recommendations(self, market_data: MarketData, 
                                        quality_stats: Dict[str, Any]) -> List[str]:
        """데이터 품질 개선 권장사항 생성"""
        recommendations = []
        
        # 전체 품질 기반 권장사항
        if market_data.overall_quality < 0.5:
            recommendations.append("전체 데이터 품질이 낮습니다. API 연결 상태를 확인하세요.")
        
        # 개별 데이터 소스 권장사항
        if market_data.kospi and market_data.kospi.quality_score < 0.6:
            recommendations.append("KOSPI 데이터 품질이 낮습니다. 데이터 소스를 확인하세요.")
        
        if market_data.exchange_rate and market_data.exchange_rate.quality_score < 0.6:
            recommendations.append("환율 데이터 품질이 낮습니다. API 키를 확인하세요.")
        
        if market_data.posco_stock and market_data.posco_stock.quality_score < 0.6:
            recommendations.append("POSCO 주가 데이터 품질이 낮습니다. 주식 API 상태를 확인하세요.")
        
        # 트렌드 기반 권장사항
        trend = quality_stats.get('quality_trend', '')
        if trend == '악화 중':
            recommendations.append("데이터 품질이 악화되고 있습니다. 시스템 점검이 필요합니다.")
        elif trend == '데이터 부족':
            recommendations.append("품질 분석을 위한 데이터가 부족합니다. 더 많은 데이터 수집이 필요합니다.")
        
        # 기본 권장사항
        if not recommendations:
            if market_data.overall_quality >= 0.8:
                recommendations.append("데이터 품질이 우수합니다. 현재 상태를 유지하세요.")
            else:
                recommendations.append("데이터 품질을 개선하기 위해 정기적인 모니터링을 권장합니다.")
        
        return recommendations


# 편의 함수들
def create_deployment_success_message(deployment_result: Dict[str, Any]) -> Dict[str, str]:
    """배포 성공 메시지 생성 (편의 함수)"""
    engine = MessageTemplateEngine()
    return engine.generate_deployment_success_message(deployment_result)


def create_deployment_failure_message(deployment_result: Dict[str, Any]) -> Dict[str, str]:
    """배포 실패 메시지 생성 (편의 함수)"""
    engine = MessageTemplateEngine()
    return engine.generate_deployment_failure_message(deployment_result)


def create_data_update_message(market_data: Dict[str, Any]) -> Dict[str, str]:
    """데이터 업데이트 메시지 생성 (편의 함수)"""
    engine = MessageTemplateEngine()
    return engine.generate_data_update_message(market_data)


def preview_message_template(message_type: str, sample_data: Dict[str, Any]) -> str:
    """메시지 템플릿 미리보기 (편의 함수)"""
    engine = MessageTemplateEngine()
    try:
        msg_type = MessageType(message_type)
        return engine.preview_message(msg_type, sample_data)
    except ValueError:
        return f"❌ 지원하지 않는 메시지 타입: {message_type}"


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 MessageTemplateEngine 테스트 시작...")
    
    engine = MessageTemplateEngine()
    
    # 배포 성공 메시지 테스트
    test_deployment_result = {
        'deployment_id': 'deploy_20250901_143022',
        'start_time': '2025-09-01T14:30:22',
        'end_time': '2025-09-01T14:32:45',
        'steps_completed': ['status_check', 'backup_creation', 'branch_switch', 'merge_main', 'commit_changes', 'push_remote', 'pages_verification'],
        'github_pages_accessible': True
    }
    
    success_msg = engine.generate_deployment_success_message(test_deployment_result)
    print("\n=== 배포 성공 메시지 테스트 ===")
    print(f"제목: {success_msg['title']}")
    print(f"내용:\n{success_msg['body']}")
    
    # 배포 실패 메시지 테스트
    test_failure_result = {
        'deployment_id': 'deploy_20250901_143022',
        'error_message': 'Git 푸시 중 인증 실패',
        'steps_completed': ['status_check', 'backup_creation', 'branch_switch'],
        'rollback_performed': True
    }
    
    failure_msg = engine.generate_deployment_failure_message(test_failure_result)
    print("\n=== 배포 실패 메시지 테스트 ===")
    print(f"제목: {failure_msg['title']}")
    print(f"내용:\n{failure_msg['body']}")
    
    print("\n✅ MessageTemplateEngine 테스트 완료")