#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 레거시 시스템 비활성화 관리자

개별 리포트 시스템을 비활성화하고 통합 리포트 시스템만 활성화하는 클래스
기존 개별 모니터링 스크립트들을 안전하게 비활성화하고 리다이렉트 처리
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class LegacySystemDisabler:
    """
    레거시 시스템 비활성화 클래스
    """
    
    def __init__(self):
        """초기화"""
        self.monitoring_dir = Path(__file__).parent
        
        # 비활성화할 개별 모니터 스크립트들
        self.individual_monitors = [
            'exchange_monitor.py',
            'kospi_monitor.py', 
            'newyork_monitor.py',
            'master_news_monitor.py',
            'run_monitor.py'
        ]
        
        # 비활성화할 개별 리포트 생성 스크립트들
        self.individual_generators = [
            'reports/html_report_generator.py'  # 개별 리포트 생성기
        ]
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def disable_individual_monitors(self) -> Dict[str, bool]:
        """
        개별 모니터링 스크립트들을 비활성화
        
        Returns:
            Dict[str, bool]: 각 스크립트별 비활성화 결과
        """
        self.logger.info("🚫 개별 모니터링 스크립트 비활성화 시작...")
        
        results = {}
        
        for monitor_script in self.individual_monitors:
            script_path = self.monitoring_dir / monitor_script
            
            try:
                if script_path.exists():
                    # 스크립트를 .disabled 확장자로 이름 변경
                    disabled_path = script_path.with_suffix('.py.disabled')
                    
                    # 이미 비활성화된 파일이 있으면 제거
                    if disabled_path.exists():
                        disabled_path.unlink()
                    
                    # 파일 이름 변경으로 비활성화
                    script_path.rename(disabled_path)
                    
                    # 비활성화 안내 파일 생성
                    self.create_redirect_file(script_path, monitor_script)
                    
                    results[monitor_script] = True
                    self.logger.info(f"✅ {monitor_script} 비활성화 완료")
                else:
                    results[monitor_script] = True  # 파일이 없으면 이미 비활성화된 것으로 간주
                    self.logger.info(f"ℹ️ {monitor_script} 파일이 존재하지 않음 (이미 비활성화됨)")
                    
            except Exception as e:
                results[monitor_script] = False
                self.logger.error(f"❌ {monitor_script} 비활성화 실패: {e}")
        
        # 결과 요약
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        self.logger.info(f"📊 개별 모니터 비활성화 결과: {successful}/{total} 성공")
        
        return results
    
    def create_redirect_file(self, original_path: Path, script_name: str):
        """
        비활성화된 스크립트 대신 안내 메시지를 보여주는 리다이렉트 파일 생성
        
        Args:
            original_path (Path): 원본 스크립트 경로
            script_name (str): 스크립트 이름
        """
        redirect_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{script_name} - 비활성화됨

이 개별 모니터링 스크립트는 통합 리포트 시스템으로 전환되면서 비활성화되었습니다.

비활성화 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
대체 시스템: 통합 리포트 시스템 (integrated_report_scheduler.py)

사용법:
- 통합 리포트 생성: python3 integrated_report_scheduler.py
- 수동 리포트 생성: python3 reports/integrated_report_generator.py

