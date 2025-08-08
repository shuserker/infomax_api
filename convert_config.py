#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 v2.0 설정 변환 스크립트

기존 v1.x 설정을 v2.0 형식으로 변환합니다.
"""

import json
import os
import sys
from datetime import datetime

def convert_config():
    """기존 설정을 v2.0 형식으로 변환"""
    
    print("🔄 설정 변환 시작")
    
    # 기존 config.py에서 설정 추출 (있는 경우)
    config_path = "Monitoring/Posco_News_mini/config.py"
    existing_config = {}
    
    if os.path.exists(config_path):
        print(f"📋 기존 설정 파일 발견: {config_path}")
        
        # 간단한 설정 추출 (실제로는 더 정교한 파싱 필요)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 웹훅 URL 추출
            if 'WEBHOOK_URL' in content:
                print("✅ 웹훅 URL 설정 발견")
                existing_config['webhook_found'] = True
                
        except Exception as e:
            print(f"⚠️ 기존 설정 파일 읽기 실패: {e}")
    
    # v2.0 modules.json 생성
    modules_config = {
        "metadata": {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "description": "POSCO WatchHamster Module Registry - Migrated from v1.x",
            "migration_info": {
                "migrated_from": "v1.x",
                "migration_date": datetime.now().isoformat(),
                "existing_config_found": bool(existing_config)
            }
        },
        "modules": {}
    }
    
    # 기본 모듈들 설정
    default_modules = {
        "posco_main_notifier": {
            "script_path": "posco_main_notifier.py",
            "description": "POSCO 메인 뉴스 알림 시스템 - v1.x에서 마이그레이션",
            "auto_start": True,
            "restart_on_failure": True,
            "max_restart_attempts": 3,
            "health_check_interval": 300,
            "dependencies": [],
            "environment_vars": {
                "PYTHONUNBUFFERED": "1"
            },
            "working_directory": "../Posco_News_mini",
            "timeout": 30,
            "priority": 1
        },
        "realtime_news_monitor": {
            "script_path": "realtime_news_monitor.py", 
            "description": "실시간 뉴스 모니터링 시스템 - v1.x에서 마이그레이션",
            "auto_start": True,
            "restart_on_failure": True,
            "max_restart_attempts": 3,
            "health_check_interval": 300,
            "dependencies": ["posco_main_notifier"],
            "environment_vars": {
                "PYTHONUNBUFFERED": "1"
            },
            "working_directory": "../Posco_News_mini",
            "timeout": 30,
            "priority": 2
        },
        "integrated_report_scheduler": {
            "script_path": "integrated_report_scheduler.py",
            "description": "통합 리포트 스케줄러 - v1.x에서 마이그레이션", 
            "auto_start": True,
            "restart_on_failure": True,
            "max_restart_attempts": 3,
            "health_check_interval": 300,
            "dependencies": ["posco_main_notifier"],
            "environment_vars": {
                "PYTHONUNBUFFERED": "1"
            },
            "working_directory": "../Posco_News_mini",
            "timeout": 30,
            "priority": 3
        }
    }
    
    # 선택적 모듈들 확인 및 추가
    optional_modules = {
        "historical_data_collector": {
            "script_path": "historical_data_collector.py",
            "description": "히스토리 데이터 수집기 - v1.x에서 마이그레이션",
            "auto_start": False,  # 선택적 시작
            "restart_on_failure": True,
            "max_restart_attempts": 2,
            "health_check_interval": 600,
            "dependencies": [],
            "environment_vars": {
                "PYTHONUNBUFFERED": "1"
            },
            "working_directory": "../Posco_News_mini",
            "timeout": 30,
            "priority": 4
        }
    }
    
    # 기본 모듈들 추가
    modules_config["modules"].update(default_modules)
    
    # 선택적 모듈들 존재 확인 후 추가
    for module_name, module_config in optional_modules.items():
        script_path = os.path.join("Monitoring/Posco_News_mini", module_config["script_path"])
        if os.path.exists(script_path):
            modules_config["modules"][module_name] = module_config
            print(f"✅ 선택적 모듈 발견: {module_name}")
        else:
            print(f"⚠️ 선택적 모듈 없음: {module_name}")
    
    # modules.json 저장
    output_path = "Monitoring/Posco_News_mini_v2/modules.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(modules_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 설정 변환 완료: {output_path}")
    print(f"📊 변환된 모듈 수: {len(modules_config['modules'])}")
    
    return True

def validate_config(config_path):
    """설정 파일 유효성 검증"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 필수 필드 확인
        if 'metadata' not in config:
            print("❌ metadata 섹션 누락")
            return False
            
        if 'modules' not in config:
            print("❌ modules 섹션 누락")
            return False
        
        # 각 모듈 검증
        for name, module in config['modules'].items():
            # 필수 필드 확인
            required_fields = ['script_path', 'description']
            for field in required_fields:
                if field not in module:
                    print(f"❌ {name}: 필수 필드 누락 - {field}")
                    return False
            
            # 스크립트 파일 존재 확인
            script_path = os.path.join('Monitoring/Posco_News_mini', module['script_path'])
            if not os.path.exists(script_path):
                print(f"⚠️ {name}: 스크립트 파일 없음 - {script_path}")
            else:
                print(f"✅ {name}: 설정 검증 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 검증 실패: {e}")
        return False

if __name__ == "__main__":
    try:
        # 설정 변환
        if convert_config():
            print("🎉 설정 변환 성공!")
            
            # 변환된 설정 검증
            config_path = "Monitoring/Posco_News_mini_v2/modules.json"
            if validate_config(config_path):
                print("✅ 변환된 설정 검증 완료!")
            else:
                print("⚠️ 변환된 설정에 문제가 있습니다.")
                
    except Exception as e:
        print(f"❌ 설정 변환 실패: {e}")
        sys.exit(1)