@echo off
REM GitHub Pages 자동 배포 스크립트 (Windows)
REM 새로운 리포트가 생성될 때마다 gh-pages 브랜치에 자동 배포

echo 🚀 GitHub Pages 배포 시작...

REM 현재 브랜치 저장
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

REM docs 폴더 확인
if not exist "docs" (
    echo ❌ docs 폴더가 없습니다.
    exit /b 1
)

REM publish 브랜치로 전환
git checkout publish

REM 임시 리포트 파일이 있으면 reports 폴더로 복사
if exist "%TEMP_REPORT_FILE%" (
    if not exist "reports" mkdir reports
    copy "%TEMP_REPORT_FILE%" "reports\%REPORT_FILENAME%"
)

REM 변경사항 커밋
git add .
git commit -m "🚀 자동 배포: %date% %time%"

REM GitHub에 푸시
git push origin publish

REM 원래 브랜치로 복귀
git checkout %CURRENT_BRANCH%

echo ✅ GitHub Pages 배포 완료!
echo 🌐 URL: https://shuserker.github.io/infomax_api/