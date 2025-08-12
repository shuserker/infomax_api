# 🗂️ POSCO WatchHamster v3.0 프로젝트 정리 가이드

## 📋 정리 대상 파일 분석

### 🚮 삭제 권장 파일들

#### 1. 중복된 구버전 제어센터 스크립트들
```bash
# 이제 posco_control_center.sh가 메인이므로 삭제 가능
🎛️POSCO_제어센터_실행_v2.bat          # 중복
🎛️POSCO_제어센터_실행_v2.sh           # 중복  
🎛️POSCO_제어센터_실행.bat             # 구버전
🎛️POSCO_제어센터_Mac실행.command       # 구버전
🐹WatchHamster_총괄_관리_센터_SIMPLE.bat   # 구버전
🐹WatchHamster_총괄_관리_센터_v3.bat       # 구버전
🐹WatchHamster_총괄_관리_센터.bat          # 구버전
🐹WatchHamster_통합_관리_센터.bat          # 구버전
watchhamster_master_control.ps1        # 구버전
watchhamster_master_control.sh         # 구버전
posco_control_mac.sh                   # 중복
```

#### 2. 구버전 문서들
```bash
# v2.0 문서로 대체되었으므로 삭제 가능
WatchHamster_사용법.md                    # 구버전 (v2 가이드로 대체)
WatchHamster_시스템_재구축_완료_보고서_v4.md # 구버전 (v2 완료보고서로 대체)
Mac_WatchHamster_실행_가이드_v4.md         # 구버전 (v2 가이드로 대체)
🎨WINDOWS_TERMINAL_UPGRADE_v3.md       # 구버전
🎨WINDOWS_TERMINAL_UPGRADE_v4.md       # 구버전
```

#### 3. 개발 중 생성된 임시 파일들
```bash
# 개발 과정에서 생성된 임시 파일들
🚀POSCO_메인_알림_시작_직접.bat        # 직접 실행용 (제어센터 사용 권장)
🚀POSCO_메인_알림_시작_직접.sh         # 직접 실행용 (제어센터 사용 권장)
POSCO_시작.bat                        # 구버전
🔄Git_덮어씌우기.bat                   # 개발용 임시 파일
```

#### 4. 시스템 생성 파일들
```bash
# 시스템에서 자동 생성되는 파일들 (필요시 재생성됨)
.DS_Store                             # macOS 시스템 파일
__pycache__/                          # Python 캐시 디렉토리
```

### 📁 보관 권장 파일들

#### 1. v2.0 핵심 파일들 (절대 삭제 금지)
```bash
# 메인 시스템
posco_control_center.sh               # 메인 제어센터
Monitoring/                           # 전체 모니터링 시스템

# v2.0 문서들
📋POSCO_WatchHamster_v2_사용자_가이드.md
🔧POSCO_WatchHamster_문제해결_가이드.md
🔔POSCO_WatchHamster_알림시스템_가이드.md
🛠️POSCO_WatchHamster_개발자_가이드.md
🔄POSCO_WatchHamster_마이그레이션_가이드.md
📋POSCO_WatchHamster_v2_프로젝트_완료_보고서.md

# 마이그레이션 도구들
migrate_to_v2.sh
rollback_migration.sh
convert_config.py
check_migration_requirements.sh
MIGRATION_README.md
```

#### 2. 데이터 및 설정 파일들
```bash
# 중요한 데이터 파일들 (백업 후 정리 고려)
posco_news_cache.json                 # 뉴스 캐시
posco_news_data.json                  # 뉴스 데이터
posco_news_historical_cache.json      # 히스토리 캐시
posco_business_day_mapping.json       # 영업일 매핑
reports_index.json                    # 리포트 인덱스
requirements.txt                      # 의존성 정보
```

#### 3. 유틸리티 파일들
```bash
# 유용한 유틸리티들 (선택적 보관)
json_viewer.py                        # JSON 뷰어
posco_news_viewer.py                  # 뉴스 뷰어
deploy_latest_report.py               # 리포트 배포
sync_publish_branch.py                # Git 동기화
posco_continuous_monitor.py           # 연속 모니터링
```

### 🗂️ 정리 스크립트

