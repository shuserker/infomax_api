# 🏭 POSCO 뉴스 알림 시스템

5가지 BOT 타입으로 구성된 POSCO 뉴스 통합 알림 시스템입니다.

## 🚀 빠른 시작

### Windows
```bash
🚀POSCO_메인_알림_시작.bat
```

### macOS/Linux
```bash
python3 posco_main_notifier.py
```

## 📊 5가지 BOT 타입

1. **🏭 POSCO 뉴스 비교알림 BOT** - 영업일 비교 분석
2. **📊 POSCO 뉴스 📊 BOT** - 일일 통합 분석 리포트
3. **🔔 POSCO 뉴스 🔔 BOT** - 데이터 갱신 상태 (동적 제목)
4. **✅ POSCO 뉴스 ✅ BOT** - 정시 발행 알림
5. **⏰ POSCO 뉴스 ⏰ BOT** - 지연 발행 알림

## 📁 핵심 파일

- `posco_main_notifier.py` - 메인 알림 시스템
- `historical_data_collector.py` - 과거 데이터 수집기
- `config.py` - 설정 파일
- `📋POSCO_시스템_유지보수_메뉴얼.md` - 상세 유지보수 가이드

## 🔧 설정

1. `config.py`에서 Dooray 웹훅 URL 설정
2. 필요시 `python3 historical_data_collector.py`로 과거 데이터 수집
3. 시스템 시작

## 📋 유지보수

자세한 유지보수 방법은 `📋POSCO_시스템_유지보수_메뉴얼.md`를 참조하세요.

## 🛑 시스템 중지

- Windows: `🛑POSCO_메인_알림_중지.bat`
- 또는 실행 중인 터미널에서 `Ctrl+C`

---

**업데이트**: 2025-08-05