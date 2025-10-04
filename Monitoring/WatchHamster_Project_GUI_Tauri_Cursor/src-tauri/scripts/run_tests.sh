#!/bin/bash

# Tauri 백엔드 테스트 실행 스크립트

echo "🦀 Tauri 백엔드 테스트 시작"
echo "================================"

# 현재 디렉토리를 src-tauri로 변경
cd "$(dirname "$0")/.."

# 환경 변수 설정
export RUST_LOG=debug
export RUST_BACKTRACE=1

echo "📋 테스트 환경 정보:"
echo "- Rust 버전: $(rustc --version)"
echo "- Cargo 버전: $(cargo --version)"
echo "- 현재 디렉토리: $(pwd)"
echo ""

# 1. 코드 포맷 확인
echo "🎨 코드 포맷 확인 중..."
if cargo fmt --check; then
    echo "✅ 코드 포맷이 올바릅니다"
else
    echo "❌ 코드 포맷을 수정해주세요: cargo fmt"
    exit 1
fi
echo ""

# 2. Clippy 린트 검사
echo "🔍 Clippy 린트 검사 중..."
if cargo clippy --all-targets --all-features -- -D warnings; then
    echo "✅ Clippy 검사 통과"
else
    echo "❌ Clippy 경고를 수정해주세요"
    exit 1
fi
echo ""

# 3. 단위 테스트 실행
echo "🧪 단위 테스트 실행 중..."
if cargo test --lib --verbose; then
    echo "✅ 단위 테스트 통과"
else
    echo "❌ 단위 테스트 실패"
    exit 1
fi
echo ""

# 4. 통합 테스트 실행
echo "🔗 통합 테스트 실행 중..."
if cargo test --test integration_tests --verbose; then
    echo "✅ 통합 테스트 통과"
else
    echo "❌ 통합 테스트 실패"
    exit 1
fi
echo ""

# 5. 문서 테스트 실행
echo "📚 문서 테스트 실행 중..."
if cargo test --doc; then
    echo "✅ 문서 테스트 통과"
else
    echo "❌ 문서 테스트 실패"
    exit 1
fi
echo ""

# 6. 빌드 테스트
echo "🔨 빌드 테스트 실행 중..."
if cargo build --release; then
    echo "✅ 릴리스 빌드 성공"
else
    echo "❌ 릴리스 빌드 실패"
    exit 1
fi
echo ""

# 7. 벤치마크 실행 (선택적)
if [ "$1" = "--bench" ]; then
    echo "⚡ 성능 벤치마크 실행 중..."
    if cargo bench; then
        echo "✅ 벤치마크 완료"
        echo "📊 벤치마크 결과는 target/criterion/report/index.html에서 확인할 수 있습니다"
    else
        echo "❌ 벤치마크 실행 실패"
        exit 1
    fi
    echo ""
fi

# 8. 테스트 커버리지 (선택적)
if [ "$1" = "--coverage" ]; then
    echo "📊 테스트 커버리지 측정 중..."
    if command -v cargo-tarpaulin &> /dev/null; then
        if cargo tarpaulin --out Html --output-dir target/coverage; then
            echo "✅ 커버리지 측정 완료"
            echo "📈 커버리지 리포트는 target/coverage/tarpaulin-report.html에서 확인할 수 있습니다"
        else
            echo "❌ 커버리지 측정 실패"
            exit 1
        fi
    else
        echo "⚠️  cargo-tarpaulin이 설치되지 않았습니다"
        echo "   설치 명령어: cargo install cargo-tarpaulin"
    fi
    echo ""
fi

echo "🎉 모든 테스트가 성공적으로 완료되었습니다!"
echo ""
echo "📋 테스트 요약:"
echo "- ✅ 코드 포맷 검사"
echo "- ✅ Clippy 린트 검사"
echo "- ✅ 단위 테스트"
echo "- ✅ 통합 테스트"
echo "- ✅ 문서 테스트"
echo "- ✅ 릴리스 빌드"

if [ "$1" = "--bench" ]; then
    echo "- ✅ 성능 벤치마크"
fi

if [ "$1" = "--coverage" ]; then
    echo "- ✅ 테스트 커버리지"
fi

echo ""
echo "🚀 Tauri 백엔드가 프로덕션 준비 완료되었습니다!"