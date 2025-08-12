#!/usr/bin/env python3
"""
POSCO 워치햄스터 웹훅 복원 전용 백업 관리자
Webhook Restoration Backup Manager

웹훅 복원 작업에 특화된 백업 및 롤백 시스템을 제공합니다.
"""

import os
import sys
import shutil
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import traceback

# 한글 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_backup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebhookBackupManager:
    """웹훅 복원 전용 백업 관리자"""
    
    def __init__(self):
        self.backup_root = Path("webhook_backup")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # 웹훅 관련 핵심 파일들
        self.webhook_files = [
            "core/monitoring/monitor_WatchHamster_v3.0.py",
            "webhook_message_restorer.py",
            "webhook_config_restorer.py",
            "compatibility_checker.py"
        ]
        
        # 백업 메타데이터 파일
        self.metadata_file = self.backup_root / "webhook_backup_metadata.json"
        self.load_metadata()
        
        # 자동 롤백 설정
        self.auto_rollback_enabled = True
        self.max_backup_count = 10
    
    def load_metadata(self):
        """백업 메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info("백업 메타데이터를 성공적으로 로드했습니다")
            except Exception as e:
                logger.warning(f"메타데이터 로드 실패: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
            logger.info("새로운 백업 메타데이터를 초기화했습니다")
    
    def save_metadata(self):
        """백업 메타데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.debug("백업 메타데이터를 저장했습니다")
        except Exception as e:
            logger.error(f"메타데이터 저장 실패: {e}")
            raise
    
    def create_backup(self, backup_name: str, description: str = "") -> str:
        """웹훅 관련 파일들의 백업 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"webhook_backup_{backup_name}_{timestamp}"
        backup_path = self.backup_root / backup_id
        
        logger.info(f"🔄 웹훅 백업 생성 시작: {backup_id}")
        
        try:
            # 백업 디렉토리 생성
            backup_path.mkdir(exist_ok=True)
            
            backed_up_files = []
            file_checksums = {}
            total_size = 0
            
            # 웹훅 관련 파일들 백업
            for file_path in self.webhook_files:
                source_path = Path(file_path)
                
                if source_path.exists():
                    # 상대 경로 유지하여 백업
                    dest_path = backup_path / file_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 파일 복사
                    shutil.copy2(source_path, dest_path)
                    
                    # 체크섬 계산
                    checksum = self._calculate_file_checksum(source_path)
                    file_checksums[file_path] = checksum
                    
                    # 파일 크기 추가
                    file_size = source_path.stat().st_size
                    total_size += file_size
                    
                    backed_up_files.append(file_path)
                    logger.debug(f"백업 완료: {file_path} ({file_size} bytes)")
                else:
                    logger.warning(f"파일이 존재하지 않아 백업에서 제외: {file_path}")
            
            # 추가 설정 파일들도 백업 (존재하는 경우)
            additional_files = [
                "webhook_restoration.log",
                "compatibility_integration_test_results.json",
                "webhook_config_restoration_report_*.txt"
            ]
            
            for pattern in additional_files:
                if '*' in pattern:
                    # 와일드카드 패턴 처리
                    import glob
                    matching_files = glob.glob(pattern)
                    for file_path in matching_files:
                        if Path(file_path).exists():
                            dest_path = backup_path / file_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dest_path)
                            backed_up_files.append(file_path)
                else:
                    if Path(pattern).exists():
                        dest_path = backup_path / pattern
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(pattern, dest_path)
                        backed_up_files.append(pattern)
            
            # 백업 메타데이터 저장
            self.metadata[backup_id] = {
                'backup_name': backup_name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'backup_path': str(backup_path),
                'backed_up_files': backed_up_files,
                'file_checksums': file_checksums,
                'file_count': len(backed_up_files),
                'total_size': total_size,
                'status': 'completed'
            }
            
            self.save_metadata()
            
            # 오래된 백업 정리
            self._cleanup_old_backups()
            
            logger.info(f"✅ 웹훅 백업 생성 완료: {backup_id}")
            logger.info(f"   백업된 파일 수: {len(backed_up_files)}개")
            logger.info(f"   총 크기: {total_size / 1024:.1f}KB")
            
            return backup_id
            
        except Exception as e:
            logger.error(f"❌ 백업 생성 실패: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            
            # 실패한 백업 디렉토리 정리
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            # 메타데이터에서 실패 기록
            if backup_id in self.metadata:
                self.metadata[backup_id]['status'] = 'failed'
                self.metadata[backup_id]['error'] = str(e)
                self.save_metadata()
            
            raise
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산"""
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"체크섬 계산 실패 {file_path}: {e}")
            return ""
    
    def rollback_to_backup(self, backup_id: str) -> bool:
        """지정된 백업으로 롤백"""
        if backup_id not in self.metadata:
            logger.error(f"❌ 백업을 찾을 수 없습니다: {backup_id}")
            return False
        
        backup_info = self.metadata[backup_id]
        backup_path = Path(backup_info['backup_path'])
        
        if not backup_path.exists():
            logger.error(f"❌ 백업 디렉토리가 존재하지 않습니다: {backup_path}")
            return False
        
        logger.info(f"🔄 웹훅 롤백 시작: {backup_id}")
        
        try:
            # 현재 상태를 비상 백업으로 저장
            emergency_backup_id = self.create_backup(
                "emergency_before_rollback",
                f"롤백 전 비상 백업 (롤백 대상: {backup_id})"
            )
            logger.info(f"비상 백업 생성 완료: {emergency_backup_id}")
            
            # 백업된 파일들을 원래 위치로 복원
            restored_files = []
            failed_files = []
            
            for file_path in backup_info['backed_up_files']:
                try:
                    source_path = backup_path / file_path
                    dest_path = Path(file_path)
                    
                    if source_path.exists():
                        # 대상 디렉토리 생성
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 파일 복원
                        shutil.copy2(source_path, dest_path)
                        
                        # 체크섬 검증 (가능한 경우)
                        if file_path in backup_info.get('file_checksums', {}):
                            expected_checksum = backup_info['file_checksums'][file_path]
                            actual_checksum = self._calculate_file_checksum(dest_path)
                            
                            if expected_checksum and actual_checksum != expected_checksum:
                                logger.warning(f"체크섬 불일치 {file_path}: 예상={expected_checksum[:8]}..., 실제={actual_checksum[:8]}...")
                        
                        restored_files.append(file_path)
                        logger.debug(f"복원 완료: {file_path}")
                    else:
                        logger.warning(f"백업 파일이 존재하지 않음: {source_path}")
                        failed_files.append(file_path)
                        
                except Exception as e:
                    logger.error(f"파일 복원 실패 {file_path}: {e}")
                    failed_files.append(file_path)
            
            # 롤백 결과 기록
            rollback_info = {
                'rollback_id': f"rollback_{backup_id}_{int(time.time())}",
                'source_backup_id': backup_id,
                'emergency_backup_id': emergency_backup_id,
                'rollback_time': datetime.now().isoformat(),
                'restored_files': restored_files,
                'failed_files': failed_files,
                'success': len(failed_files) == 0
            }
            
            # 롤백 기록을 메타데이터에 추가
            if 'rollback_history' not in self.metadata:
                self.metadata['rollback_history'] = []
            self.metadata['rollback_history'].append(rollback_info)
            self.save_metadata()
            
            if rollback_info['success']:
                logger.info(f"✅ 웹훅 롤백 완료: {backup_id}")
                logger.info(f"   복원된 파일 수: {len(restored_files)}개")
                return True
            else:
                logger.error(f"❌ 웹훅 롤백 부분 실패: {len(failed_files)}개 파일 실패")
                logger.error(f"   실패한 파일들: {failed_files}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 롤백 실행 중 오류: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            return False
    
    def auto_rollback_on_error(self, error_context: str) -> bool:
        """오류 발생 시 자동 롤백"""
        if not self.auto_rollback_enabled:
            logger.info("자동 롤백이 비활성화되어 있습니다")
            return False
        
        logger.warning(f"🚨 오류 감지로 인한 자동 롤백 시도: {error_context}")
        
        # 가장 최근 백업 찾기
        recent_backup = self.get_most_recent_backup()
        
        if not recent_backup:
            logger.error("❌ 자동 롤백할 백업이 없습니다")
            return False
        
        logger.info(f"가장 최근 백업으로 자동 롤백 시도: {recent_backup}")
        
        try:
            success = self.rollback_to_backup(recent_backup)
            
            if success:
                logger.info(f"✅ 자동 롤백 성공: {recent_backup}")
                
                # 자동 롤백 기록
                auto_rollback_info = {
                    'auto_rollback_time': datetime.now().isoformat(),
                    'error_context': error_context,
                    'backup_used': recent_backup,
                    'success': True
                }
                
                if 'auto_rollback_history' not in self.metadata:
                    self.metadata['auto_rollback_history'] = []
                self.metadata['auto_rollback_history'].append(auto_rollback_info)
                self.save_metadata()
                
                return True
            else:
                logger.error(f"❌ 자동 롤백 실패: {recent_backup}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 자동 롤백 중 오류: {e}")
            return False
    
    def get_most_recent_backup(self) -> Optional[str]:
        """가장 최근 백업 ID 반환"""
        if not self.metadata:
            return None
        
        # 비상 백업은 제외하고 일반 백업만 고려
        regular_backups = {
            backup_id: info for backup_id, info in self.metadata.items()
            if isinstance(info, dict) and 
            info.get('status') == 'completed' and
            'emergency' not in info.get('backup_name', '')
        }
        
        if not regular_backups:
            return None
        
        # 생성 시간 기준으로 정렬하여 가장 최근 것 반환
        sorted_backups = sorted(
            regular_backups.items(),
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        )
        
        return sorted_backups[0][0] if sorted_backups else None
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """백업 목록 조회"""
        backups = []
        
        for backup_id, info in self.metadata.items():
            if isinstance(info, dict) and 'backup_name' in info:
                backups.append({
                    'backup_id': backup_id,
                    'backup_name': info.get('backup_name', ''),
                    'description': info.get('description', ''),
                    'created_at': info.get('created_at', ''),
                    'file_count': info.get('file_count', 0),
                    'total_size': info.get('total_size', 0),
                    'status': info.get('status', 'unknown')
                })
        
        # 생성 시간 순으로 정렬 (최신 순)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """백업 무결성 검증"""
        if backup_id not in self.metadata:
            logger.error(f"백업을 찾을 수 없습니다: {backup_id}")
            return False
        
        backup_info = self.metadata[backup_id]
        backup_path = Path(backup_info['backup_path'])
        
        if not backup_path.exists():
            logger.error(f"백업 디렉토리가 존재하지 않습니다: {backup_path}")
            return False
        
        logger.info(f"🔍 백업 무결성 검증 시작: {backup_id}")
        
        try:
            file_checksums = backup_info.get('file_checksums', {})
            verification_results = []
            
            for file_path in backup_info.get('backed_up_files', []):
                backup_file_path = backup_path / file_path
                
                if not backup_file_path.exists():
                    logger.error(f"백업 파일이 존재하지 않음: {backup_file_path}")
                    verification_results.append(False)
                    continue
                
                # 체크섬 검증 (가능한 경우)
                if file_path in file_checksums:
                    expected_checksum = file_checksums[file_path]
                    actual_checksum = self._calculate_file_checksum(backup_file_path)
                    
                    if expected_checksum and actual_checksum != expected_checksum:
                        logger.error(f"체크섬 불일치 {file_path}: 예상={expected_checksum[:8]}..., 실제={actual_checksum[:8]}...")
                        verification_results.append(False)
                    else:
                        verification_results.append(True)
                else:
                    # 체크섬이 없는 경우 파일 존재만 확인
                    verification_results.append(True)
            
            success = all(verification_results)
            
            if success:
                logger.info(f"✅ 백업 무결성 검증 통과: {backup_id}")
            else:
                logger.error(f"❌ 백업 무결성 검증 실패: {backup_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"백업 무결성 검증 중 오류: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """오래된 백업 정리"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= self.max_backup_count:
                return
            
            # 오래된 백업들 삭제 (비상 백업은 제외)
            backups_to_delete = []
            regular_backups = [b for b in backups if 'emergency' not in b['backup_name']]
            
            if len(regular_backups) > self.max_backup_count:
                backups_to_delete = regular_backups[self.max_backup_count:]
            
            for backup in backups_to_delete:
                backup_id = backup['backup_id']
                backup_info = self.metadata[backup_id]
                backup_path = Path(backup_info['backup_path'])
                
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                    logger.info(f"오래된 백업 삭제: {backup_id}")
                
                del self.metadata[backup_id]
            
            if backups_to_delete:
                self.save_metadata()
                logger.info(f"총 {len(backups_to_delete)}개의 오래된 백업을 정리했습니다")
                
        except Exception as e:
            logger.warning(f"백업 정리 중 오류: {e}")
    
    def get_backup_status(self) -> Dict[str, Any]:
        """백업 시스템 상태 조회"""
        backups = self.list_backups()
        
        status = {
            'total_backups': len(backups),
            'successful_backups': len([b for b in backups if b['status'] == 'completed']),
            'failed_backups': len([b for b in backups if b['status'] == 'failed']),
            'total_size': sum(b['total_size'] for b in backups),
            'auto_rollback_enabled': self.auto_rollback_enabled,
            'max_backup_count': self.max_backup_count,
            'backup_root': str(self.backup_root),
            'most_recent_backup': self.get_most_recent_backup()
        }
        
        # 롤백 히스토리 정보 추가
        rollback_history = self.metadata.get('rollback_history', [])
        auto_rollback_history = self.metadata.get('auto_rollback_history', [])
        
        status['rollback_count'] = len(rollback_history)
        status['auto_rollback_count'] = len(auto_rollback_history)
        status['last_rollback'] = rollback_history[-1]['rollback_time'] if rollback_history else None
        status['last_auto_rollback'] = auto_rollback_history[-1]['auto_rollback_time'] if auto_rollback_history else None
        
        return status

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='POSCO 워치햄스터 웹훅 백업 관리자')
    parser.add_argument('--create', type=str, help='백업 생성 (백업 이름 지정)')
    parser.add_argument('--description', type=str, default='', help='백업 설명')
    parser.add_argument('--list', action='store_true', help='백업 목록 조회')
    parser.add_argument('--rollback', type=str, help='지정된 백업으로 롤백')
    parser.add_argument('--verify', type=str, help='백업 무결성 검증')
    parser.add_argument('--status', action='store_true', help='백업 시스템 상태 조회')
    parser.add_argument('--auto-rollback', type=str, help='자동 롤백 테스트 (오류 컨텍스트 지정)')
    
    args = parser.parse_args()
    
    backup_manager = WebhookBackupManager()
    
    try:
        if args.create:
            backup_id = backup_manager.create_backup(args.create, args.description)
            print(f"✅ 백업 생성 완료: {backup_id}")
            
        elif args.list:
            backups = backup_manager.list_backups()
            print("\n📋 웹훅 백업 목록:")
            print("-" * 100)
            for backup in backups:
                print(f"ID: {backup['backup_id']}")
                print(f"이름: {backup['backup_name']}")
                print(f"설명: {backup['description']}")
                print(f"생성일: {backup['created_at']}")
                print(f"파일 수: {backup['file_count']:,}개")
                print(f"크기: {backup['total_size'] / 1024:.1f}KB")
                print(f"상태: {backup['status']}")
                print("-" * 100)
                
        elif args.rollback:
            success = backup_manager.rollback_to_backup(args.rollback)
            if success:
                print(f"✅ 롤백 완료: {args.rollback}")
            else:
                print(f"❌ 롤백 실패: {args.rollback}")
                
        elif args.verify:
            is_valid = backup_manager.verify_backup_integrity(args.verify)
            if is_valid:
                print(f"✅ 백업 무결성 검증 통과: {args.verify}")
            else:
                print(f"❌ 백업 무결성 검증 실패: {args.verify}")
                
        elif args.status:
            status = backup_manager.get_backup_status()
            print("\n📊 웹훅 백업 시스템 상태:")
            print("-" * 50)
            print(f"총 백업 수: {status['total_backups']}개")
            print(f"성공한 백업: {status['successful_backups']}개")
            print(f"실패한 백업: {status['failed_backups']}개")
            print(f"총 크기: {status['total_size'] / 1024:.1f}KB")
            print(f"자동 롤백: {'활성화' if status['auto_rollback_enabled'] else '비활성화'}")
            print(f"최대 백업 수: {status['max_backup_count']}개")
            print(f"백업 디렉토리: {status['backup_root']}")
            print(f"최근 백업: {status['most_recent_backup'] or '없음'}")
            print(f"롤백 횟수: {status['rollback_count']}회")
            print(f"자동 롤백 횟수: {status['auto_rollback_count']}회")
            
        elif args.auto_rollback:
            success = backup_manager.auto_rollback_on_error(args.auto_rollback)
            if success:
                print(f"✅ 자동 롤백 성공: {args.auto_rollback}")
            else:
                print(f"❌ 자동 롤백 실패: {args.auto_rollback}")
                
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ 작업 실행 중 오류: {e}")
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()