# 🌍 POSCO WatchHamster v3.0 크로스 플랫폼 가이드

## 📱 지원 플랫폼

**POSCO WatchHamster v3.0**은 다음 플랫폼에서 완벽하게 작동합니다:

- 🖥️ **Windows 10/11** (배치 파일 + PowerShell)
- 🍎 **macOS** (Bash + Command 파일)
- 🐧 **Linux** (Bash 스크립트)

---

## 🖥️ Windows 버전

### 📁 **Windows 전용 파일들**

#### 🎛️ **제어센터**
- `🐹POSCO_WatchHamster_v3_제어센터.bat` - **v3.0 최신 제어센터**
- `🐹WatchHamster_총괄_관리_센터_v3.bat` - 기존 v3 제어센터
- `🎛️POSCO_제어센터_실행_v2.bat` - v2 제어센터

#### 🔧 **공통 라이브러리**
- `lib_wt_common.bat` - Windows 배치 공통 함수
- `lib_wt_common.ps1` - PowerShell 공통 함수
- `watchhamster_control_center.ps1` - PowerShell 제어센터
- `watchhamster_master_control.ps1` - PowerShell 마스터 제어

#### 🚀 **실행 스크립트**
- `🚀POSCO_메인_알림_시작_직접.bat` - 직접 실행
- `POSCO_시작.bat` - 간단 시작
- `PowerShell_진단.bat` - 시스템 진단

### 🎯 **Windows 사용법**

#### **1. 기본 실행 (권장)**
```cmd
# v3.0 최신 제어센터 실행
🐹POSCO_WatchHamster_v3_제어센터.bat
```

#### **2. PowerShell 실행**
```powershell
# PowerShell에서 실행
.\watchhamster_control_center.ps1
```

#### **3. 직접 실행**
```cmd
# WatchHamster 직접 시작
🚀POSCO_메인_알림_시작_직접.bat
```

### 🔧 **Windows 특별 기능**

- **한글 지원**: UTF-8 인코딩으로 완벽한 한글 표시
- **색상 터미널**: Windows Terminal에서 컬러 지원
- **작업 관리자 연동**: tasklist/taskkill 명령어 활용
- **배치 파일 최적화**: Windows 환경에 특화된 스크립트

---

## 🍎 macOS 버전

### 📁 **macOS 전용 파일들**

#### 🎛️ **제어센터**
- `🐹POSCO_WatchHamster_v3_제어센터.command` - **v3.0 최신 제어센터**
- `🎛️POSCO_제어센터_Mac실행.command` - 기존 Mac 제어센터
- `posco_control_mac.sh` - Mac 전용 제어 스크립트

#### 🔧 **공통 라이브러리**
- `lib_wt_common.sh` - Bash 공통 함수
- `watchhamster_control_center.sh` - Bash 제어센터
- `watchhamster_master_control.sh` - Bash 마스터 제어

#### 🚀 **실행 스크립트**
- `🚀POSCO_메인_알림_시작_직접.sh` - 직접 실행
- `migrate_to_v2.sh` - v3.0 마이그레이션

### 🎯 **macOS 사용법**

#### **1. 기본 실행 (권장)**
```bash
# v3.0 최신 제어센터 실행 (더블클릭 가능)
./.naming_backup/config_data_backup/watchhamster.log
```

#### **2. 터미널에서 실행**
```bash
# 터미널에서 직접 실행
bash .naming_backup/scripts/.naming_backup/scripts/watchhamster_control_center.sh
```

#### **3. 직접 실행**
```bash
# WatchHamster 직접 시작
bash .naming_backup/scripts/.naming_backup/scripts/🚀POSCO_메인_알림_시작_직접.sh
```

### 🔧 **macOS 특별 기능**

- **Finder 통합**: .command 파일로 더블클릭 실행 가능
- **컬러 터미널**: ANSI 색상 코드로 아름다운 인터페이스
- **Unix 명령어**: ps, kill, grep 등 Unix 도구 활용
- **권한 관리**: chmod로 실행 권한 자동 설정

---

## 🐧 Linux 버전

### 📁 **Linux 호환 파일들**

Linux는 macOS와 동일한 Bash 스크립트를 사용합니다:

- `watchhamster_control_center.sh` - 메인 제어센터
- `lib_wt_common.sh` - 공통 함수 라이브러리
- `migrate_to_v2.sh` - v3.0 마이그레이션
- 모든 Python 스크립트들 (크로스 플랫폼)

### 🎯 **Linux 사용법**

```bash
# 제어센터 실행
bash .naming_backup/scripts/.naming_backup/scripts/watchhamster_control_center.sh

# 직접 실행
python3 Monitoring/POSCO News/monitor_WatchHamster.py

# 마이그레이션
bash migrate_to_v2.sh
```

---

## 🔄 플랫폼별 차이점

### 📊 **기능 비교표**

