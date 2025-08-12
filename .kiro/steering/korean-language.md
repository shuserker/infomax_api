---
inclusion: always
---

# 한국어 응답 규칙 (Korean Language Response Rules)

## 언어 사용 규칙

**중요**: 모든 응답은 반드시 한국어로 작성해야 합니다.

### 기본 원칙
- 모든 대화와 설명은 한국어로 진행
- 기술 용어는 한국어 번역을 우선하되, 필요시 영문 병기
- 코드 주석도 가능한 한국어로 작성
- 파일명이나 변수명 등 코드 자체는 기존 규칙 유지

### 응답 스타일
- 정중하고 친근한 한국어 사용
- 존댓말 사용 (예: "~습니다", "~해주세요")
- 기술적 내용도 이해하기 쉬운 한국어로 설명

### 예시

#### ✅ 올바른 응답
```
네, 이 작업을 진행하겠습니다. 먼저 파일 구조를 확인한 후 필요한 수정을 진행하겠습니다.
```

#### ❌ 잘못된 응답
```
I'll proceed with this task. First, I'll check the file structure and then make the necessary modifications.
```

### 코드 주석 예시

#### ✅ 올바른 주석
```python
# 파일 경로 확인
def check_file_path(path):
    """파일 경로가 존재하는지 확인합니다."""
    return os.path.exists(path)
```

#### ❌ 잘못된 주석
```python
# Check file path
def check_file_path(path):
    """Check if file path exists."""
    return os.path.exists(path)
```

### 특별 지침
- POSCO 시스템 관련 작업 시 더욱 한국어 사용 강화
- 사용자가 한국어로 질문하면 반드시 한국어로 응답
- 기술 문서나 가이드 작성 시에도 한국어 우선

이 규칙은 모든 Kiro 상호작용에 적용됩니다.