#### 자동 정리 스크립트 생성
```bash
#!/bin/bash
# cleanup_old_files.sh

echo "🗂️ POSCO WatchHamster v3.0 프로젝트 정리 시작"

# 백업 디렉토리 생성
CLEANUP_BACKUP="cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CLEANUP_BACKUP"

echo "📦 삭제 예정 파일들을 백업 중..."

# 구버전 제어센터 스크립트들 백업 후 삭제
OLD_SCRIPTS=(
    ".naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/🎛️POSCO_제어센터_실행_v2.bat"
    "🎛️POSCO_제어센터_실행_v2.sh"
    "🎛️POSCO_제어센터_실행.bat"
    ".naming_backup/scripts/.naming_backup/scripts/🎛️POSCO_제어센터_Mac실행.command"
    ".naming_backup/config_data_backup/watchhamster.log"
    ".naming_backup/config_data_backup/watchhamster.log"
    ".naming_backup/config_data_backup/watchhamster.log"
    ".naming_backup/config_data_backup/watchhamster.log"
    "watchhamster_master_control.ps1"
    ".naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/watchhamster_master_control.sh"
    ".naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/posco_control_mac.sh"
)

for file in "${OLD_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$CLEANUP_BACKUP/"
        rm "$file"
        echo "✅ 삭제: $file"
    fi
done

# 구버전 문서들 백업 후 삭제
OLD_DOCS=(
    ".naming_backup/config_data_backup/watchhamster.log"
    ".naming_backup/config_data_backup/watchhamster.log"
    ".naming_backup/config_data_backup/watchhamster.log"
    "🎨WINDOWS_TERMINAL_UPGRADE_v3.md"
    "🎨WINDOWS_TERMINAL_UPGRADE_v4.md"
)

for file in "${OLD_DOCS[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$CLEANUP_BACKUP/"
        rm "$file"
        echo "✅ 삭제: $file"
    fi
done

# 임시 파일들 백업 후 삭제
TEMP_FILES=(
    ".naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/🚀POSCO_메인_알림_시작_직접.bat"
    ".naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/.naming_backup/scripts/🚀POSCO_메인_알림_시작_직접.sh"
    "POSCO_시작.bat"
    "🔄Git_덮어씌우기.bat"
)

for file in "${TEMP_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$CLEANUP_BACKUP/"
        rm "$file"
        echo "✅ 삭제: $file"
    fi
done

# 시스템 파일들 삭제
if [ -f ".DS_Store" ]; then
    rm ".DS_Store"
    echo "✅ 삭제: .DS_Store"
fi

if [ -d "__pycache__" ]; then
    rm -rf "__pycache__"
    echo "✅ 삭제: __pycache__/"
fi

echo ""
echo "🎉 정리 완료!"
echo "📦 백업 위치: $CLEANUP_BACKUP"
echo ""
echo "📋 정리 결과:"
echo "  ✅ 구버전 제어센터 스크립트 정리"
echo "  ✅ 구버전 문서 정리"
echo "  ✅ 임시 파일 정리"
echo "  ✅ 시스템 파일 정리"
echo ""
echo "🚀 이제 깔끔한 v2.0 환경이 준비되었습니다!"
```

## 🎯 정리 권장사항

### 1. 단계별 정리 접근
1. **1단계**: 명확히 불필요한 파일들 먼저 정리
2. **2단계**: 백업 후 구버전 파일들 정리
3. **3단계**: 데이터 파일들은 신중하게 검토 후 정리

### 2. 안전한 정리 방법
- 모든 삭제 전에 백업 생성
- 중요한 데이터 파일은 별도 보관
- 정리 후 시스템 동작 확인

### 3. 정리 후 확인사항
- v2.0 시스템 정상 동작 확인
- 필요한 파일들이 모두 존재하는지 확인
- 백업 파일 위치 기록

## 💡 추천 정리 순서

1. **즉시 삭제 가능**: 시스템 파일들 (.DS_Store, __pycache__)
2. **백업 후 삭제**: 구버전 스크립트 및 문서들
3. **검토 후 결정**: 데이터 파일들 및 유틸리티들
4. **보관 필수**: v2.0 핵심 파일들

이렇게 정리하면 프로젝트가 훨씬 깔끔해지고 유지보수가 쉬워집니다! 🎉