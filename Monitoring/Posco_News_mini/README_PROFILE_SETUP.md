# POSCO 뉴스 모니터 - 프로필 이미지 설정 가이드

## 🎨 봇 프로필 이미지 설정 방법

### 1. 이미지 파일 준비
- 제공된 POSCO 로고 이미지를 `posco-logo.png` 파일명으로 저장
- 이 폴더(`Monitoring/Posco_News_mini/`)에 저장

### 2. GitHub에 커밋 및 푸시
```bash
git add Monitoring/Posco_News_mini/posco-logo.png
git commit -m "Add POSCO logo for bot profile"
git push origin main
```

### 3. 설정 확인
- `config.py`에 이미 설정된 GitHub Raw URL:
```
https://raw.githubusercontent.com/shuserker/infomax_api/main/Monitoring/Posco_News_mini/posco-logo.png
```

### 4. 테스트
```bash
python run_monitor.py 6
```

## ✅ 완료 후 효과
- 모든 Dooray 알림에서 POSCO 로고가 봇 프로필 이미지로 표시됩니다
- 브랜딩 일관성 확보
- 전문적인 알림 시스템 구축

## 🔧 문제 해결
- 이미지가 표시되지 않는 경우: GitHub에 파일이 정상 업로드되었는지 확인
- URL 직접 접근 테스트: 브라우저에서 Raw URL 접근해보기