원본 파일 위치: {script_name}.disabled
"""

import sys
from datetime import datetime

def main():
    print("🚫 이 스크립트는 비활성화되었습니다.")
    print(f"📅 비활성화 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("🔄 POSCO 리포트 시스템이 통합 리포트 시스템으로 전환되었습니다.")
    print()
    print("✅ 대신 사용할 수 있는 명령어:")
    print("   • 통합 리포트 생성: python3 integrated_report_scheduler.py")
    print("   • 수동 리포트 생성: python3 reports/integrated_report_generator.py")
    print("   • 메타데이터 업데이트: python3 metadata_reset_manager.py")
    print()
    print("📋 더 자세한 정보는 README.md 파일을 참조하세요.")
    print()
    print("⚠️ 개별 리포트 시스템은 더 이상 지원되지 않습니다.")
    
    return False

if __name__ == "__main__":
    main()
    sys.exit(1)  # 비정상 종료로 스크립트 실행 방지
'''
        
        try:
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(redirect_content)
            self.logger.info(f"📝 {script_name} 리다이렉트 파일 생성 완료")
        except Exception as e:
            self.logger.error(f"❌ {script_name} 리다이렉트 파일 생성 실패: {e}")
    
    def update_scheduler_config(self) -> bool:
        """
        스케줄러 설정을 통합 리포트만 사용하도록 업데이트
        
        Returns:
            bool: 업데이트 성공 여부
        """
        self.logger.info("⚙️ 스케줄러 설정 업데이트 시작...")
        
        try:
            # integrated_report_scheduler.py가 메인 스케줄러가 되도록 설정
            scheduler_path = self.monitoring_dir / 'integrated_report_scheduler.py'
            
            if scheduler_path.exists():
                self.logger.info("✅ 통합 리포트 스케줄러가 이미 존재합니다")
                
                # 스케줄러 실행 권한 확인
                if os.access(scheduler_path, os.X_OK):
                    self.logger.info("✅ 통합 리포트 스케줄러 실행 권한 확인됨")
                else:
                    # 실행 권한 부여
                    scheduler_path.chmod(0o755)
                    self.logger.info("✅ 통합 리포트 스케줄러 실행 권한 부여 완료")
                
                return True
            else:
                self.logger.error("❌ 통합 리포트 스케줄러를 찾을 수 없습니다")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 스케줄러 설정 업데이트 실패: {e}")
            return False
    
    def create_system_status_file(self) -> bool:
        """
        시스템 상태 파일 생성 (통합 리포트 시스템 활성화 상태 기록)
        
        Returns:
            bool: 파일 생성 성공 여부
        """
        try:
            status_file = self.monitoring_dir / 'system_status.json'
            
            status_data = {
                "system_mode": "integrated_reports_only",
                "transition_date": datetime.now().isoformat(),
                "active_components": [
                    "integrated_report_scheduler.py",
                    "reports/integrated_report_generator.py",
                    "metadata_reset_manager.py"
                ],
                "disabled_components": self.individual_monitors + self.individual_generators,
                "description": "POSCO 리포트 시스템이 통합 리포트 전용 모드로 전환됨",
                "last_update": datetime.now().isoformat()
            }
            
            import json
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 시스템 상태 파일 생성 완료: {status_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 상태 파일 생성 실패: {e}")
            return False
    
    def validate_system_state(self) -> Dict[str, str]:
        """
        시스템 상태 검증
        
        Returns:
            Dict[str, str]: 각 컴포넌트별 상태
        """
        self.logger.info("🔍 시스템 상태 검증 시작...")
        
        validation_results = {}
        
        # 1. 개별 모니터 비활성화 확인
        for monitor_script in self.individual_monitors:
            script_path = self.monitoring_dir / monitor_script
            disabled_path = script_path.with_suffix('.py.disabled')
            
            if disabled_path.exists() and not script_path.exists():
                validation_results[monitor_script] = "properly_disabled"
            elif script_path.exists():
                # 리다이렉트 파일인지 확인
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if "비활성화됨" in content and "sys.exit(1)" in content:
                        validation_results[monitor_script] = "redirect_active"
                    else:
                        validation_results[monitor_script] = "still_active"
                except:
                    validation_results[monitor_script] = "unknown_state"
            else:
                validation_results[monitor_script] = "missing"
        
        # 2. 통합 리포트 시스템 활성화 확인
        integrated_scheduler = self.monitoring_dir / 'integrated_report_scheduler.py'
        if integrated_scheduler.exists():
            validation_results['integrated_scheduler'] = "active"
        else:
            validation_results['integrated_scheduler'] = "missing"
        
        integrated_generator = self.monitoring_dir / 'reports' / 'integrated_report_generator.py'
        if integrated_generator.exists():
            validation_results['integrated_generator'] = "active"
        else:
            validation_results['integrated_generator'] = "missing"
        
        # 3. 시스템 상태 파일 확인
        status_file = self.monitoring_dir / 'system_status.json'
        if status_file.exists():
            validation_results['system_status_file'] = "present"
        else:
            validation_results['system_status_file'] = "missing"
        
        # 결과 로깅
        self.log_validation_results(validation_results)
        
        return validation_results
    
    def log_validation_results(self, results: Dict[str, str]):
        """
        검증 결과 로깅
        
        Args:
            results (Dict[str, str]): 검증 결과
        """
        self.logger.info("\\n" + "="*60)
        self.logger.info("📋 시스템 상태 검증 결과")
        self.logger.info("="*60)
        
        # 개별 모니터 상태
        self.logger.info("🚫 개별 모니터 비활성화 상태:")
        for monitor in self.individual_monitors:
            status = results.get(monitor, 'unknown')
            status_icon = {
                'properly_disabled': '✅',
                'redirect_active': '🔄',
                'still_active': '❌',
                'missing': '⚠️',
                'unknown_state': '❓'
            }.get(status, '❓')
            
            self.logger.info(f"  {status_icon} {monitor}: {status}")
        
        # 통합 시스템 상태
        self.logger.info("\\n✅ 통합 시스템 활성화 상태:")
        integrated_components = ['integrated_scheduler', 'integrated_generator', 'system_status_file']
        for component in integrated_components:
            status = results.get(component, 'unknown')
            status_icon = '✅' if status in ['active', 'present'] else '❌'
            self.logger.info(f"  {status_icon} {component}: {status}")
        
        # 전체 상태 요약
        disabled_count = sum(1 for monitor in self.individual_monitors 
                           if results.get(monitor) in ['properly_disabled', 'redirect_active'])
        total_monitors = len(self.individual_monitors)
        
        active_count = sum(1 for component in integrated_components 
                         if results.get(component) in ['active', 'present'])
        total_integrated = len(integrated_components)
        
        self.logger.info(f"\\n📊 전체 상태 요약:")
        self.logger.info(f"  🚫 개별 모니터 비활성화: {disabled_count}/{total_monitors}")
        self.logger.info(f"  ✅ 통합 시스템 활성화: {active_count}/{total_integrated}")
        
        if disabled_count == total_monitors and active_count == total_integrated:
            self.logger.info("\\n🎉 시스템 전환이 성공적으로 완료되었습니다!")
        else:
            self.logger.warning("\\n⚠️ 시스템 전환이 완전하지 않습니다. 수동 확인이 필요합니다.")

def main():
    """메인 실행 함수"""
    disabler = LegacySystemDisabler()
    
    print("🚫 레거시 시스템 비활성화 시작...")
    
    # 1. 개별 모니터 비활성화
    print("\\n1️⃣ 개별 모니터링 스크립트 비활성화 중...")
    monitor_results = disabler.disable_individual_monitors()
    
    # 2. 스케줄러 설정 업데이트
    print("\\n2️⃣ 스케줄러 설정 업데이트 중...")
    scheduler_success = disabler.update_scheduler_config()
    
    # 3. 시스템 상태 파일 생성
    print("\\n3️⃣ 시스템 상태 파일 생성 중...")
    status_file_success = disabler.create_system_status_file()
    
    # 4. 시스템 상태 검증
    print("\\n4️⃣ 시스템 상태 검증 중...")
    validation_results = disabler.validate_system_state()
    
    return {
        'monitor_results': monitor_results,
        'scheduler_success': scheduler_success,
        'status_file_success': status_file_success,
        'validation_results': validation_results
    }

if __name__ == "__main__":
    main()