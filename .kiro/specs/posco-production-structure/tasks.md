# Implementation Plan

- [x] 1. 새로운 폴더 구조 생성
  - Monitoring/WatchHamster_Project 폴더 구조 생성
  - WatchHamster_Project 하위에 core, scripts, docs 폴더 생성
  - WatchHamster_Project/Posco_News_Mini_Final 폴더 구조 생성
  - Posco_News_Mini_Final 하위에 core, scripts, docs, config, logs 폴더 생성
  - 각 폴더에 __init__.py 파일 생성 (Python 패키지화)
  - recovery_config 폴더는 그대로 보존 (레거시 참고용)
  - _Requirements: 1.1, 2.1_

- [x] 2. 워치햄스터 공통 모듈들 복사
  - recovery_config/watchhamster_monitor.py를 WatchHamster_Project/core로 복사
  - recovery_config/git_monitor.py를 WatchHamster_Project/core로 복사
  - 원본 파일들은 recovery_config에 그대로 보존
  - _Requirements: 2.1, 2.2_

- [x] 3. 포스코 프로젝트 모듈들 복사
  - recovery_config/environment_setup.py를 Posco_News_Mini_Final/core로 복사
  - recovery_config/integrated_api_module.py를 Posco_News_Mini_Final/core로 복사
  - recovery_config/news_message_generator.py를 Posco_News_Mini_Final/core로 복사
  - recovery_config/webhook_sender.py를 Posco_News_Mini_Final/core로 복사
  - 원본 파일들은 recovery_config에 그대로 보존
  - _Requirements: 2.1, 2.2_

- [x] 4. 워치햄스터 실행 스크립트 복사
  - recovery_config/start_watchhamster_monitor.py를 WatchHamster_Project/scripts/start_monitoring.py로 복사
  - recovery_config/daily_check.bat를 WatchHamster_Project/scripts로 복사
  - recovery_config/daily_check.sh를 WatchHamster_Project/scripts로 복사
  - 원본 파일들은 recovery_config에 그대로 보존
  - _Requirements: 2.2, 3.4_

- [x] 5. 포스코 실행 스크립트 복사
  - recovery_config/comprehensive_system_integration_test.py를 Posco_News_Mini_Final/scripts/system_test.py로 복사
  - 원본 파일은 recovery_config에 그대로 보존
  - _Requirements: 2.2, 3.4_

- [x] 6. 문서 파일들 복사 및 정리
  - 워치햄스터 운영 가이드를 WatchHamster_Project/docs로 새로 생성
  - recovery_config/MONITORING_GUIDE_FOR_OPERATORS.md를 Posco_News_Mini_Final/docs/MONITORING_GUIDE.md로 복사
  - recovery_config/QUICK_MONITORING_CHEAT_SHEET.md를 Posco_News_Mini_Final/docs/QUICK_CHEAT_SHEET.md로 복사
  - 원본 파일들은 recovery_config에 그대로 보존
  - _Requirements: 4.4_

- [x] 7. 포스코 설정 파일 복사
  - recovery_config/environment_settings.json을 Posco_News_Mini_Final/config 폴더로 복사
  - 원본 파일은 recovery_config에 그대로 보존
  - _Requirements: 2.2_

- [x] 8. 워치햄스터 레벨 Import 경로 수정
  - 복사된 워치햄스터 모듈들의 import 경로를 새로운 구조에 맞게 수정
  - 워치햄스터에서 포스코 모듈을 참조하는 경로 수정
  - recovery_config 경로를 Monitoring.WatchHamster_Project 경로로 변경
  - _Requirements: 4.1, 4.2_

- [x] 9. 포스코 프로젝트 Import 경로 수정
  - 복사된 포스코 모듈들의 내부 import 경로 수정
  - recovery_config 경로를 Monitoring.WatchHamster_Project.Posco_News_Mini_Final.core 경로로 변경
  - 워치햄스터 공통 모듈을 참조하는 경로를 상위 패키지로 수정
  - _Requirements: 4.1, 4.2_

- [x] 10. 실행 스크립트 경로 수정
  - 복사된 start_monitoring.py의 import 경로 수정 (워치햄스터 + 포스코)
  - 복사된 system_test.py의 import 경로 수정 (포스코 전용)
  - daily_check 스크립트들의 실행 경로를 새로운 구조로 수정
  - _Requirements: 4.1, 4.2_

- [x] 11. 워치햄스터 레벨 기능 테스트
  - 워치햄스터 모니터 모듈 로드 테스트
  - Git 모니터링 기능 테스트
  - 시스템 리소스 모니터링 테스트
  - _Requirements: 3.1, 3.2_

- [x] 12. 포스코 프로젝트 기능 테스트
  - 환경 설정 모듈 로드 테스트
  - API 연동 모듈 테스트
  - 메시지 생성 모듈 테스트
  - 웹훅 전송 모듈 테스트
  - _Requirements: 3.1, 3.2_

- [x] 13. 전체 시스템 통합 테스트
  - 새로운 구조에서 system_test.py 실행
  - 워치햄스터와 포스코 연동 테스트
  - 100% 성공률 달성 확인
  - _Requirements: 3.1, 3.2_

- [x] 14. 플랫폼별 실행 스크립트 테스트
  - Mac에서 daily_check.sh 실행 테스트
  - Windows에서 daily_check.bat 실행 테스트
  - 경로 구분자 호환성 확인
  - _Requirements: 2.3_

- [x] 15. 모니터링 가이드 업데이트
  - 워치햄스터 운영 가이드 생성
  - 포스코 모니터링 가이드를 새로운 구조로 업데이트
  - 실행 명령어를 새로운 경로로 수정
  - 확장성 안내 (새 프로젝트 추가 방법)
  - _Requirements: 2.3_

- [x] 16. 최종 검증 및 레거시 보존 확인
  - 모든 파일이 올바른 위치에 복사되었는지 확인
  - recovery_config 폴더 원본 파일들 무결성 확인 (레거시 보존)
  - 워치햄스터-포스코 연동 확인
  - 새로운 구조에서 최종 안정성 테스트 (100% 성공률 달성)
  - 향후 확장성 검증 (새 프로젝트 추가 준비)
  - 복사본과 원본 파일 내용 일치 확인
  - _Requirements: 3.1, 3.2, 3.3, 2.1_