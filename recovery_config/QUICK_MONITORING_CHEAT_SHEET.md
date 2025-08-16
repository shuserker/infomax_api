# 🚀 POSCO 시스템 모니터링 치트시트

## ⚡ 매일 5분 체크 (필수!)

### 🍎 Mac 사용자
```bash
cd recovery_config
python3 comprehensive_system_integration_test.py
```

### 🪟 Windows 사용자
```cmd
cd recovery_config
python comprehensive_system_integration_test.py
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
ls recovery_config/  # Mac
dir recovery_config\  # Windows
```

### Discord 메시지 안 옴
```bash
# 워치햄스터 재시작
python3 start_watchhamster_monitor.py  # Mac
python start_watchhamster_monitor.py   # Windows
```

## 📞 긴급 연락처
**1차**: [담당자] - [전화번호]  
**2차**: [부담당자] - [전화번호]

## 📝 보고 양식
```
[긴급] POSCO 시스템 문제
시간: MM-DD HH:MM
결과: X/8 (XX%)
오류: [메시지 복사]
```

---
**🎯 의심스러우면 연락하세요! 정상이면 건드리지 마세요!**