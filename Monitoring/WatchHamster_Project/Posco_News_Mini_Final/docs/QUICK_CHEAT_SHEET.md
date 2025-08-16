# 🚀 POSCO 뉴스 시스템 모니터링 치트시트

## ⚡ 매일 5분 체크 (필수!)

### 🍎 Mac 사용자
```bash
# 포스코 프로젝트 폴더로 이동
cd Monitoring/WatchHamster_Project/Posco_News_Mini_Final

# 전체 시스템 테스트 (가장 중요!)
python3 scripts/system_test.py

# 간단한 통합 테스트
python3 scripts/simple_integration_test.py

# 포스코 모듈 개별 테스트
python3 scripts/test_posco_modules.py
```

### 🪟 Windows 사용자
```cmd
# 포스코 프로젝트 폴더로 이동
cd Monitoring\WatchHamster_Project\Posco_News_Mini_Final

# 전체 시스템 테스트 (가장 중요!)
python scripts/system_test.py

# 간단한 통합 테스트
python scripts/simple_integration_test.py

# 포스코 모듈 개별 테스트
python scripts/test_posco_modules.py
```

## 🎯 결과 판단

### ✅ 정상 (아무것도 안 해도 됨)
```
🎯 전체 성공률: 100.0% (8/8)
테스트 실행 시간: 0.XX초
```

### ⚠️ 주의 (관찰 필요)
```
🎯 전체 성공률: 75-99% (6-7/8)
```
→ 내일 다시 체크, 3일 연속 문제 시 연락

### 🚨 긴급 (즉시 연락!)
```
🎯 전체 성공률: 75% 미만 (5/8 이하)
또는 실행 자체가 안 됨
```
→ 담당자 즉시 연락: [전화번호]

## 🔧 간단 문제해결

### "python 명령어 없음"
- Mac: `python3` 사용
- Windows: Python 재설치

### "폴더 없음"
```bash
# 올바른 위치 확인
ls Monitoring/WatchHamster_Project/Posco_News_Mini_Final/  # Mac
dir Monitoring\WatchHamster_Project\Posco_News_Mini_Final\  # Windows
```

### "모듈을 찾을 수 없음"
```bash
# 워치햄스터 공통 모듈 경로 확인
ls ../../core/  # Mac
dir ..\..\core\  # Windows

# 포스코 프로젝트 폴더에 있는지 확인
pwd  # Mac
cd   # Windows
```

### Discord 메시지 안 옴
```bash
# 웹훅 모듈 테스트
python3 core/webhook_sender.py --test  # Mac
python core/webhook_sender.py --test   # Windows
```

### 워치햄스터 연동 문제
```bash
# 워치햄스터 프로젝트 루트로 이동
cd ../../

# 워치햄스터에서 포스코 프로젝트 감지 확인
python3 scripts/start_monitoring.py --list-projects  # Mac
python scripts/start_monitoring.py --list-projects   # Windows

# 워치햄스터-포스코 통합 테스트
python3 scripts/watchhamster_posco_integration_test.py  # Mac
python scripts/watchhamster_posco_integration_test.py   # Windows
```

## 📞 긴급 연락처
**1차**: [담당자] - [전화번호]  
**2차**: [부담당자] - [전화번호]

## 📝 보고 양식
```
[긴급] POSCO 뉴스 시스템 문제
시간: MM-DD HH:MM
결과: X/8 (XX%)
오류: [메시지 복사]
```

## 🚀 주간 체크 (워치햄스터 연동)

### 워치햄스터 통합 테스트 (주 1회)
```bash
# 워치햄스터 프로젝트 루트로 이동
cd ../../

# 최종 통합 테스트 실행
python3 scripts/final_integration_test.py  # Mac
python scripts/final_integration_test.py   # Windows

# 워치햄스터-포스코 연동 테스트
python3 scripts/watchhamster_posco_integration_test.py  # Mac
python scripts/watchhamster_posco_integration_test.py   # Windows
```

### 결과 판단
- ✅ **정상**: 모든 테스트 통과
- ⚠️ **주의**: 일부 테스트 실패 (관찰 필요)
- 🚨 **긴급**: 다수 테스트 실패 (즉시 연락)

---
**🎯 의심스러우면 연락하세요! 정상이면 건드리지 마세요!**  
**🐹 워치햄스터가 건강하면 포스코도 건강합니다!**