| 기능 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 기본 모니터링 | ✅ | ✅ | ✅ |
| 컬러 터미널 | ✅ | ✅ | ✅ |
| 한글 지원 | ✅ | ✅ | ✅ |
| GUI 더블클릭 | ✅ (.bat) | ✅ (.command) | ❌ |
| 프로세스 관리 | tasklist/taskkill | ps/kill | ps/kill |
| 시스템 정보 | wmic/systeminfo | system_profiler | /proc, uname |
| 패키지 관리 | pip | pip/brew | pip/apt |

### 🎨 **인터페이스 차이**

#### **Windows**
- 배치 파일 기반 메뉴 시스템
- Windows Terminal에서 최적화된 색상
- 한글 UTF-8 완벽 지원

#### **macOS**
- Bash 기반 ANSI 색상 터미널
- .command 파일로 Finder 통합
- Unix 스타일 명령어 활용

#### **Linux**
- 순수 Bash 스크립트
- 배포판별 패키지 관리자 지원
- 서버 환경 최적화

---

## 🚀 설치 및 실행 가이드

### 🖥️ **Windows 설치**

1. **Python 설치**
   ```cmd
   # Python 3.7+ 설치 (python.org에서 다운로드)
   python --version
   ```

2. **의존성 설치**
   ```cmd
   pip install -r requirements.txt
   ```

3. **실행**
   ```cmd
   # v3.0 제어센터 실행
   🐹POSCO_WatchHamster_v3_제어센터.bat
   ```

### 🍎 **macOS 설치**

1. **Python 설치**
   ```bash
   # Homebrew로 설치 (권장)
   brew install python3
   
   # 또는 python.org에서 다운로드
   python3 --version
   ```

2. **의존성 설치**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **실행 권한 설정**
   ```bash
   chmod +x 🐹POSCO_WatchHamster_v3_제어센터.command
   ```

4. **실행**
   ```bash
   # 더블클릭 또는 터미널에서
   ./.naming_backup/config_data_backup/watchhamster.log
   ```

### 🐧 **Linux 설치**

1. **Python 설치**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3 python3-pip
   
   # CentOS/RHEL
   sudo yum install python3 python3-pip
   
   # Arch Linux
   sudo pacman -S python python-pip
   ```

2. **의존성 설치**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **실행**
   ```bash
   bash .naming_backup/scripts/.naming_backup/scripts/watchhamster_control_center.sh
   ```

---

## 🔧 플랫폼별 문제 해결

### 🖥️ **Windows 문제 해결**

#### **한글 깨짐 문제**
```cmd
# 코드페이지를 UTF-8로 설정
chcp 65001
```

#### **PowerShell 실행 정책**
```powershell
# 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Python 경로 문제**
```cmd
# Python 경로 확인
where python
where python3
```

### 🍎 **macOS 문제 해결**

#### **권한 문제**
```bash
# 실행 권한 부여
chmod +x *.command
chmod +x *.sh
```

#### **Python 버전 문제**
```bash
# Python3 확인
which python3
python3 --version

# 심볼릭 링크 생성 (필요시)
ln -s /usr/bin/python3 /usr/local/bin/python
```

#### **보안 설정**
```bash
# Gatekeeper 우회 (필요시)
sudo spctl --master-disable
```

### 🐧 **Linux 문제 해결**

#### **권한 문제**
```bash
# 실행 권한 부여
chmod +x *.sh
```

#### **의존성 문제**
```bash
# 시스템 패키지 설치
sudo apt install python3-dev python3-venv

# 가상환경 사용 (권장)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 플랫폼별 최적화 팁

### 🖥️ **Windows 최적화**

- **Windows Terminal 사용**: 더 나은 색상과 폰트 지원
- **배치 파일 최적화**: `@echo off`로 명령어 숨김
- **작업 스케줄러**: 자동 시작 설정 가능
- **바이러스 백신 예외**: Python 스크립트 폴더 예외 처리

### 🍎 **macOS 최적화**

- **iTerm2 사용**: 더 나은 터미널 경험
- **Homebrew 활용**: 패키지 관리 최적화
- **LaunchAgent**: 자동 시작 설정 가능
- **Spotlight 인덱싱**: 빠른 파일 검색

### 🐧 **Linux 최적화**

- **systemd 서비스**: 백그라운드 서비스로 실행
- **cron 작업**: 정기 실행 스케줄링
- **로그 로테이션**: logrotate로 로그 관리
- **방화벽 설정**: 필요한 포트만 개방

---

## 🎉 결론

**POSCO WatchHamster v3.0**은 진정한 크로스 플랫폼 솔루션입니다!

### 🏆 **주요 장점**

- **완벽한 호환성**: Windows, macOS, Linux 모두 지원
- **네이티브 경험**: 각 플랫폼에 최적화된 인터페이스
- **동일한 기능**: 모든 플랫폼에서 동일한 v3.0 기능
- **쉬운 설치**: 플랫폼별 최적화된 설치 가이드

**어떤 운영체제를 사용하든 POSCO WatchHamster v3.0의 혁신적인 기능을 모두 경험하세요! 🚀**

---

*📅 작성일: 2025년 8월 8일*  
*🌍 지원 플랫폼: Windows, macOS, Linux*  
*📝 버전: v3.0-crossplatform*