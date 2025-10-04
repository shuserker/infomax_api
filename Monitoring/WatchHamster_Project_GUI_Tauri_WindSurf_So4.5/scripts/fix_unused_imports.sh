#!/bin/bash

# 미사용 import 자동 제거 스크립트

echo "🔧 미사용 import 제거 시작..."
echo "================================"

cd "$(dirname "$0")/.."

# ESLint로 자동 수정
echo "1. ESLint 자동 수정 실행..."
npm run lint -- --fix 2>&1 | grep -E "(✓|✖|error|warning)" | head -20

# TypeScript 타입 체크
echo ""
echo "2. TypeScript 타입 체크..."
npm run type-check 2>&1 | grep -E "error TS" | wc -l | xargs -I {} echo "타입 에러: {}개"

# 결과 요약
echo ""
echo "================================"
echo "✅ 자동 수정 완료"
echo ""
echo "남은 작업:"
echo "- 수동으로 수정이 필요한 타입 에러 확인"
echo "- npm run type-check 실행하여 확인"
