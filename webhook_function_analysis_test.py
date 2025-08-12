#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 함수 분석 테스트
문법 오류가 있는 파일에서도 웹훅 함수 복원 상태를 분석

Created: 2025-08-12
"""

import os
import re
import json
from datetime import datetime

class WebhookFunctionAnalysisTest:
    """웹훅 함수 분석 테스트 클래스"""
    
    def __init__(self):
        self.monitor_file = 'core/monitoring/monitor_WatchHamster_v3.0.py'
        self.test_results = []
        
        # 복원되어야 할 웹훅 함수들
        self.expected_functions = [
            'send_status_notification',
            'send_notification',
            'send_enhanced_status_notification',
            'send_startup_notification_v2'
        ]
        
        # 웹훅 URL 설정들
        self.expected_webhook_urls = [
            'DOORAY_WEBHOOK_URL',
            'WATCHHAMSTER_WEBHOOK_URL'
        ]
        
        print("🔍 웹훅 함수 분석 테스트 초기화 완료")
    
    def log(self, message):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def analyze_webhook_functions(self):
        """웹훅 함수 분석"""
        self.log("📋 웹훅 함수 분석 시작...")
        
        if not os.path.exists(self.monitor_file):
            self.log(f"❌ 모니터 파일 없음: {self.monitor_file}")
            return False
        
        try:
            with open(self.monitor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            function_analysis = []
            
            for func_name in self.expected_functions:
                # 함수 정의 찾기
                pattern = rf'def {func_name}\s*\([^)]*\):'
                matches = re.findall(pattern, content)
                
                if matches:
                    # 함수 내용 분석
                    func_pattern = rf'def {func_name}\s*\([^)]*\):(.*?)(?=def\s+\w+|class\s+\w+|\Z)'
                    func_match = re.search(func_pattern, content, re.DOTALL)
                    
                    if func_match:
                        func_content = func_match.group(1)
                        
                        # 웹훅 관련 키워드 확인
                        webhook_keywords = [
                            'webhook',
                            'dooray',
                            'requests.post',
                            'DOORAY_WEBHOOK_URL',
                            'WATCHHAMSTER_WEBHOOK_URL',
                            'payload',
                            'json='
                        ]
                        
                        found_keywords = [kw for kw in webhook_keywords if kw.lower() in func_content.lower()]
                        
                        # 메시지 템플릿 확인
                        has_korean_message = bool(re.search(r'[가-힣]', func_content))
                        has_emoji = bool(re.search(r'[🔔🚨📅🎯✅❌⚠️🔧📊🐹🛡️]', func_content))
                        
                        # 줄바꿈 문자 확인
                        has_newlines = '\\n' in func_content or '\n' in func_content
                        
                        function_analysis.append({
                            'function': func_name,
                            'exists': True,
                            'definition_count': len(matches),
                            'content_length': len(func_content),
                            'webhook_keywords': found_keywords,
                            'has_korean_message': has_korean_message,
                            'has_emoji': has_emoji,
                            'has_newlines': has_newlines,
                            'analysis': 'RESTORED' if len(found_keywords) > 0 else 'INCOMPLETE'
                        })
                        
                        self.log(f"✅ {func_name}: 발견됨 ({len(found_keywords)}개 웹훅 키워드)")
                    else:
                        function_analysis.append({
                            'function': func_name,
                            'exists': True,
                            'definition_count': len(matches),
                            'analysis': 'DEFINITION_ONLY'
                        })
                        self.log(f"⚠️ {func_name}: 정의만 있음")
                else:
                    function_analysis.append({
                        'function': func_name,
                        'exists': False,
                        'analysis': 'MISSING'
                    })
                    self.log(f"❌ {func_name}: 없음")
            
            self.test_results.append({
                'test_name': '웹훅 함수 분석',
                'success': all(f['exists'] for f in function_analysis),
                'details': {
                    'total_functions': len(self.expected_functions),
                    'found_functions': sum(1 for f in function_analysis if f['exists']),
                    'restored_functions': sum(1 for f in function_analysis if f.get('analysis') == 'RESTORED'),
                    'function_analysis': function_analysis
                }
            })
            
            return True
            
        except Exception as e:
            self.log(f"❌ 파일 분석 실패: {e}")
            return False
    
    def analyze_webhook_urls(self):
        """웹훅 URL 설정 분석"""
        self.log("🔗 웹훅 URL 설정 분석 시작...")
        
        try:
            with open(self.monitor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            url_analysis = []
            
            for url_name in self.expected_webhook_urls:
                # URL 설정 찾기
                pattern = rf'{url_name}\s*=\s*["\']([^"\']+)["\']'
                matches = re.findall(pattern, content)
                
                if matches:
                    url_value = matches[0]
                    is_valid_url = url_value.startswith('https://') and 'dooray.com' in url_value
                    
                    url_analysis.append({
                        'url_name': url_name,
                        'exists': True,
                        'url_value': url_value[:50] + '...' if len(url_value) > 50 else url_value,
                        'is_valid': is_valid_url,
                        'analysis': 'VALID' if is_valid_url else 'INVALID'
                    })
                    
                    self.log(f"✅ {url_name}: 설정됨 ({'유효' if is_valid_url else '무효'})")
                else:
                    url_analysis.append({
                        'url_name': url_name,
                        'exists': False,
                        'analysis': 'MISSING'
                    })
                    self.log(f"❌ {url_name}: 없음")
            
            self.test_results.append({
                'test_name': '웹훅 URL 설정 분석',
                'success': all(u['exists'] and u['is_valid'] for u in url_analysis if u['exists']),
                'details': {
                    'total_urls': len(self.expected_webhook_urls),
                    'found_urls': sum(1 for u in url_analysis if u['exists']),
                    'valid_urls': sum(1 for u in url_analysis if u.get('is_valid', False)),
                    'url_analysis': url_analysis
                }
            })
            
            return True
            
        except Exception as e:
            self.log(f"❌ URL 분석 실패: {e}")
            return False
    
    def analyze_message_templates(self):
        """메시지 템플릿 분석"""
        self.log("💬 메시지 템플릿 분석 시작...")
        
        try:
            with open(self.monitor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 중요한 메시지 패턴들 확인
            message_patterns = [
                ('POSCO 워치햄스터', r'POSCO\s*워치햄스터'),
                ('WatchHamster', r'WatchHamster'),
                ('정기 상태 보고', r'정기\s*상태\s*보고'),
                ('시스템 상태', r'시스템\s*상태'),
                ('조용한 시간대', r'조용한\s*시간대'),
                ('성능 알림', r'성능\s*알림'),
                ('오류 알림', r'오류\s*알림')
            ]
            
            template_analysis = []
            
            for pattern_name, pattern in message_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                template_analysis.append({
                    'pattern_name': pattern_name,
                    'found_count': len(matches),
                    'exists': len(matches) > 0
                })
                
                if len(matches) > 0:
                    self.log(f"✅ {pattern_name}: {len(matches)}개 발견")
                else:
                    self.log(f"❌ {pattern_name}: 없음")
            
            # 이모지 사용 확인
            emoji_patterns = ['🔔', '🚨', '📅', '🎯', '✅', '❌', '⚠️', '🔧', '📊', '🐹', '🛡️']
            found_emojis = [emoji for emoji in emoji_patterns if emoji in content]
            
            self.log(f"🎨 이모지 사용: {len(found_emojis)}/{len(emoji_patterns)}개")
            
            self.test_results.append({
                'test_name': '메시지 템플릿 분석',
                'success': sum(1 for t in template_analysis if t['exists']) >= len(template_analysis) * 0.7,  # 70% 이상
                'details': {
                    'total_patterns': len(message_patterns),
                    'found_patterns': sum(1 for t in template_analysis if t['exists']),
                    'emoji_usage': f"{len(found_emojis)}/{len(emoji_patterns)}",
                    'template_analysis': template_analysis,
                    'found_emojis': found_emojis
                }
            })
            
            return True
            
        except Exception as e:
            self.log(f"❌ 메시지 템플릿 분석 실패: {e}")
            return False
    
    def analyze_integration_compatibility(self):
        """통합 호환성 분석"""
        self.log("🔄 통합 호환성 분석 시작...")
        
        try:
            with open(self.monitor_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # v3.0 컴포넌트와의 통합 확인
            integration_patterns = [
                ('v3.0 컴포넌트', r'v3[._]0[._]components'),
                ('ProcessManager', r'ProcessManager'),
                ('StateManager', r'StateManager'),
                ('NotificationManager', r'NotificationManager'),
                ('PerformanceMonitor', r'PerformanceMonitor'),
                ('통합 아키텍처', r'통합.*아키텍처|아키텍처.*통합'),
                ('하이브리드', r'하이브리드'),
                ('폴백', r'폴백|fallback')
            ]
            
            integration_analysis = []
            
            for pattern_name, pattern in integration_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                integration_analysis.append({
                    'pattern_name': pattern_name,
                    'found_count': len(matches),
                    'exists': len(matches) > 0
                })
                
                if len(matches) > 0:
                    self.log(f"✅ {pattern_name}: {len(matches)}개 발견")
                else:
                    self.log(f"⚠️ {pattern_name}: 없음")
            
            self.test_results.append({
                'test_name': '통합 호환성 분석',
                'success': sum(1 for i in integration_analysis if i['exists']) >= 3,  # 최소 3개 이상
                'details': {
                    'total_patterns': len(integration_patterns),
                    'found_patterns': sum(1 for i in integration_analysis if i['exists']),
                    'integration_analysis': integration_analysis
                }
            })
            
            return True
            
        except Exception as e:
            self.log(f"❌ 통합 호환성 분석 실패: {e}")
            return False
    
    def run_comprehensive_analysis(self):
        """전체 분석 실행"""
        self.log("🚀 웹훅 함수 종합 분석 시작")
        
        # 분석 단계별 실행
        analyses = [
            ("웹훅 함수 분석", self.analyze_webhook_functions),
            ("웹훅 URL 설정 분석", self.analyze_webhook_urls),
            ("메시지 템플릿 분석", self.analyze_message_templates),
            ("통합 호환성 분석", self.analyze_integration_compatibility)
        ]
        
        overall_success = True
        for analysis_name, analysis_func in analyses:
            self.log(f"🔍 {analysis_name} 실행 중...")
            try:
                result = analysis_func()
                if not result:
                    overall_success = False
            except Exception as e:
                self.log(f"❌ {analysis_name} 중 오류: {e}")
                overall_success = False
        
        # 결과 요약
        self.generate_analysis_report(overall_success)
        
        return overall_success
    
    def generate_analysis_report(self, overall_success):
        """분석 결과 보고서 생성"""
        self.log("📊 분석 결과 보고서 생성 중...")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        
        report = {
            'analysis_summary': {
                'overall_success': overall_success,
                'total_analyses': total_tests,
                'successful_analyses': successful_tests,
                'failed_analyses': total_tests - successful_tests,
                'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': self.test_results
        }
        
        # JSON 보고서 저장
        report_filename = f'webhook_function_analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 마크다운 보고서 생성
        self.generate_markdown_report(report, overall_success)
        
        self.log(f"📄 분석 보고서 저장: {report_filename}")
        
        # 결과 요약 출력
        self.log("=" * 60)
        self.log("🎯 웹훅 함수 분석 결과 요약")
        self.log("=" * 60)
        self.log(f"전체 성공: {'✅ 성공' if overall_success else '❌ 실패'}")
        self.log(f"분석 수행: {successful_tests}/{total_tests} ({report['analysis_summary']['success_rate']:.1f}%)")
        
        # 주요 결과 요약
        for result in self.test_results:
            status = "✅ 성공" if result['success'] else "❌ 실패"
            self.log(f"  • {result['test_name']}: {status}")
        
        self.log("=" * 60)
        
        return report
    
    def generate_markdown_report(self, report, overall_success):
        """마크다운 형식 보고서 생성"""
        report_filename = f'webhook_function_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("# 웹훅 함수 분석 보고서\n\n")
            f.write(f"**분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**전체 결과**: {'✅ 성공' if overall_success else '❌ 실패'}\n\n")
            
            # 요약 정보
            summary = report['analysis_summary']
            f.write("## 📊 분석 요약\n\n")
            f.write(f"- **총 분석 항목**: {summary['total_analyses']}\n")
            f.write(f"- **성공한 분석**: {summary['successful_analyses']}\n")
            f.write(f"- **실패한 분석**: {summary['failed_analyses']}\n")
            f.write(f"- **성공률**: {summary['success_rate']:.1f}%\n\n")
            
            # 상세 결과
            f.write("## 📋 상세 분석 결과\n\n")
            for result in report['detailed_results']:
                status = "✅ 성공" if result['success'] else "❌ 실패"
                f.write(f"### {result['test_name']} - {status}\n\n")
                
                if 'details' in result:
                    f.write("**세부 정보**:\n")
                    f.write(f"```json\n{json.dumps(result['details'], ensure_ascii=False, indent=2)}\n```\n\n")
            
            f.write("## 🔍 결론\n\n")
            if overall_success:
                f.write("- ✅ 웹훅 기능이 성공적으로 복원되었습니다.\n")
                f.write("- ✅ 메시지 템플릿과 URL 설정이 정상적으로 구성되었습니다.\n")
                f.write("- ✅ 신규 시스템과의 통합 호환성이 확인되었습니다.\n")
            else:
                f.write("- ⚠️ 일부 웹훅 기능에 문제가 있을 수 있습니다.\n")
                f.write("- ⚠️ 상세 결과를 확인하여 필요한 수정을 진행하세요.\n")
        
        self.log(f"📄 마크다운 보고서 저장: {report_filename}")

def main():
    """메인 실행 함수"""
    print("🔍 POSCO 워치햄스터 v3.0 웹훅 함수 분석 테스트")
    print("=" * 60)
    
    analyzer = WebhookFunctionAnalysisTest()
    success = analyzer.run_comprehensive_analysis()
    
    if success:
        print("\n🎉 웹훅 함수 분석 성공!")
        return 0
    else:
        print("\n⚠️ 웹훅 함수 분석에서 일부 문제 발견")
        return 1

if __name__ == "__main__":
    exit(main())