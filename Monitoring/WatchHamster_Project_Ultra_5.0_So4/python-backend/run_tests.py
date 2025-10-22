#!/usr/bin/env python3
"""
단위 테스트 실행 스크립트
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_pytest(test_path: str = "tests/", verbose: bool = True, coverage: bool = False, markers: str = None):
    """pytest 실행"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if markers:
        cmd.extend(["-m", markers])
    
    cmd.append(test_path)
    
    print(f"테스트 실행 명령어: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n테스트가 사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")
        return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="WatchHamster 백엔드 단위 테스트 실행")
    
    parser.add_argument(
        "--test-type", 
        choices=["all", "unit", "api", "websocket", "posco", "integration"],
        default="all",
        help="실행할 테스트 타입"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="코드 커버리지 측정"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="상세 출력"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="특정 테스트 파일 실행"
    )
    
    args = parser.parse_args()
    
    print("🚀 WatchHamster 백엔드 단위 테스트 시작")
    print("=" * 60)
    
    # 테스트 경로 및 마커 설정
    test_path = "tests/"
    markers = None
    
    if args.file:
        test_path = f"tests/{args.file}"
    elif args.test_type != "all":
        markers = args.test_type
    
    # 테스트 실행
    success = run_pytest(
        test_path=test_path,
        verbose=args.verbose,
        coverage=args.coverage,
        markers=markers
    )
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())