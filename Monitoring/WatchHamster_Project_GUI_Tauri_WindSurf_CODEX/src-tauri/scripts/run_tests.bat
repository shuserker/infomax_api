@echo off
setlocal enabledelayedexpansion

REM Tauri 백엔드 테스트 실행 스크립트 (Windows)

echo 🦀 Tauri 백엔드 테스트 시작
echo ================================

REM 현재 디렉토리를 src-tauri로 변경
cd /d "%~dp0\.."

REM 환경 변수 설정
set RUST_LOG=debug
set RUST_BACKTRACE=1

echo 📋 테스트 환경 정보:
for /f "tokens=*" %%i in ('rustc --version') do echo - Rust 버전: %%i
for /f "tokens=*" %%i in ('cargo --version') do echo - Cargo 버전: %%i
echo - 현재 디렉토리: %CD%
echo.

REM 1. 코드 포맷 확인
echo 🎨 코드 포맷 확인 중...
cargo fmt --check
if !errorlevel! neq 0 (
    echo ❌ 코드 포맷을 수정해주세요: cargo fmt
    exit /b 1
)
echo ✅ 코드 포맷이 올바릅니다
echo.

REM 2. Clippy 린트 검사
echo 🔍 Clippy 린트 검사 중...
cargo clippy --all-targets --all-features -- -D warnings
if !errorlevel! neq 0 (
    echo ❌ Clippy 경고를 수정해주세요
    exit /b 1
)
echo ✅ Clippy 검사 통과
echo.

REM 3. 단위 테스트 실행
echo 🧪 단위 테스트 실행 중...
cargo test --lib --verbose
if !errorlevel! neq 0 (
    echo ❌ 단위 테스트 실패
    exit /b 1
)
echo ✅ 단위 테스트 통과
echo.

REM 4. 통합 테스트 실행
echo 🔗 통합 테스트 실행 중...
cargo test --test integration_tests --verbose
if !errorlevel! neq 0 (
    echo ❌ 통합 테스트 실패
    exit /b 1
)
echo ✅ 통합 테스트 통과
echo.

REM 5. 문서 테스트 실행
echo 📚 문서 테스트 실행 중...
cargo test --doc
if !errorlevel! neq 0 (
    echo ❌ 문서 테스트 실패
    exit /b 1
)
echo ✅ 문서 테스트 통과
echo.

REM 6. 빌드 테스트
echo 🔨 빌드 테스트 실행 중...
cargo build --release
if !errorlevel! neq 0 (
    echo ❌ 릴리스 빌드 실패
    exit /b 1
)
echo ✅ 릴리스 빌드 성공
echo.

REM 7. 벤치마크 실행 (선택적)
if "%1"=="--bench" (
    echo ⚡ 성능 벤치마크 실행 중...
    cargo bench
    if !errorlevel! neq 0 (
        echo ❌ 벤치마크 실행 실패
        exit /b 1
    )
    echo ✅ 벤치마크 완료
    echo 📊 벤치마크 결과는 target\criterion\report\index.html에서 확인할 수 있습니다
    echo.
)

REM 8. 테스트 커버리지 (선택적)
if "%1"=="--coverage" (
    echo 📊 테스트 커버리지 측정 중...
    where cargo-tarpaulin >nul 2>&1
    if !errorlevel! equ 0 (
        cargo tarpaulin --out Html --output-dir target\coverage
        if !errorlevel! neq 0 (
            echo ❌ 커버리지 측정 실패
            exit /b 1
        )
        echo ✅ 커버리지 측정 완료
        echo 📈 커버리지 리포트는 target\coverage\tarpaulin-report.html에서 확인할 수 있습니다
    ) else (
        echo ⚠️  cargo-tarpaulin이 설치되지 않았습니다
        echo    설치 명령어: cargo install cargo-tarpaulin
    )
    echo.
)

echo 🎉 모든 테스트가 성공적으로 완료되었습니다!
echo.
echo 📋 테스트 요약:
echo - ✅ 코드 포맷 검사
echo - ✅ Clippy 린트 검사
echo - ✅ 단위 테스트
echo - ✅ 통합 테스트
echo - ✅ 문서 테스트
echo - ✅ 릴리스 빌드

if "%1"=="--bench" (
    echo - ✅ 성능 벤치마크
)

if "%1"=="--coverage" (
    echo - ✅ 테스트 커버리지
)

echo.
echo 🚀 Tauri 백엔드가 프로덕션 준비 완료되었습니다!

pause