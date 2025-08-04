@echo off
chcp 65001 > nul
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🔄 Git 최신 커밋 덮어씌우기                             ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🔍 현재 변경사항 확인 중...
git status --porcelain
echo.
echo ⚠️ 최신 커밋에 덮어씌웁니다. 계속하시겠습니까?
set /p confirm=Y/N: 
if /i "%confirm%" neq "Y" (
    echo ❌ 취소되었습니다.
    pause
    exit /b
)
echo.
echo 📦 1단계: 변경사항 스테이징...
git add .
if %errorlevel% neq 0 (
    echo ❌ 스테이징 실패
    pause
    exit /b 1
)
echo ✅ 스테이징 완료
echo.
echo 🔄 2단계: 최신 커밋에 덮어씌우기...
git commit --amend --no-edit
if %errorlevel% neq 0 (
    echo ❌ 커밋 덮어씌우기 실패
    pause
    exit /b 1
)
echo ✅ 커밋 덮어씌우기 완료
echo.
echo 🚀 3단계: 원격 저장소에 강제 푸시...
git push --force-with-lease origin main
if %errorlevel% neq 0 (
    echo ❌ 푸시 실패
    pause
    exit /b 1
)
echo ✅ 푸시 완료
echo.
echo 🎉 Git 덮어씌우기 완료!
echo 📋 최신 커밋 정보:
git log --oneline -1
echo.
pause