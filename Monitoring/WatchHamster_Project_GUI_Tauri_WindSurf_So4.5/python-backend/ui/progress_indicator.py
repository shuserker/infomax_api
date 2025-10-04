#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WatchHamster 진행 표시기 모듈

비동기 작업의 진행 상황을 시각적으로 표시합니다.
- 스피너 애니메이션
- 프로그레스 바
- 실시간 상태 업데이트
"""

from __future__ import annotations

import asyncio
from typing import Optional
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
from rich.live import Live
from rich.text import Text


class ProgressIndicator:
    """진행 상황 표시기"""

    # 스피너 스타일
    SPINNER_STYLES = {
        "dots": "dots",
        "line": "line",
        "arc": "arc",
        "arrow": "arrow",
        "bounce": "bounce",
        "circle": "circleHalves",
        "moon": "moon",
        "runner": "runner",
        "pong": "pong",
        "shark": "shark",
        "dqpb": "dqpb",
    }

    def __init__(self, console: Optional[Console] = None):
        """
        Args:
            console: Rich Console 인스턴스 (None이면 새로 생성)
        """
        self.console = console or Console()
        self._progress: Optional[Progress] = None
        self._live: Optional[Live] = None
        self._spinner_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # 스피너
    # ------------------------------------------------------------------
    async def show_spinner(
        self,
        message: str,
        style: str = "dots",
        duration: Optional[float] = None
    ):
        """스피너를 표시합니다.

        Args:
            message: 표시할 메시지
            style: 스피너 스타일
            duration: 표시 시간 (None이면 수동 중지 필요)
        """
        spinner_style = self.SPINNER_STYLES.get(style, "dots")
        
        with self.console.status(f"[cyan]{message}[/cyan]", spinner=spinner_style):
            if duration:
                await asyncio.sleep(duration)
            else:
                # 수동 중지를 위해 무한 대기
                try:
                    await asyncio.sleep(float('inf'))
                except asyncio.CancelledError:
                    pass

    def start_spinner_sync(self, message: str, style: str = "dots"):
        """동기 방식으로 스피너를 시작합니다.

        Args:
            message: 표시할 메시지
            style: 스피너 스타일

        Returns:
            Live 컨텍스트 (with 문에서 사용)
        """
        spinner_style = self.SPINNER_STYLES.get(style, "dots")
        return self.console.status(f"[cyan]{message}[/cyan]", spinner=spinner_style)

    # ------------------------------------------------------------------
    # 프로그레스 바
    # ------------------------------------------------------------------
    def create_progress(
        self,
        show_time: bool = True,
        show_percentage: bool = True
    ) -> Progress:
        """프로그레스 바를 생성합니다.

        Args:
            show_time: 시간 정보 표시 여부
            show_percentage: 퍼센트 표시 여부

        Returns:
            Progress 객체
        """
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
        ]

        if show_percentage:
            columns.append(TaskProgressColumn())

        if show_time:
            columns.append(TimeElapsedColumn())
            columns.append(TimeRemainingColumn())

        return Progress(*columns, console=self.console)

    async def show_progress(
        self,
        tasks: list,
        description: str = "처리 중...",
        show_time: bool = True
    ):
        """프로그레스 바를 표시하며 작업을 실행합니다.

        Args:
            tasks: 실행할 비동기 작업 리스트
            description: 작업 설명
            show_time: 시간 정보 표시 여부
        """
        progress = self.create_progress(show_time=show_time)
        
        with progress:
            task_id = progress.add_task(description, total=len(tasks))
            
            for task in tasks:
                if asyncio.iscoroutine(task):
                    await task
                elif callable(task):
                    result = task()
                    if asyncio.iscoroutine(result):
                        await result
                
                progress.update(task_id, advance=1)

    def show_progress_sync(
        self,
        total: int,
        description: str = "처리 중..."
    ) -> tuple[Progress, int]:
        """동기 방식으로 프로그레스 바를 시작합니다.

        Args:
            total: 전체 작업 수
            description: 작업 설명

        Returns:
            (Progress 객체, task_id) 튜플
        """
        progress = self.create_progress()
        task_id = progress.add_task(description, total=total)
        return progress, task_id

    # ------------------------------------------------------------------
    # 다중 프로그레스
    # ------------------------------------------------------------------
    def create_multi_progress(self) -> Progress:
        """다중 프로그레스 바를 생성합니다.

        Returns:
            Progress 객체
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        )

    async def show_multi_progress(
        self,
        task_groups: dict,
        overall_description: str = "전체 진행"
    ):
        """다중 프로그레스 바를 표시합니다.

        Args:
            task_groups: {그룹명: [작업 리스트]} 형태의 딕셔너리
            overall_description: 전체 작업 설명
        """
        progress = self.create_multi_progress()
        
        with progress:
            # 전체 진행 태스크
            total_tasks = sum(len(tasks) for tasks in task_groups.values())
            overall_task = progress.add_task(
                overall_description,
                total=total_tasks
            )
            
            # 그룹별 태스크
            for group_name, tasks in task_groups.items():
                group_task = progress.add_task(
                    f"  └─ {group_name}",
                    total=len(tasks)
                )
                
                for task in tasks:
                    if asyncio.iscoroutine(task):
                        await task
                    elif callable(task):
                        result = task()
                        if asyncio.iscoroutine(result):
                            await result
                    
                    progress.update(group_task, advance=1)
                    progress.update(overall_task, advance=1)

    # ------------------------------------------------------------------
    # 간단한 진행 표시
    # ------------------------------------------------------------------
    def print_step(self, step: int, total: int, message: str):
        """단계별 진행 상황을 출력합니다.

        Args:
            step: 현재 단계
            total: 전체 단계
            message: 메시지
        """
        percentage = (step / total * 100) if total > 0 else 0
        emoji = "✓" if step == total else "→"
        
        text = Text.assemble(
            (f"{emoji} ", "green" if step == total else "cyan"),
            (f"[{step}/{total}] ", "yellow"),
            (f"({percentage:.0f}%) ", "dim"),
            (message, "white"),
        )
        
        self.console.print(text)

    def print_completion(self, message: str, elapsed_time: float = None):
        """완료 메시지를 출력합니다.

        Args:
            message: 완료 메시지
            elapsed_time: 소요 시간 (초)
        """
        text = Text.assemble(
            ("✅ ", "green bold"),
            (message, "green"),
        )
        
        if elapsed_time is not None:
            text.append(f" [dim]({elapsed_time:.2f}초 소요)[/dim]")
        
        self.console.print(text)

    # ------------------------------------------------------------------
    # 실시간 업데이트
    # ------------------------------------------------------------------
    def create_live_display(self, content) -> Live:
        """실시간 업데이트 디스플레이를 생성합니다.

        Args:
            content: 표시할 컨텐츠 (Text, Table 등)

        Returns:
            Live 객체
        """
        return Live(content, console=self.console, refresh_per_second=4)

    async def update_live_display(
        self,
        update_func,
        interval: float = 1.0,
        duration: Optional[float] = None
    ):
        """실시간으로 디스플레이를 업데이트합니다.

        Args:
            update_func: 업데이트 함수 (컨텐츠를 반환)
            interval: 업데이트 간격 (초)
            duration: 실행 시간 (None이면 수동 중지 필요)
        """
        initial_content = update_func()
        
        with self.create_live_display(initial_content) as live:
            start_time = asyncio.get_event_loop().time()
            
            try:
                while True:
                    await asyncio.sleep(interval)
                    
                    # 업데이트
                    new_content = update_func()
                    live.update(new_content)
                    
                    # 시간 제한 확인
                    if duration:
                        elapsed = asyncio.get_event_loop().time() - start_time
                        if elapsed >= duration:
                            break
                            
            except asyncio.CancelledError:
                pass

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------
    def clear_line(self):
        """현재 라인을 지웁니다."""
        self.console.print("\r" + " " * 80 + "\r", end="")

    def print_separator(self, char: str = "─", length: int = 60):
        """구분선을 출력합니다."""
        self.console.print(f"[dim]{char * length}[/dim]")


# 편의 함수
def create_indicator(console: Optional[Console] = None) -> ProgressIndicator:
    """ProgressIndicator 인스턴스를 생성합니다."""
    return ProgressIndicator(console=console)
