#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WatchHamster 콘솔 UI 모듈

`design.md`에서 정의한 `ColorfulConsoleUI` 사양을 충족하도록 구현했습니다.
- 컬러풀한 터미널 출력 (rich 라이브러리 활용)
- 이모지 지원
- 크로스 플랫폼 호환성 (Windows/Mac/Linux)
- 다양한 스타일 및 레이아웃
"""

from __future__ import annotations

import sys
from typing import Dict, List, Optional, Any
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.style import Style


class UIStyle(Enum):
    """UI 스타일"""
    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    HEADER = "header"


class ColorfulConsoleUI:
    """컬러풀한 콘솔 UI 제공"""

    # 이모지 맵
    EMOJI = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "running": "🔄",
        "stopped": "⏹️",
        "monitoring": "📊",
        "clock": "🕐",
        "rocket": "🚀",
        "check": "✓",
        "cross": "✗",
        "arrow_right": "→",
        "arrow_down": "↓",
        "bullet": "•",
        "star": "★",
        "gear": "⚙️",
        "fire": "🔥",
        "chart": "📈",
    }

    # 스타일 맵
    STYLES = {
        UIStyle.DEFAULT: Style(color="white"),
        UIStyle.SUCCESS: Style(color="green", bold=True),
        UIStyle.WARNING: Style(color="yellow", bold=True),
        UIStyle.ERROR: Style(color="red", bold=True),
        UIStyle.INFO: Style(color="cyan"),
        UIStyle.HEADER: Style(color="magenta", bold=True),
    }

    def __init__(self, enable_colors: bool = True, enable_emojis: bool = True):
        """
        Args:
            enable_colors: 색상 활성화 여부
            enable_emojis: 이모지 활성화 여부
        """
        self.console = Console(
            force_terminal=True,
            color_system="auto" if enable_colors else None,
            emoji=enable_emojis,
        )
        self.colors_enabled = enable_colors
        self.emoji_enabled = enable_emojis

    # ------------------------------------------------------------------
    # 기본 출력
    # ------------------------------------------------------------------
    def print_header(self, title: str, style: str = "default", subtitle: str = None):
        """헤더를 출력합니다.

        Args:
            title: 헤더 제목
            style: 스타일 (default, success, warning, error, info, header)
            subtitle: 부제목 (선택)
        """
        try:
            ui_style = UIStyle(style)
        except ValueError:
            ui_style = UIStyle.DEFAULT

        # 제목 텍스트 생성
        title_text = Text(title, style=self.STYLES[ui_style])
        
        # 패널 생성
        panel_content = title_text
        if subtitle:
            panel_content = Text.assemble(
                (title, self.STYLES[ui_style]),
                "\n",
                (subtitle, "dim"),
            )

        # border_style은 문자열로 전달
        border_color = "magenta" if ui_style == UIStyle.HEADER else "green" if ui_style == UIStyle.SUCCESS else "red" if ui_style == UIStyle.ERROR else "yellow" if ui_style == UIStyle.WARNING else "cyan" if ui_style == UIStyle.INFO else "white"
        
        panel = Panel(
            panel_content,
            box=box.DOUBLE,
            border_style=border_color,
            padding=(1, 2),
        )
        
        self.console.print(panel)

    def print_status(self, status: Dict[str, Any], highlight: bool = False):
        """상태 정보를 출력합니다.

        Args:
            status: 상태 딕셔너리
            highlight: 하이라이트 여부
        """
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED if highlight else box.SIMPLE,
            border_style="cyan" if highlight else "white",
        )
        
        table.add_column("항목", style="cyan", no_wrap=True)
        table.add_column("값", style="white")
        table.add_column("상태", justify="center")

        for key, value in status.items():
            # 상태 이모지 결정
            status_emoji = self._get_status_emoji(key, value)
            
            # 값 포맷팅
            formatted_value = self._format_value(value)
            
            table.add_row(
                key,
                formatted_value,
                status_emoji
            )

        self.console.print(table)

    def print_menu(self, options: List[str], current_selection: int = 0):
        """메뉴를 출력합니다.

        Args:
            options: 메뉴 옵션 리스트
            current_selection: 현재 선택된 인덱스
        """
        self.console.print("\n[bold cyan]메뉴 옵션:[/bold cyan]\n")
        
        for idx, option in enumerate(options, 1):
            prefix = f"{self.EMOJI['arrow_right']} " if idx - 1 == current_selection else "  "
            style = "bold yellow" if idx - 1 == current_selection else "white"
            
            self.console.print(f"{prefix}[{style}]{idx}. {option}[/{style}]")

    def print_separator(self, char: str = "=", length: int = 60, style: str = "dim"):
        """구분선을 출력합니다.

        Args:
            char: 구분선 문자
            length: 길이
            style: 스타일
        """
        separator = char * length
        self.console.print(f"[{style}]{separator}[/{style}]")

    def print_error(self, message: str, details: str = None):
        """오류 메시지를 출력합니다.

        Args:
            message: 오류 메시지
            details: 상세 정보 (선택)
        """
        emoji = self.EMOJI["error"] if self.emoji_enabled else "[ERROR]"
        
        error_text = Text.assemble(
            (f"{emoji} ", "red bold"),
            (message, "red"),
        )
        
        if details:
            error_text.append("\n")
            error_text.append(details, style="dim")

        panel = Panel(
            error_text,
            title="오류",
            border_style="red",
            box=box.ROUNDED,
        )
        
        self.console.print(panel)

    def print_success(self, message: str, details: str = None):
        """성공 메시지를 출력합니다.

        Args:
            message: 성공 메시지
            details: 상세 정보 (선택)
        """
        emoji = self.EMOJI["success"] if self.emoji_enabled else "[OK]"
        
        success_text = Text.assemble(
            (f"{emoji} ", "green bold"),
            (message, "green"),
        )
        
        if details:
            success_text.append("\n")
            success_text.append(details, style="dim")

        panel = Panel(
            success_text,
            title="성공",
            border_style="green",
            box=box.ROUNDED,
        )
        
        self.console.print(panel)

    def print_warning(self, message: str, details: str = None):
        """경고 메시지를 출력합니다.

        Args:
            message: 경고 메시지
            details: 상세 정보 (선택)
        """
        emoji = self.EMOJI["warning"] if self.emoji_enabled else "[WARN]"
        
        warning_text = Text.assemble(
            (f"{emoji} ", "yellow bold"),
            (message, "yellow"),
        )
        
        if details:
            warning_text.append("\n")
            warning_text.append(details, style="dim")

        panel = Panel(
            warning_text,
            title="경고",
            border_style="yellow",
            box=box.ROUNDED,
        )
        
        self.console.print(panel)

    def print_info(self, message: str, details: str = None):
        """정보 메시지를 출력합니다.

        Args:
            message: 정보 메시지
            details: 상세 정보 (선택)
        """
        emoji = self.EMOJI["info"] if self.emoji_enabled else "[INFO]"
        
        info_text = Text.assemble(
            (f"{emoji} ", "cyan bold"),
            (message, "cyan"),
        )
        
        if details:
            info_text.append("\n")
            info_text.append(details, style="dim")

        self.console.print(info_text)

    # ------------------------------------------------------------------
    # 고급 출력
    # ------------------------------------------------------------------
    def print_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        title: str = None,
        highlight_row: int = None
    ):
        """테이블을 출력합니다.

        Args:
            headers: 헤더 리스트
            rows: 데이터 행 리스트
            title: 테이블 제목 (선택)
            highlight_row: 하이라이트할 행 인덱스 (선택)
        """
        table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            border_style="cyan",
        )

        # 헤더 추가
        for header in headers:
            table.add_column(header, style="white")

        # 행 추가
        for idx, row in enumerate(rows):
            style = "yellow" if idx == highlight_row else None
            table.add_row(*[str(cell) for cell in row], style=style)

        self.console.print(table)

    def print_progress_summary(self, current: int, total: int, description: str):
        """진행 상황 요약을 출력합니다.

        Args:
            current: 현재 진행
            total: 전체
            description: 설명
        """
        percentage = (current / total * 100) if total > 0 else 0
        bar_length = 40
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        progress_text = Text.assemble(
            (f"{description}\n", "bold"),
            (f"[{bar}] ", "cyan"),
            (f"{current}/{total} ", "white"),
            (f"({percentage:.1f}%)", "dim"),
        )

        self.console.print(progress_text)

    def clear(self):
        """화면을 지웁니다."""
        self.console.clear()

    def print_banner(self, text: str):
        """배너를 출력합니다.

        Args:
            text: 배너 텍스트
        """
        banner = Panel(
            Text(text, justify="center", style="bold magenta"),
            box=box.DOUBLE_EDGE,
            border_style="magenta",
            padding=(1, 4),
        )
        self.console.print(banner)

    # ------------------------------------------------------------------
    # 내부 도우미
    # ------------------------------------------------------------------
    def _get_status_emoji(self, key: str, value: Any) -> str:
        """상태에 따른 이모지를 반환합니다."""
        if not self.emoji_enabled:
            return ""

        # 값 기반 판단
        if isinstance(value, bool):
            return self.EMOJI["success"] if value else self.EMOJI["error"]
        
        if isinstance(value, str):
            value_lower = value.lower()
            if "running" in value_lower or "active" in value_lower:
                return self.EMOJI["running"]
            elif "stopped" in value_lower or "inactive" in value_lower:
                return self.EMOJI["stopped"]
            elif "error" in value_lower or "failed" in value_lower:
                return self.EMOJI["error"]
            elif "success" in value_lower or "ok" in value_lower:
                return self.EMOJI["success"]
            elif "warning" in value_lower:
                return self.EMOJI["warning"]

        return self.EMOJI["info"]

    def _format_value(self, value: Any) -> str:
        """값을 포맷팅합니다."""
        if isinstance(value, bool):
            return "[green]예[/green]" if value else "[red]아니오[/red]"
        elif isinstance(value, (int, float)):
            return f"[yellow]{value}[/yellow]"
        elif value is None:
            return "[dim]N/A[/dim]"
        else:
            return str(value)


# 편의 함수
def create_ui(colors: bool = True, emojis: bool = True) -> ColorfulConsoleUI:
    """ColorfulConsoleUI 인스턴스를 생성합니다."""
    return ColorfulConsoleUI(enable_colors=colors, enable_emojis=emojis)
