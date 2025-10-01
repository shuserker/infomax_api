# Git 충돌 자동 해결 시스템 (내장형)

## 📋 개요

Task 6에서 구현된 Git 충돌 자동 해결 시스템은 브랜치 전환 시 발생하는 충돌을 자동으로 감지하고 해결하는 완전 독립적인 시스템입니다.

**Requirements 구현:**
- ✅ **3.2**: 브랜치 전환 시 발생하는 충돌 자동 감지 및 해결 로직
- ✅ **3.3**: 해결 불가능한 충돌 시 GUI 알림 및 수동 해결 인터페이스

## 🔧 주요 기능

### 1. 자동 충돌 감지 (Requirements 3.2)

#### `detect_conflict_files()` 메서드
- 병합 진행 상태 확인 (`MERGE_HEAD` 검사)
- 충돌 파일 목록 자동 감지 (`git diff --name-only --diff-filter=U`)
- 각 충돌 파일의 상세 분석 수행

#### 충돌 파일 분석 기능
```python
def _analyze_conflict_file(self, file_path: str) -> Dict[str, any]:
    """개별 충돌 파일 분석"""
    # 파일 타입 식별 (code, markup, style, config, text, other)
    # 충돌 마커 개수 계산 (<<<<<<<, =======, >>>>>>>)
    # 충돌 섹션 상세 분석
    # 자동 해결 가능성 판단
```

**지원하는 파일 타입:**
- `code`: .py, .js, .ts, .java, .cpp, .c, .h
- `markup`: .html, .htm, .xml
- `style`: .css, .scss, .sass
- `config`: .json, .yaml, .yml
- `text`: .md, .txt, .rst
- `other`: 기타 파일

### 2. 스마트 자동 해결 (Requirements 3.2)

#### 자동 해결 가능성 판단 기준
- 충돌 섹션 개수 (5개 이하)
- 파일 크기 (100KB 이하)
- 파일 타입별 복잡도 분석
- 코드 파일의 경우 더 엄격한 기준 적용

#### 해결 전략
```python
def _get_resolution_strategy(self, analysis: Dict[str, any]) -> str:
    """해결 전략 결정"""
    if analysis['file_type'] in ['config', 'text']:
        return 'prefer_ours'  # 설정 파일은 우리 버전 우선
    elif analysis['file_type'] == 'code':
        return 'smart_merge'  # 코드는 스마트 병합 시도
    else:
        return 'prefer_ours'  # 기본적으로 우리 버전 우선
```

#### 스마트 병합 로직
- 한쪽이 비어있으면 다른 쪽 선택
- 동일한 내용이면 하나만 선택
- 기본적으로 안전한 선택 (우리 버전 우선)

### 3. GUI 수동 해결 인터페이스 (Requirements 3.3)

#### GUI 콜백 시스템
```python
def handle_git_conflicts(self, gui_callback=None) -> Dict[str, any]:
    """GUI 콜백을 통한 수동 해결 인터페이스 호출"""
    if manual_required and gui_callback:
        gui_result = gui_callback(manual_required, conflict_info)
```

#### GUI 인터페이스 기능
- **충돌 파일 목록 표시**: 트리뷰로 파일 상태 실시간 표시
- **해결 옵션 제공**: 우리 버전/그들 버전/수동 편집
- **외부 편집기 연동**: 시스템 기본 편집기로 파일 열기
- **실시간 진행 상황**: 해결 완료 상태 즉시 반영

#### 해결 옵션
1. **우리 버전 사용** (`--ours`): 현재 브랜치 변경사항 유지
2. **그들 버전 사용** (`--theirs`): 병합 브랜치 변경사항 적용
3. **수동 편집**: 외부 편집기에서 직접 충돌 해결

### 4. 통합 충돌 해결 시스템

#### `handle_git_conflicts()` 메서드 워크플로우
1. **충돌 감지**: 모든 충돌 파일 식별 및 분석
2. **자동 해결**: 가능한 파일들 자동 처리
3. **GUI 호출**: 수동 해결 필요 시 GUI 인터페이스 표시
4. **병합 완료**: 모든 충돌 해결 후 자동 커밋

#### 반환 정보
```python
resolution_result = {
    'success': bool,                    # 전체 해결 성공 여부
    'conflicts_detected': bool,         # 충돌 감지 여부
    'auto_resolved': [],               # 자동 해결된 파일 목록
    'manual_required': [],             # 수동 해결 필요 파일 목록
    'failed_resolutions': [],          # 해결 실패 파일 목록
    'resolution_summary': {},          # 해결 요약 통계
    'gui_intervention_needed': bool,   # GUI 개입 필요 여부
    'error_message': str              # 오류 메시지
}
```

## 🔄 브랜치 전환 통합

### `safe_branch_switch()` 메서드 개선
기존 브랜치 전환 로직에 향상된 충돌 해결 시스템이 통합되었습니다:

```python
# 2단계: 충돌 상태 확인 및 해결
if status_info['has_conflicts']:
    conflict_result = self.handle_git_conflicts()
    
    if conflict_result['success']:
        # 자동 해결 성공
        switch_result['conflicts_resolved'] = True
        switch_result['conflict_resolution_summary'] = conflict_result['resolution_summary']
    elif conflict_result['gui_intervention_needed']:
        # GUI 개입 필요
        switch_result['manual_conflicts'] = conflict_result['manual_required']
        switch_result['conflict_details'] = conflict_result
        return switch_result  # 사용자 개입 대기
```

## 🖥️ GUI 통합

### PoscoGUIManager 개선사항

#### 브랜치 전환 결과 처리
- 자동 충돌 해결 성공 시 요약 정보 표시
- 수동 해결 필요 시 전용 GUI 창 자동 표시
- 실시간 해결 진행 상황 모니터링

#### 수동 충돌 해결 GUI
```python
def _show_manual_conflict_resolution(self, conflict_files, conflict_details, target_branch):
    """수동 충돌 해결 GUI 인터페이스 표시"""
    # 모달 창 생성
    # 충돌 파일 목록 트리뷰
    # 해결 옵션 버튼들
    # 실시간 상태 업데이트
```

#### GUI 기능
- **파일별 해결**: 개별 파일 선택 및 해결 옵션 적용
- **외부 편집기**: 시스템 기본 편집기로 파일 열기
- **실시간 상태**: 해결 완료 파일 즉시 표시
- **일괄 완료**: 모든 충돌 해결 후 병합 커밋 자동 실행

## 🧪 테스트 및 검증

### 테스트 스크립트
- **`test_conflict_resolution.py`**: 자동화된 충돌 해결 테스트
- **`demo_conflict_gui.py`**: GUI 인터페이스 데모 및 시뮬레이션

### 테스트 결과
```
============================================================
📊 Git 충돌 해결 시스템 테스트 결과
============================================================
✅ PASS 충돌 감지: 2개 파일 감지
✅ PASS 자동 충돌 해결: 모든 충돌 해결 완료
✅ PASS 충돌 해결 옵션: 모든 옵션 테스트 완료
------------------------------------------------------------
총 테스트: 3개
성공: 3개
실패: 0개
성공률: 100.0%
```

## 🔒 안전성 보장

### 안전 장치
1. **단계별 로깅**: 모든 해결 과정 상세 기록
2. **상태 백업**: 해결 전 Git 상태 정보 보존
3. **점진적 해결**: 파일별 개별 처리로 위험 최소화
4. **사용자 확인**: 중요한 결정은 사용자 승인 필요

### 오류 처리
- 각 단계별 예외 처리 및 복구
- 실패 시 명확한 오류 메시지 제공
- GUI를 통한 사용자 알림 및 대안 제시

## 📁 파일 구조

```
Posco_News_Mini_Final_GUI/
├── git_deployment_manager.py          # 핵심 충돌 해결 로직
├── posco_gui_manager.py               # GUI 통합 인터페이스
├── test_conflict_resolution.py        # 자동화 테스트
├── demo_conflict_gui.py               # GUI 데모
└── CONFLICT_RESOLUTION_SYSTEM.md      # 이 문서
```

## 🚀 사용 방법

### 1. 자동 충돌 해결
```python
deployment_manager = GitDeploymentManager()
result = deployment_manager.handle_git_conflicts()

if result['success']:
    print("모든 충돌 자동 해결 완료!")
```

### 2. GUI와 함께 사용
```python
def gui_callback(manual_files, conflict_info):
    # GUI 인터페이스 표시
    # 사용자 선택 처리
    return {'resolved_files': resolved_files}

result = deployment_manager.handle_git_conflicts(gui_callback)
```

### 3. 브랜치 전환 시 자동 적용
```python
switch_result = deployment_manager.safe_branch_switch("publish")

if switch_result['success']:
    print("브랜치 전환 및 충돌 해결 완료!")
elif switch_result.get('manual_conflicts'):
    print("수동 해결 필요한 파일:", switch_result['manual_conflicts'])
```

## 🎯 구현 완료 사항

### Requirements 3.2 ✅
- [x] 브랜치 전환 시 발생하는 충돌 자동 감지
- [x] 충돌 파일 자동 해결 로직 구현
- [x] 파일 타입별 스마트 해결 전략
- [x] 안전한 자동 병합 시스템

### Requirements 3.3 ✅
- [x] 해결 불가능한 충돌 시 GUI 알림
- [x] 수동 해결 인터페이스 제공
- [x] 다양한 해결 옵션 (ours/theirs/manual)
- [x] 외부 편집기 연동 지원
- [x] 실시간 해결 진행 상황 표시

## 🔮 향후 개선 가능사항

1. **AI 기반 충돌 해결**: 머신러닝을 활용한 더 스마트한 자동 해결
2. **시각적 diff 도구**: GUI 내장 diff 뷰어 추가
3. **충돌 패턴 학습**: 반복되는 충돌 패턴 자동 학습 및 적용
4. **팀 협업 기능**: 충돌 해결 히스토리 공유 및 베스트 프랙티스 제안

---

**구현 완료일**: 2025-09-02  
**테스트 통과율**: 100%  
**Requirements 충족**: 3.2, 3.3 완전 구현