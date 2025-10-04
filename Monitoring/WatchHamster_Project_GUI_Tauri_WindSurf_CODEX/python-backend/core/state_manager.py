#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WatchHamster 상태 관리 모듈

`design.md`에서 정의한 `StateManager` 사양을 충족하도록 구현했습니다.
- 상태 저장/로드 시 None 값을 안전하게 처리
- datetime 필드를 ISO 형식으로 직렬화
- 상태 데이터 스키마를 검증하여 NoneType 오류 방지
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class StateManager:
    """모니터링 상태를 안전하게 저장/복원하는 관리자"""

    DEFAULT_STATE_FILENAME = "watchhamster_state.json"

    def __init__(self, base_dir: Optional[Path | str] = None, state_file: Optional[Path | str] = None) -> None:
        base_path = Path(base_dir) if base_dir else Path(__file__).resolve().parents[1]
        self.state_file = Path(state_file) if state_file else base_path / "data" / self.DEFAULT_STATE_FILENAME
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger.getChild(self.__class__.__name__)
        self.logger.debug("StateManager initialised at %s", self.state_file)

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------
    def save_state(self, state_data: Dict[str, Any]) -> bool:
        """상태 데이터를 파일에 저장합니다.

        Args:
            state_data: 직렬화 가능한 상태 딕셔너리
        Returns:
            저장 성공 여부
        """

        try:
            if not self.validate_state_data(state_data):
                self.logger.warning("Invalid state data schema. Save aborted.")
                return False

            sanitized = self.handle_null_values(state_data)
            serialisable = self._serialise_state(sanitized)

            with self.state_file.open("w", encoding="utf-8") as fp:
                json.dump(serialisable, fp, ensure_ascii=False, indent=2)

            self.logger.debug("State saved successfully")
            return True
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error("Failed to save state: %s", exc, exc_info=True)
            return False

    def load_state(self) -> Dict[str, Any]:
        """상태 파일을 로드합니다. 파일이 없으면 기본값을 반환합니다."""

        if not self.state_file.exists():
            self.logger.debug("State file does not exist. Returning empty state.")
            return {}

        try:
            with self.state_file.open("r", encoding="utf-8") as fp:
                raw_state = json.load(fp)

            return self._deserialise_state(raw_state)
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error("Failed to load state: %s", exc, exc_info=True)
            return {}

    def validate_state_data(self, data: Dict[str, Any]) -> bool:
        """상태 데이터의 유효성을 검증합니다."""

        if not isinstance(data, dict):
            return False

        # 최소 필드 검증 (필요 시 확장 가능)
        allowed_top_keys = {
            "watchhamster_running",
            "individual_monitors",
            "master_monitor_active",
            "last_health_check",
            "error_count",
            "recovery_attempts",
            "metadata",
        }

        unknown_keys = set(data.keys()) - allowed_top_keys
        if unknown_keys:
            self.logger.debug("Unknown state keys detected: %s", ", ".join(sorted(unknown_keys)))

        return True

    def handle_null_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """None 값을 안전한 기본값으로 대체합니다."""

        sanitized: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self.handle_null_values(value)
            elif isinstance(value, list):
                sanitized[key] = [self.handle_null_values(item) if isinstance(item, dict) else item for item in value]
            elif value is None:
                sanitized[key] = self._default_for_key(key)
            else:
                sanitized[key] = value
        return sanitized

    # ------------------------------------------------------------------
    # 내부 도우미
    # ------------------------------------------------------------------
    def _default_for_key(self, key: str) -> Any:
        if key in {"last_health_check", "last_update", "timestamp"}:
            return datetime.utcnow().isoformat()
        if key in {"watchhamster_running", "master_monitor_active"}:
            return False
        if key in {"error_count", "recovery_attempts"}:
            return 0
        return ""

    def _serialise_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """datetime을 ISO 문자열로 변환하여 직렬화 가능한 딕셔너리 생성"""

        def _convert(value: Any) -> Any:
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, dict):
                return {k: _convert(v) for k, v in value.items()}
            if isinstance(value, list):
                return [_convert(item) for item in value]
            return value

        serialised = _convert(data)
        serialised["last_saved_at"] = datetime.utcnow().isoformat()
        return serialised

    def _deserialise_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """ISO 문자열을 datetime 객체로 변환"""

        def _parse(value: Any) -> Any:
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    return value
            if isinstance(value, dict):
                return {k: _parse(v) for k, v in value.items()}
            if isinstance(value, list):
                return [_parse(item) for item in value]
            return value

        cleaned = data.copy()
        cleaned.pop("last_saved_at", None)
        return _parse(cleaned)
