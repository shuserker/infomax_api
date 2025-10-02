# Git 명령어 안전 실행 가이드

## Git Show 명령어 재발방지 설정

### 문제 상황
- `git show` 명령어 실행 시 프로세스가 멈춰서 기다리는 상황 발생
- CPU 사용률 0%로 진행 없이 대기 상태 지속
- IDE 후처리만 높은 CPU 사용률 보임

### 해결 방안

#### 1. Git Show 대신 안전한 대안 사용
```bash
# 위험: git show (멈출 수 있음)
git show

# 안전: git log with format
git log --oneline -1 [commit-hash]
git log --stat -1 [commit-hash]
git show --name-only [commit-hash]
```

#### 2. 타임아웃 설정
```bash
# 타임아웃과 함께 실행
timeout 30s git show [commit-hash]
```

#### 3. 페이저 비활성화
```bash
# 페이저 없이 실행
git --no-pager show [commit-hash]
git show --no-pager [commit-hash]
```

#### 4. 출력 제한
```bash
# 출력 크기 제한
git show --stat [commit-hash]
git show --name-status [commit-hash]
```

### 권장 사항

1. **Git show 사용 금지**: 대화형 페이저로 인한 멈춤 현상 방지
2. **대안 명령어 사용**: `git log`, `git diff`, `git show --name-only` 등 활용
3. **항상 --no-pager 옵션 사용**: 페이저 비활성화로 안전한 실행
4. **타임아웃 설정**: 긴 출력 시 자동 중단 메커니즘

### 자동 적용 설정
```bash
# Git 전역 설정으로 페이저 비활성화
git config --global core.pager ""
git config --global --unset core.pager
```

이 가이드를 따라 Git 명령어 실행 시 멈춤 현상을 방지하세요.