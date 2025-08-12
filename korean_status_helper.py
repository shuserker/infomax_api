#!/usr/bin/env python3
"""
POSCO 시스템 한글 상태 도우미
Korean Status Helper for POSCO System

모든 시스템에서 일관된 한글 상태 메시지를 사용할 수 있도록 도와줍니다.
"""

# 상태 번역 사전
STATUS_KO = {
    "active": "활성",
    "cancel": "취소",
    "cancelled": "취소됨",
    "completed": "완료",
    "connected": "연결됨",
    "continue": "계속",
    "copied": "복사됨",
    "created": "생성됨",
    "debug": "디버그",
    "deleted": "삭제됨",
    "disabled": "비활성화",
    "disconnected": "연결끊김",
    "enabled": "활성화",
    "error": "오류",
    "failed": "실패",
    "finish": "완료",
    "in_progress": "진행중",
    "inactive": "비활성",
    "info": "정보",
    "moved": "이동됨",
    "not_started": "시작안함",
    "offline": "오프라인",
    "online": "온라인",
    "passed": "통과",
    "paused": "일시정지",
    "pending": "대기중",
    "renamed": "이름변경됨",
    "restart": "재시작",
    "retry": "재시도",
    "running": "실행중",
    "skipped": "건너뜀",
    "start": "시작",
    "stop": "중지",
    "stopped": "중지됨",
    "success": "성공",
    "timeout": "시간초과",
    "updated": "업데이트됨",
    "warning": "경고",
}

def get_korean_status(status: str) -> str:
    """영어 상태를 한글로 번역"""
    return STATUS_KO.get(status.lower(), status)

def format_korean_message(template: str, **kwargs) -> str:
    """한글 메시지 템플릿 포맷팅"""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template

# 자주 사용되는 메시지 템플릿
MESSAGES_KO = {
    "backup_created": "백업이 {path}에 생성되었습니다",
    "backup_failed": "백업 생성에 실패했습니다: {error}",
    "backup_restored": "백업 {backup_id}에서 복원되었습니다",
    "cleanup_completed": "정리 작업이 완료되었습니다",
    "cleanup_progress": "{processed}개 파일 처리 완료",
    "cleanup_started": "정리 작업을 시작합니다",
    "file_copied": "파일이 {source}에서 {destination}으로 복사되었습니다",
    "file_created": "파일 {path}가 생성되었습니다",
    "file_deleted": "파일 {path}가 삭제되었습니다",
    "file_moved": "파일이 {source}에서 {destination}으로 이동되었습니다",
    "file_renamed": "파일이 {old_name}에서 {new_name}으로 이름이 변경되었습니다",
    "files_organized": "{count}개 파일이 {destination}으로 정리되었습니다",
    "progress_update": "진행 상황: {current}/{total} ({percentage:.1f}%)",
    "rollback_completed": "롤백이 완료되었습니다",
    "rollback_failed": "롤백이 실패했습니다: {error}",
    "rollback_initiated": "롤백을 시작합니다",
    "system_error": "시스템 오류가 발생했습니다: {error}",
    "system_ready": "시스템이 준비되었습니다",
    "system_starting": "시스템을 시작하는 중입니다",
    "system_stopping": "시스템을 중지하는 중입니다",
    "task_completed": "작업 "{task_name}"이 완료되었습니다",
    "task_failed": "작업 "{task_name}"이 실패했습니다: {error}",
    "task_started": "작업 "{task_name}"을 시작했습니다",
    "verification_failed": "무결성 검증이 실패했습니다",
    "verification_passed": "무결성 검증이 통과되었습니다",
    "verification_started": "무결성 검증을 시작합니다",
}

def get_korean_message(key: str, **kwargs) -> str:
    """한글 메시지 템플릿 가져오기"""
    template = MESSAGES_KO.get(key, key)
    return format_korean_message(template, **kwargs)

# 사용 예시
if __name__ == "__main__":
    print(get_korean_status("completed"))  # "완료"
    print(get_korean_message("file_moved", source="a.txt", destination="b.txt"))
