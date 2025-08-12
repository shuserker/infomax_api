# 🔧 POSCO 네이밍 컨벤션 문제 해결 가이드

## 📋 개요

이 문서는 POSCO 네이밍 컨벤션 표준화 과정에서 발생할 수 있는 문제들과 해결 방법을 제공합니다.

## 🚨 일반적인 문제들

### 1. 파일 접근 권한 문제

#### 증상
```
# BROKEN_REF: PermissionError: [Errno 13] Permission denied: 'filename.py'
```

#### 원인
- 파일이 읽기 전용으로 설정됨
- 관리자 권한이 필요한 파일
- 다른 프로세스가 파일을 사용 중

#### 해결 방법
```bash
# 1. 파일 권한 확인
ls -la problematic_file.py

# 2. 권한 수정
chmod 644 *.py *.json *.md
chmod +x *.sh *.bat *.command

# 3. 소유권 확인 및 수정 (필요시)
sudo chown $USER:$USER problematic_file.py

# 4. 관리자 권한으로 실행 (최후 수단)
sudo python3 posco_file_renamer.py --watchhamster
```

### 2. 파일이 사용 중인 경우

#### 증상
```
# BROKEN_REF: OSError: [Errno 16] Device or resource busy: 'filename.py'
```

#### 원인
- 파일이 다른 프로그램에서 실행 중
- 텍스트 에디터에서 파일을 열어둠
- 시스템 프로세스가 파일을 잠금

#### 해결 방법
```bash
# 1. 실행 중인 프로세스 확인
ps aux | grep python | grep posco
ps aux | grep -E "(posco|watchhamster)"

# 2. 프로세스 종료
pkill -f "posco_main_notifier"
pkill -f "monitor_WatchHamster"
pkill -f "realtime_news_monitor"

# 3. 파일을 사용하는 프로세스 확인 (Linux/Mac)
lsof filename.py

# 4. 강제 종료 (주의해서 사용)
sudo pkill -9 -f "posco"

# 5. 재시도
python3 posco_file_renamer.py --watchhamster
```

### 3. 디스크 공간 부족

#### 증상
```
OSError: [Errno 28] No space left on device
```

#### 원인
- 백업 파일로 인한 디스크 공간 부족
- 로그 파일이 과도하게 커짐
- 임시 파일이 정리되지 않음

#### 해결 방법
```bash
# 1. 디스크 사용량 확인
df -h
du -sh .naming_backup/
du -sh *.log

# 2. 불필요한 파일 정리
rm -f *.log.old
rm -rf __pycache__/
rm -rf .pytest_cache/

# 3. 백업 파일 정리 (주의)
rm -rf .naming_backup/old_backups/
find .naming_backup/ -name "*.bak" -mtime +7 -delete

# 4. 로그 파일 정리
truncate -s 0 file_renaming.log
truncate -s 0 naming_verification.log

# 5. 임시 파일 정리
find /tmp -name "*posco*" -user $USER -delete
```

### 4. 네이밍 컨벤션 감지 실패

#### 증상
```
ConversionResult(success=False, reason="Unknown component type")
```

#### 원인
- 파일명에 인식 가능한 키워드가 없음
- 새로운 파일 패턴이 규칙에 없음
- 특수 문자로 인한 패턴 매칭 실패

#### 해결 방법
```python
# 1. 컴포넌트 감지 테스트
# BROKEN_REF: from naming_convention_manager.py.py import NamingConventionManager
manager = NamingConventionManager()

# 문제 파일 확인
# BROKEN_REF: component = manager.detect_component_type("problematic_file.py")
print(f"감지된 컴포넌트: {component}")

# 2. 수동 컴포넌트 지정
# BROKEN_REF: result = manager.standardize_filename("problematic_file.py", force_component="watchhamster")
print(f"수동 변환 결과: {result}")

# 3. 키워드 추가 (코드 수정 필요)
# naming_convention_manager.py에서 키워드 목록 확장
```

