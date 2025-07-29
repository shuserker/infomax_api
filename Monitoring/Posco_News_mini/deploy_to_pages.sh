#!/bin/bash

# GitHub Pages 자동 배포 스크립트
# 새로운 리포트가 생성될 때마다 gh-pages 브랜치에 자동 배포

echo "🚀 GitHub Pages 배포 시작..."

# 현재 브랜치 저장
CURRENT_BRANCH=$(git branch --show-current)

# docs 폴더 변경사항 확인
if [ ! -d "docs" ]; then
    echo "❌ docs 폴더가 없습니다."
    exit 1
fi

# publish 브랜치로 전환
git checkout publish

# main 브랜치에서 docs 폴더 내용 가져오기
git checkout main -- Monitoring/Posco_News_mini/docs

# docs 내용을 루트로 이동
cp -r Monitoring/Posco_News_mini/docs/* .
rm -rf Monitoring

# 변경사항 커밋
git add .
git commit -m "🚀 자동 배포: $(date '+%Y-%m-%d %H:%M:%S')"

# GitHub에 푸시
git push origin publish

# 원래 브랜치로 복귀
git checkout $CURRENT_BRANCH

echo "✅ GitHub Pages 배포 완료!"
echo "🌐 URL: https://shuserker.github.io/infomax_api/"