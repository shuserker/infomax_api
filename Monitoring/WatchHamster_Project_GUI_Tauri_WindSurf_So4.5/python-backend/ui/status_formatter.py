#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WatchHamster 상태 포맷터 모듈

`design.md`에서 정의한 `StatusFormatter` 사양을 충족하도록 구현했습니다.
- 모니터 상태 정보 포맷팅
- 시간 정보 포맷팅 (한국 시간)
- 시스템 리소스 시각화
- 오류 메시지 포맷팅
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz

from rich.text import Text
from rich.table import Table
from rich import box


class StatusFormatter:
    """상태 정보를 시각적으로 포맷팅"""

    KST = pytz.timezone("Asia/Seoul")

    def __init__(self):
        """StatusFormatter 초기화"""
        pass

    # ------------------------------------------------------------------
    # 모니터 상태 포맷팅
    # ------------------------------------------------------------------
    def format_monitor_status(self, monitors: Dict[str, Any]) -> str:
        """모니터 상태를 포맷팅합니다.

        Args:
            monitors: 모니터 상태 딕셔너리
                {
                    "monitor_name": {
                        "status": "running",
                        "health": "healthy",
                        "last_check": datetime,
                        "error_count": 0,
                        ...
                    }
                }

        Returns:
            포맷팅된 문자열
        """
        if not monitors:
            return "[dim]모니터 없음[/dim]"

        lines = []
        for name, info in monitors.items():
            status = info.get("status", "unknown")
            health = info.get("health", "unknown")
            error_count = info.get("error_count", 0)

            # 상태 이모지
            status_emoji = self._get_status_emoji(status)
            health_emoji = self._get_health_emoji(health)

            # 상태 색상
            status_color = self._get_status_color(status)
            health_color = self._get_health_color(health)

            line = (
                f"{status_emoji} [{status_color}]{name}[/{status_color}] "
                f"- 상태: [{status_color}]{status}[/{status_color}] "
                f"| 헬스: [{health_color}]{health}[/{health_color}]"
            )

            if error_count > 0:
                line += f" | [red]오류: {error_count}회[/red]"

            lines.append(line)

        return "\n".join(lines)

    def format_monitor_table(self, monitors: Dict[str, Any]) -> Table:
        """모니터 상태를 테이블로 포맷팅합니다.

        Args:
            monitors: 모니터 상태 딕셔너리

        Returns:
            Rich Table 객체
        """
        table = Table(
            title="모니터 상태",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            border_style="cyan",
        )

        table.add_column("모니터", style="cyan", no_wrap=True)
        table.add_column("상태", justify="center")
        table.add_column("헬스", justify="center")
        table.add_column("재시작", justify="right")
        table.add_column("오류", justify="right")
        table.add_column("마지막 체크", style="dim")

        for name, info in monitors.items():
            status = info.get("status", "unknown")
            health = info.get("health", "unknown")
            restart_count = info.get("restart_count", 0)
            error_count = info.get("error_count", 0)
            last_check = info.get("last_check")

            # 상태 포맷팅
            status_emoji = self._get_status_emoji(status)
            status_color = self._get_status_color(status)
            status_text = f"{status_emoji} [{status_color}]{status}[/{status_color}]"

            # 헬스 포맷팅
            health_emoji = self._get_health_emoji(health)
            health_color = self._get_health_color(health)
            health_text = f"{health_emoji} [{health_color}]{health}[/{health_color}]"

            # 시간 포맷팅
            time_text = self.format_datetime(last_check) if last_check else "N/A"

            # 오류 색상
            error_style = "red" if error_count > 0 else "green"

            table.add_row(
                name,
                status_text,
                health_text,
                str(restart_count),
                f"[{error_style}]{error_count}[/{error_style}]",
                time_text,
            )

        return table

    # ------------------------------------------------------------------
    # 시간 정보 포맷팅
    # ------------------------------------------------------------------
    def format_time_info(self, current_time: datetime, next_time: datetime = None) -> str:
        """시간 정보를 포맷팅합니다.

        Args:
            current_time: 현재 시간
            next_time: 다음 시간 (선택)

        Returns:
            포맷팅된 문자열
        """
        # KST로 변환
        if current_time.tzinfo is None:
            current_time = pytz.utc.localize(current_time)
        current_kst = current_time.astimezone(self.KST)

        lines = [
            f"🕐 [cyan]현재 시간:[/cyan] {current_kst.strftime('%Y-%m-%d %H:%M:%S KST')}"
        ]

        if next_time:
            if next_time.tzinfo is None:
                next_time = pytz.utc.localize(next_time)
            next_kst = next_time.astimezone(self.KST)

            # 남은 시간 계산
            time_diff = next_time - current_time
            remaining = self._format_timedelta(time_diff)

            lines.append(
                f"⏰ [yellow]다음 실행:[/yellow] {next_kst.strftime('%Y-%m-%d %H:%M:%S KST')} "
                f"[dim]({remaining} 후)[/dim]"
            )

        return "\n".join(lines)

    def format_datetime(self, dt: datetime, include_seconds: bool = True) -> str:
        """datetime을 포맷팅합니다.

        Args:
            dt: datetime 객체
            include_seconds: 초 포함 여부

        Returns:
            포맷팅된 문자열
        """
        if dt is None:
            return "N/A"

        # KST로 변환
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        dt_kst = dt.astimezone(self.KST)

        fmt = "%Y-%m-%d %H:%M:%S" if include_seconds else "%Y-%m-%d %H:%M"
        return dt_kst.strftime(fmt)

    def format_uptime(self, start_time: datetime) -> str:
        """가동 시간을 포맷팅합니다.

        Args:
            start_time: 시작 시간

        Returns:
            포맷팅된 문자열
        """
        if start_time is None:
            return "N/A"

        now = datetime.utcnow()
        if start_time.tzinfo:
            now = pytz.utc.localize(now)

        uptime = now - start_time
        return self._format_timedelta(uptime)

    # ------------------------------------------------------------------
    # 시스템 리소스 포맷팅
    # ------------------------------------------------------------------
    def format_system_resources(self, resources: Dict[str, Any]) -> str:
        """시스템 리소스를 포맷팅합니다.

        Args:
            resources: 리소스 정보 딕셔너리
                {
                    "cpu_percent": 45.2,
                    "memory_percent": 62.8,
                    "disk_percent": 78.5,
                    ...
                }

        Returns:
            포맷팅된 문자열
        """
        lines = []

        # CPU
        cpu = resources.get("cpu_percent", 0)
        cpu_bar = self._create_progress_bar(cpu, 100)
        cpu_color = self._get_resource_color(cpu)
        lines.append(f"💻 [cyan]CPU:[/cyan] [{cpu_color}]{cpu:.1f}%[/{cpu_color}] {cpu_bar}")

        # Memory
        memory = resources.get("memory_percent", 0)
        memory_bar = self._create_progress_bar(memory, 100)
        memory_color = self._get_resource_color(memory)
        lines.append(f"🧠 [cyan]메모리:[/cyan] [{memory_color}]{memory:.1f}%[/{memory_color}] {memory_bar}")

        # Disk
        disk = resources.get("disk_percent", 0)
        disk_bar = self._create_progress_bar(disk, 100)
        disk_color = self._get_resource_color(disk)
        lines.append(f"💾 [cyan]디스크:[/cyan] [{disk_color}]{disk:.1f}%[/{disk_color}] {disk_bar}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 오류 메시지 포맷팅
    # ------------------------------------------------------------------
    def format_error_message(self, error: Exception, context: str = "") -> str:
        """오류 메시지를 포맷팅합니다.

        Args:
            error: 오류 객체
            context: 오류 컨텍스트

        Returns:
            포맷팅된 문자열
        """
        error_type = type(error).__name__
        error_msg = str(error)

        lines = [
            f"[red bold]오류 발생:[/red bold] {error_type}"
        ]

        if context:
            lines.append(f"[yellow]컨텍스트:[/yellow] {context}")

        lines.append(f"[red]메시지:[/red] {error_msg}")

        return "\n".join(lines)

    def format_success_message(self, action: str, details: Dict[str, Any] = None) -> str:
        """성공 메시지를 포맷팅합니다.

        Args:
            action: 수행한 작업
            details: 상세 정보 딕셔너리

        Returns:
            포맷팅된 문자열
        """
        lines = [
            f"✅ [green bold]{action} 성공![/green bold]"
        ]

        if details:
            for key, value in details.items():
                lines.append(f"  • [cyan]{key}:[/cyan] {value}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 테이블 포맷팅
    # ------------------------------------------------------------------
    def format_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        title: str = None
    ) -> Table:
        """테이블을 생성합니다.

        Args:
            headers: 헤더 리스트
            rows: 데이터 행 리스트
            title: 테이블 제목

        Returns:
            Rich Table 객체
        """
        table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            border_style="cyan",
        )

        for header in headers:
            table.add_column(header)

        for row in rows:
            table.add_row(*[str(cell) for cell in row])

        return table

    # ------------------------------------------------------------------
    # 내부 도우미
    # ------------------------------------------------------------------
    def _get_status_emoji(self, status: str) -> str:
        """상태 이모지를 반환합니다."""
        status_lower = status.lower()
        if "running" in status_lower:
            return "🔄"
        elif "stopped" in status_lower:
            return "⏹️"
        elif "error" in status_lower:
            return "❌"
        elif "starting" in status_lower:
            return "🚀"
        elif "stopping" in status_lower:
            return "⏸️"
        else:
            return "❓"

    def _get_health_emoji(self, health: str) -> str:
        """헬스 이모지를 반환합니다."""
        health_lower = health.lower()
        if "healthy" in health_lower:
            return "✅"
        elif "degraded" in health_lower:
            return "⚠️"
        elif "unhealthy" in health_lower:
            return "❌"
        else:
            return "❓"

    def _get_status_color(self, status: str) -> str:
        """상태 색상을 반환합니다."""
        status_lower = status.lower()
        if "running" in status_lower:
            return "green"
        elif "stopped" in status_lower:
            return "yellow"
        elif "error" in status_lower:
            return "red"
        else:
            return "white"

    def _get_health_color(self, health: str) -> str:
        """헬스 색상을 반환합니다."""
        health_lower = health.lower()
        if "healthy" in health_lower:
            return "green"
        elif "degraded" in health_lower:
            return "yellow"
        elif "unhealthy" in health_lower:
            return "red"
        else:
            return "white"

    def _get_resource_color(self, percent: float) -> str:
        """리소스 사용률 색상을 반환합니다."""
        if percent < 50:
            return "green"
        elif percent < 80:
            return "yellow"
        else:
            return "red"

    def _create_progress_bar(self, current: float, total: float, length: int = 20) -> str:
        """프로그레스 바를 생성합니다."""
        if total == 0:
            return "░" * length

        filled = int(length * current / total)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"

    def _format_timedelta(self, td: timedelta) -> str:
        """timedelta를 포맷팅합니다."""
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 0:
            return "0초"

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}일")
        if hours > 0:
            parts.append(f"{hours}시간")
        if minutes > 0:
            parts.append(f"{minutes}분")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}초")

        return " ".join(parts)


# 편의 함수
def create_formatter() -> StatusFormatter:
    """StatusFormatter 인스턴스를 생성합니다."""
    return StatusFormatter()
