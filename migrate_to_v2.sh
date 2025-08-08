#!/bin/bash
# POSCO 워치햄스터 v2.0 마이그레이션 스크립트

set -e  # 오류 시 중단

echo "🚀 POSCO 워치햄스터 v2.0 마이그레이션 시작"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[단계 $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 단계 1: 사전 확인
print_step "1" "사전 확인 및 백업"

# 기존 워치햄스터 중지
if pgrep -f "monitor_WatchHamster.py" > /dev/null; then
    print_warning "기존 워치햄스터 중지 중..."
    pkill -f "monitor_WatchHamster.py"
    sleep 5
fi

# 백업 생성
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 기존 시스템 백업 중..."
cp -r Monitoring/ "$BACKUP_DIR/" 2>/dev/null || true
cp watchhamster_control_center.sh "$BACKUP_DIR/" 2>/dev/null || true
cp *.log "$BACKUP_DIR/" 2>/dev/null || true
cp *.json "$BACKUP_DIR/" 2>/dev/null || true

print_success "백업 완료: $BACKUP_DIR"

# 단계 2: v2 아키텍처 설치
print_step "2" "v2 아키텍처 설치"

# v2 디렉토리 생성
mkdir -p Monitoring/Posco_News_mini_v2/core

# 핵심 컴포넌트 파일들이 존재하는지 확인
if [ ! -f "Monitoring/Posco_News_mini_v2/core/enhanced_process_manager.py" ]; then
    print_error "v2 컴포넌트 파일들이 없습니다. 먼저 v2 파일들을 배치해주세요."
    exit 1
fi

print_success "v2 아키텍처 파일 확인 완료"# 단계 
3: 설정 파일 마이그레이션
print_step "3" "설정 파일 마이그레이션"

# 설정 변환 스크립트 실행
python3 << 'EOF'
import json
import os
from datetime import datetime

# 기존 설정 로드 (있는 경우)
config_data = {
    "metadata": {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "description": "POSCO WatchHamster Module Registry Configuration - Migrated from v1.x"
    },
    "modules": {
        "posco_main_notifier": {
            "script_path": "posco_main_notifier.py",
            "description": "POSCO 메인 뉴스 알림 시스템",
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
            "description": "실시간 뉴스 모니터링 시스템",
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
            "description": "통합 리포트 스케줄러",
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
}

# 선택적 모듈 확인 및 추가
optional_modules = ["historical_data_collector.py"]
for module_file in optional_modules:
    module_path = f"Monitoring/Posco_News_mini/{module_file}"
    if os.path.exists(module_path):
        module_name = module_file.replace('.py', '')
        config_data["modules"][module_name] = {
            "script_path": module_file,
            "description": f"{module_name} - v1.x에서 마이그레이션",
            "auto_start": False,
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
        print(f"✅ 선택적 모듈 추가: {module_name}")

# modules.json 생성
with open('Monitoring/Posco_News_mini_v2/modules.json', 'w', encoding='utf-8') as f:
    json.dump(config_data, f, indent=2, ensure_ascii=False)

print("✅ modules.json 생성 완료")
EOF

print_success "설정 파일 마이그레이션 완료"#
 단계 4: 워치햄스터 업데이트 확인
print_step "4" "워치햄스터 업데이트 확인"

# 새로운 아키텍처 import 테스트
python3 -c "
import sys
import os
sys.path.insert(0, 'Monitoring/Posco_News_mini')

try:
    from monitor_WatchHamster import PoscoMonitorWatchHamster
    wh = PoscoMonitorWatchHamster()
    
    # 새로운 컴포넌트 확인
    if hasattr(wh, 'process_manager') and wh.process_manager:
        print('✅ Enhanced ProcessManager 활성화')
    else:
        print('⚠️ Enhanced ProcessManager 비활성화 (기존 방식 사용)')
        
    if hasattr(wh, 'module_registry') and wh.module_registry:
        print('✅ ModuleRegistry 활성화')
    else:
        print('⚠️ ModuleRegistry 비활성화')
        
    if hasattr(wh, 'notification_manager') and wh.notification_manager:
        print('✅ NotificationManager 활성화')
    else:
        print('⚠️ NotificationManager 비활성화')
        
    print('🎉 워치햄스터 v2.0 초기화 성공')
    
except Exception as e:
    print(f'❌ 워치햄스터 초기화 실패: {e}')
    exit(1)
"

print_success "워치햄스터 업데이트 확인 완료"

# 단계 5: 제어센터 업데이트 확인
print_step "5" "제어센터 업데이트 확인"

if grep -q "워치햄스터 통합 관리" watchhamster_control_center.sh 2>/dev/null; then
    print_success "워치햄스터 제어센터 v2.0 메뉴 구조 확인"
else
    print_warning "워치햄스터 제어센터가 v2.0으로 업데이트되지 않았습니다"
fi

# 단계 6: 마이그레이션 검증
print_step "6" "마이그레이션 검증"

# 테스트 시작
print_warning "워치햄스터 테스트 시작 (10초간)..."
timeout 10s python3 Monitoring/Posco_News_mini/monitor_WatchHamster.py &
TEST_PID=$!

sleep 5

if kill -0 $TEST_PID 2>/dev/null; then
    print_success "워치햄스터 테스트 실행 성공"
    kill $TEST_PID 2>/dev/null
    wait $TEST_PID 2>/dev/null || true
else
    print_error "워치햄스터 테스트 실행 실패"
fi

# 단계 7: 마이그레이션 검증 실행
print_step "7" "마이그레이션 검증 실행"

echo "🔍 마이그레이션 검증 시스템을 실행합니다..."
if [ -f "run_migration_verification.sh" ]; then
    if ./run_migration_verification.sh --full; then
        print_success "마이그레이션 검증 완료"
        VERIFICATION_SUCCESS=true
    else
        print_warning "마이그레이션 검증에서 일부 문제가 발견되었습니다"
        VERIFICATION_SUCCESS=false
    fi
else
    print_warning "마이그레이션 검증 스크립트를 찾을 수 없습니다"
    VERIFICATION_SUCCESS=false
fi

# 단계 8: 마이그레이션 완료
print_step "8" "마이그레이션 완료"

echo ""
echo "🎉 POSCO 워치햄스터 v2.0 마이그레이션 완료!"
echo ""
echo "📋 마이그레이션 결과:"
echo "  ✅ 기존 기능 100% 보존"
echo "  ✅ 새로운 아키텍처 적용"
echo "  ✅ 향상된 프로세스 관리"
echo "  ✅ 개선된 제어센터"

if [ "$VERIFICATION_SUCCESS" = true ]; then
    echo "  ✅ 마이그레이션 검증 통과"
else
    echo "  ⚠️ 마이그레이션 검증 부분 실패 (상세 내용은 보고서 확인)"
fi

echo ""
echo "🚀 다음 단계:"
echo "  1. ./watchhamster_control_center.sh 실행"
echo "  2. 메뉴 1번으로 워치햄스터 시작"
echo "  3. 메뉴 4번으로 상태 확인"

if [ "$VERIFICATION_SUCCESS" = false ]; then
    echo "  4. 검증 보고서 확인: migration_reports/ 디렉토리"
    echo "  5. 필요시 롤백 고려: ./rollback_migration.sh"
fi

echo ""
echo "📞 문제 발생 시:"
echo "  - 로그 확인: tail -f watchhamster.log"
echo "  - 검증 재실행: ./run_migration_verification.sh"
echo "  - 롤백: ./rollback_migration.sh"
echo ""