```bash
# 4. 파일명 패턴 확인
python3 -c "
# BROKEN_REF: from naming_convention_manager.py.py import NamingConventionManager
manager = NamingConventionManager()
print('WatchHamster 키워드:', manager.WATCHHAMSTER_KEYWORDS)
print('POSCO News 키워드:', manager.POSCO_NEWS_KEYWORDS)
"
```

### 5. 백업 파일 손상

#### 증상
```
FileNotFoundError: [Errno 2] No such file or directory: '.naming_backup/mapping_table.json'
```

#### 원인
- 백업 과정에서 오류 발생
- 백업 파일이 삭제됨
- 백업 디렉토리 권한 문제

#### 해결 방법
```bash
# 1. 백업 디렉토리 확인
ls -la .naming_backup/
ls -la .naming_backup/config_data_backup/
ls -la .naming_backup/scripts/

# 2. 백업 파일 재생성
python3 posco_file_renamer.py --create-backup

# 3. Git에서 복구 (Git 사용 시)
git checkout HEAD -- .naming_backup/

# 4. 수동 백업에서 복구
cp -r ../manual_backup/.naming_backup/ .

# 5. 새로운 백업 생성
python3 -c "
# BROKEN_REF: from file_renaming_system.py.py import FileRenamingSystem
system = FileRenamingSystem('.')
system.create_backup()
"
```

### 6. JSON 파일 파싱 오류

#### 증상
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 15 column 5
```

#### 원인
- JSON 파일 형식 오류
- 파일 인코딩 문제
- 파일이 부분적으로 손상됨

#### 해결 방법
```bash
# 1. JSON 파일 검증
python3 -m json.tool posco_news_250808_data.json

# 2. 백업에서 복구
cp .naming_backup/config_data_backup/posco_news_250808_data.json .

# 3. 파일 인코딩 확인
file posco_news_250808_data.json
hexdump -C posco_news_250808_data.json | head

