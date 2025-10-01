#!/bin/bash

# WatchHamster macOS GUI 실행 스크립트

echo "🐹 WatchHamster macOS GUI 실행기"
echo "=================================="

# 1. Homebrew 확인
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew가 설치되지 않았습니다."
    echo "📥 Homebrew 설치:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

echo "✅ Homebrew 설치됨"

# 2. Python-tk 설치 확인 및 설치
echo "🔍 Python-tk 확인 중..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "📦 Python-tk 설치 중..."
    brew install python-tk
    
    if [ $? -eq 0 ]; then
        echo "✅ Python-tk 설치 완료"
    else
        echo "❌ Python-tk 설치 실패"
        exit 1
    fi
else
    echo "✅ Python-tk 이미 설치됨"
fi

# 3. tkinter 테스트
echo "🖥️  tkinter 테스트 중..."
python3 -c "
import tkinter as tk
root = tk.Tk()
root.withdraw()  # 창 숨기기
root.quit()
print('✅ tkinter 정상 작동')
"

if [ $? -ne 0 ]; then
    echo "❌ tkinter 테스트 실패"
    exit 1
fi

# 4. 필요한 패키지 확인
echo "📦 필요한 패키지 확인 중..."
python3 -c "
try:
    import psutil
    print('✅ psutil 사용 가능')
except ImportError:
    print('❌ psutil 설치 필요: pip3 install psutil')
    exit(1)
"

# 5. WatchHamster GUI 실행
echo "🚀 WatchHamster GUI 시작..."
echo "GUI 창이 열리면 성공입니다!"

# 환경 변수 설정
export PYTHONPATH="."

# GUI 실행
python3 main_gui.py &

# 프로세스 ID 저장
GUI_PID=$!

echo "🎯 GUI 프로세스 ID: $GUI_PID"
echo "🛑 GUI 종료: kill $GUI_PID"

# 5초 후 상태 확인
sleep 5

if ps -p $GUI_PID > /dev/null; then
    echo "✅ WatchHamster GUI 실행 중!"
    echo "🖥️  GUI 창을 확인하세요."
else
    echo "❌ GUI 실행 실패"
    echo "🔧 백엔드 테스트: python3 test_headless.py"
fi

echo "=================================="
echo "🎊 설정 완료!"