# 4. 수동 수정 (간단한 오류의 경우)
python3 -c "
import test_config.test_config.json
try:
    with open('posco_news_250808_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print('JSON 파일이 정상입니다.')
except json.JSONDecodeError as e:
    print(f'JSON 오류: {e}')
    print(f'라인 {e.lineno}, 컬럼 {e.colno}')
"
```

### 7. 폴더 구조 불일치

#### 증상
```
FileNotFoundError: No such file or directory: 'Monitoring/POSCO_News_250808/config.py'
```

#### 원인
- 폴더명 변경 후 경로 참조 업데이트 누락
- 상대 경로와 절대 경로 혼용
- 심볼릭 링크 문제

#### 해결 방법
```bash
# 1. 폴더 구조 확인
find . -type d -name "*WatchHamster*" -o -name "*POSCO_News*" -o -name "*posco*"

# 2. 경로 참조 확인
grep -r "Monitoring/Posco_News_mini" . --include="*.py" --include="*.sh"
grep -r "POSCO_News_250808" . --include="*.py" --include="*.sh"

# 3. 폴더 구조 복구
mv Monitoring/POSCO_News_250808 Monitoring/Posco_News_mini
mv Monitoring/WatchHamster_v3.0 Monitoring/Posco_News_mini_v2

# 4. 심볼릭 링크 확인
find . -type l -ls

# 5. 경로 참조 업데이트 (필요시)
sed -i 's|POSCO_News_250808|Posco_News_mini|g' *.py
sed -i 's|WatchHamster_v3.0|Posco_News_mini_v2|g' *.py
```

### 8. 인코딩 문제

#### 증상
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

#### 원인
- 파일이 UTF-8이 아닌 인코딩으로 저장됨
- BOM(Byte Order Mark) 문제
- 바이너리 파일을 텍스트로 처리

#### 해결 방법
```bash
# 1. 파일 인코딩 확인
file -bi filename.py
chardet filename.py

# 2. 인코딩 변환
iconv -f EUC-KR -t UTF-8 filename.py > filename_utf8.py
mv filename_utf8.py filename.py

# 3. BOM 제거
sed -i '1s/^\xEF\xBB\xBF//' filename.py

# 4. Python에서 인코딩 지정
python3 -c "
# BROKEN_REF: with open('filename.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
# BROKEN_REF: with open('filename.py', 'w', encoding='utf-8') as f:
    f.write(content)
"
```

## 🔍 진단 도구

### 1. 시스템 상태 확인 스크립트

```bash
#!/bin/bash
# posco_system_diagnosis.sh

echo "=== POSCO 시스템 진단 ==="
echo "날짜: $(date)"
echo

echo "1. 디스크 사용량:"
df -h | grep -E "(Filesystem|/dev/)"
echo

echo "2. 실행 중인 POSCO 프로세스:"
ps aux | grep -E "(posco|watchhamster)" | grep -v grep
echo

echo "3. 주요 파일 존재 확인:"
for file in "🐹WatchHamster_v3.0_Control_Center.bat" "POSCO_News_250808.py" "posco_news_250808_data.json"; do
    if [ -f "$file" ]; then
        echo "✓ $file (존재)"
    else
        echo "✗ $file (없음)"
    fi
done
echo

echo "4. 폴더 구조:"
find Monitoring/ -maxdepth 2 -type d 2>/dev/null | sort
echo

echo "5. 백업 상태:"
if [ -d ".naming_backup" ]; then
    echo "✓ 백업 디렉토리 존재"
    echo "백업 파일 수: $(find .naming_backup/ -type f | wc -l)"
else
    echo "✗ 백업 디렉토리 없음"
fi
echo

echo "6. 로그 파일 크기:"
for log in "file_renaming.log" "naming_verification.log" "WatchHamster_v3.0.log"; do
    if [ -f "$log" ]; then
        size=$(du -h "$log" | cut -f1)
        echo "$log: $size"
    fi
done
```

### 2. 네이밍 일관성 검사 스크립트

```python
#!/usr/bin/env python3
# naming_consistency_checker.py

import pposco_news_250808_monitor.logco_news_250808_monitor.log
import test_config.test_config.json
import verify_folder_verify_folder_reorganization.pyorganization.py
# BROKEN_REF: from pathlib import Path

def check_naming_consistency():
    """네이밍 일관성 검사"""
    issues = []
    
    # WatchHamster 파일 검사
    watchhamster_pattern = re.compile(r'.*watchhamster.*v3\.0.*', re.IGNORECASE)
    posco_news_pattern = re.compile(r'.*posco.*news.*250808.*', re.IGNORECASE)
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            filepath = os.path.join(root, file)
            
            # WatchHamster 관련 파일 검사
            if 'watchhamster' in file.lower() or 'hamster' in file.lower():
                if not watchhamster_pattern.match(file):
                    issues.append(f"WatchHamster 파일 네이밍 불일치: {filepath}")
            
            # POSCO News 관련 파일 검사
            if 'posco' in file.lower() and 'news' in file.lower():
                if not posco_news_pattern.match(file):
                    issues.append(f"POSCO News 파일 네이밍 불일치: {filepath}")
    
    return issues

if __name__ == "__main__":
    issues = check_naming_consistency()
    if issues:
        print("네이밍 일관성 문제 발견:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("네이밍 일관성 검사 통과")
```

### 3. 백업 무결성 검사

```python
#!/usr/bin/env python3
# backup_integrity_checker.py

import pposco_news_250808_monitor.logco_news_250808_monitor.log
import test_config.test_config.json
# BROKEN_REF: import hashlib
# BROKEN_REF: from pathlib import Path

def check_backup_integrity():
    """백업 파일 무결성 검사"""
    backup_dir = Path('.naming_backup')
    
    if not backup_dir.exists():
        return ["백업 디렉토리가 존재하지 않습니다."]
    
    issues = []
    
    # 필수 백업 파일 확인
    required_files = [
        '.naming_backup/.naming_backup/.naming_backup/.naming_backup/mapping_table.json',
# BROKEN_REF:         'operations_log.json'
    ]
    
    for file in required_files:
        file_path = backup_dir / file
        if not file_path.exists():
            issues.append(f"필수 백업 파일 누락: {file}")
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                issues.append(f"백업 파일 손상: {file}")
    
    return issues

if __name__ == "__main__":
    issues = check_backup_integrity()
    if issues:
        print("백업 무결성 문제 발견:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("백업 무결성 검사 통과")
```

## 📞 지원 요청 시 정보 수집

### 자동 정보 수집 스크립트

```bash
#!/bin/bash
# collect_debug_info.sh

DEBUG_DIR="debug_info_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_DIR"

echo "디버그 정보 수집 중..."

# 시스템 정보
# BROKEN_REF: uname -a > "$DEBUG_DIR/system_info.txt"
# BROKEN_REF: python3 --version >> "$DEBUG_DIR/system_info.txt"
# BROKEN_REF: pip3 list | grep -E "(requests|psutil|json)" >> "$DEBUG_DIR/system_info.txt"

# 프로세스 정보
# BROKEN_REF: ps aux | grep -E "(python|posco|watchhamster)" > "$DEBUG_DIR/processes.txt"

# 파일 구조
# BROKEN_REF: find . -name "*.py" -o -name "*.bat" -o -name "*.sh" -o -name "*.json" | head -50 > "$DEBUG_DIR/file_structure.txt"

# 로그 파일 (최근 100줄)
for log in "file_renaming.log" "naming_verification.log" "WatchHamster_v3.0.log"; do
    if [ -f "$log" ]; then
# BROKEN_REF:         tail -100 "$log" > "$DEBUG_DIR/${log%.log}_recent.log"
    fi
done

# 백업 정보
if [ -d ".naming_backup" ]; then
    cp .naming_backup/mapping_table.json "$DEBUG_DIR/" 2>/dev/null
    cp .naming_backup/operations_log.json "$DEBUG_DIR/" 2>/dev/null
fi

# 설정 파일
cp posco_news_250808_*.json "$DEBUG_DIR/" 2>/dev/null
cp modules.json "$DEBUG_DIR/" 2>/dev/null

# 압축
tar -czf "${DEBUG_DIR}.tar.gz" "$DEBUG_DIR"
rm -rf "$DEBUG_DIR"

echo "디버그 정보가 ${DEBUG_DIR}.tar.gz에 저장되었습니다."
echo "지원 요청 시 이 파일을 첨부해 주세요."
```

## 🔄 예방 조치

### 정기 점검 스크립트

```bash
#!/bin/bash
# posco_maintenance.sh

echo "=== POSCO 시스템 정기 점검 ==="

# 1. 디스크 공간 확인 (80% 이상 시 경고)
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  디스크 사용량이 ${DISK_USAGE}%입니다. 정리가 필요합니다."
fi

# 2. 로그 파일 크기 확인 (100MB 이상 시 경고)
for log in "file_renaming.log" "naming_verification.log"; do
    if [ -f "$log" ]; then
        SIZE=$(du -m "$log" | cut -f1)
        if [ "$SIZE" -gt 100 ]; then
            echo "⚠️  $log 파일이 ${SIZE}MB입니다. 정리를 고려하세요."
        fi
    fi
done

# 3. 백업 파일 무결성 확인
# BROKEN_REF: python3 backup_integrity_checker.py

# 4. 네이밍 일관성 확인
# BROKEN_REF: python3 naming_consistency_checker.py

echo "정기 점검 완료"
```

---

## 📋 문제 해결 체크리스트

### 마이그레이션 전 체크리스트
- [ ] 전체 시스템 백업 완료
- [ ] 실행 중인 프로세스 종료
- [ ] 디스크 공간 충분 (최소 1GB)
- [ ] 파일 권한 확인
- [ ] 네트워크 연결 안정

### 문제 발생 시 체크리스트
- [ ] 오류 메시지 정확히 기록
- [ ] 로그 파일 확인
- [ ] 백업 파일 존재 확인
- [ ] 시스템 리소스 확인
- [ ] 권한 문제 확인

### 복구 후 체크리스트
- [ ] 주요 파일 존재 확인
- [ ] 실행 권한 확인
- [ ] 기능 테스트 수행
- [ ] 성능 확인
- [ ] 로그 정상성 확인

---

**🔧 문제가 지속되거나 해결되지 않는 경우, 위의 디버그 정보 수집 스크립트를 실행하고 결과를 개발팀에 전달해 주세요.**