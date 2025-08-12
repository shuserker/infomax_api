#!/usr/bin/env python3
"""
POSCO 시스템 백업 및 롤백 시스템
System Backup and Rollback Manager

기존 시스템의 모든 내용과 로직을 완전히 보존하면서 안전한 백업/복구 기능을 제공합니다.
"""

import os
import sys
import shutil
import json
import hashlib
import tarfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# 한글 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemBackupManager:
    """시스템 백업 관리자"""
    
    def __init__(self):
        self.backup_root = Path("archive/backups")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # 핵심 보존 파일 목록 (절대 변경 금지)
        self.critical_files = [
            "POSCO_News_250808.py",
            "🐹POSCO_워치햄스터_v3_제어센터.bat",
            "🐹POSCO_워치햄스터_v3_제어센터.command",
            "Monitoring/POSCO_News_250808/posco_main_notifier.py",
            "Monitoring/POSCO_News_250808/posco_main_notifier_minimal.py",
            "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0_minimal.py"
        ]
        
        # 백업 메타데이터
        self.metadata_file = self.backup_root / "backup_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """백업 메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"메타데이터 로드 실패: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        """백업 메타데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"메타데이터 저장 실패: {e}")
    
    def create_full_backup(self) -> str:
        """전체 시스템 백업 생성"""
        backup_id = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_root / backup_id
        
        logger.info(f"🔄 전체 시스템 백업 시작: {backup_id}")
        
        try:
            # 백업 디렉토리 생성
            backup_path.mkdir(exist_ok=True)
            
            # 현재 디렉토리의 모든 파일 백업 (숨김 파일 제외)
            exclude_patterns = [
                '__pycache__',
                '*.pyc',
                '.git',
                'archive/backups',  # 백업 디렉토리 자체는 제외
                '*.log'
            ]
            
            file_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk('.'):
                # 제외할 디렉토리 필터링
                dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in exclude_patterns)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # 제외 패턴 체크
                    if any(pattern in str(file_path) for pattern in exclude_patterns):
                        continue
                    
                    try:
                        # 상대 경로로 백업
                        relative_path = file_path.relative_to('.')
                        backup_file_path = backup_path / relative_path
                        
                        # 디렉토리 생성
                        backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 파일 복사
                        shutil.copy2(file_path, backup_file_path)
                        
                        file_count += 1
                        total_size += file_path.stat().st_size
                        
                        if file_count % 100 == 0:
                            logger.info(f"진행 상황: {file_count}개 파일 백업 완료")
                            
                    except Exception as e:
                        logger.warning(f"파일 백업 실패 {file_path}: {e}")
            
            # 백업 압축
            compressed_backup = self._compress_backup(backup_path, backup_id)
            
            # 체크섬 생성
            checksum = self._calculate_checksum(compressed_backup)
            
            # 메타데이터 저장
            self.metadata[backup_id] = {
                'type': 'full_backup',
                'created_at': datetime.now().isoformat(),
                'file_count': file_count,
                'total_size': total_size,
                'compressed_file': str(compressed_backup),
                'checksum': checksum,
                'description': '정리 작업 시작 전 전체 시스템 백업'
            }
            
            self.save_metadata()
            
            # 원본 디렉토리 삭제 (압축 파일만 보관)
            shutil.rmtree(backup_path)
            
            logger.info(f"✅ 전체 백업 완료: {backup_id}")
            logger.info(f"   파일 수: {file_count:,}개")
            logger.info(f"   총 크기: {total_size / 1024 / 1024:.1f}MB")
            logger.info(f"   압축 파일: {compressed_backup}")
            
            return backup_id
            
        except Exception as e:
            logger.error(f"❌ 백업 생성 실패: {e}")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise
    
    def _compress_backup(self, backup_path: Path, backup_id: str) -> Path:
        """백업 디렉토리 압축"""
        compressed_file = self.backup_root / f"{backup_id}.tar.gz"
        
        logger.info(f"🗜️ 백업 압축 중: {compressed_file}")
        
        with tarfile.open(compressed_file, 'w:gz') as tar:
            tar.add(backup_path, arcname=backup_id)
        
        return compressed_file
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def create_stage_backup(self, stage_name: str, changed_files: List[str] = None) -> str:
        """단계별 백업 생성"""
        backup_id = f"stage_{stage_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_root / backup_id
        
        logger.info(f"🔄 단계별 백업 시작: {stage_name}")
        
        try:
            backup_path.mkdir(exist_ok=True)
            
            # 변경된 파일들만 백업 (지정된 경우)
            if changed_files:
                files_to_backup = changed_files
            else:
                # 핵심 파일들은 항상 백업
                files_to_backup = [f for f in self.critical_files if Path(f).exists()]
            
            file_count = 0
            for file_path in files_to_backup:
                try:
                    source = Path(file_path)
                    if source.exists():
                        dest = backup_path / file_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, dest)
                        file_count += 1
                except Exception as e:
                    logger.warning(f"파일 백업 실패 {file_path}: {e}")
            
            # 압축 및 메타데이터 저장
            compressed_backup = self._compress_backup(backup_path, backup_id)
            checksum = self._calculate_checksum(compressed_backup)
            
            self.metadata[backup_id] = {
                'type': 'stage_backup',
                'stage_name': stage_name,
                'created_at': datetime.now().isoformat(),
                'file_count': file_count,
                'compressed_file': str(compressed_backup),
                'checksum': checksum,
                'files': files_to_backup
            }
            
            self.save_metadata()
            shutil.rmtree(backup_path)
            
            logger.info(f"✅ 단계별 백업 완료: {backup_id} ({file_count}개 파일)")
            return backup_id
            
        except Exception as e:
            logger.error(f"❌ 단계별 백업 실패: {e}")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise
    
    def list_backups(self) -> List[Dict]:
        """백업 목록 조회"""
        backups = []
        for backup_id, info in self.metadata.items():
            backups.append({
                'id': backup_id,
                'type': info.get('type', 'unknown'),
                'created_at': info.get('created_at', ''),
                'file_count': info.get('file_count', 0),
                'description': info.get('description', info.get('stage_name', ''))
            })
        
        # 생성 시간 순으로 정렬
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def rollback_to_backup(self, backup_id: str) -> bool:
        """지정된 백업으로 롤백"""
        if backup_id not in self.metadata:
            logger.error(f"❌ 백업을 찾을 수 없습니다: {backup_id}")
            return False
        
        backup_info = self.metadata[backup_id]
        compressed_file = Path(backup_info['compressed_file'])
        
        if not compressed_file.exists():
            logger.error(f"❌ 백업 파일이 존재하지 않습니다: {compressed_file}")
            return False
        
        logger.info(f"🔄 롤백 시작: {backup_id}")
        
        try:
            # 체크섬 검증
            current_checksum = self._calculate_checksum(compressed_file)
            if current_checksum != backup_info['checksum']:
                logger.error("❌ 백업 파일 무결성 검증 실패")
                return False
            
            # 현재 상태 임시 백업
            emergency_backup = self.create_stage_backup("emergency_before_rollback")
            logger.info(f"비상 백업 생성: {emergency_backup}")
            
            # 백업 압축 해제
            temp_restore_path = self.backup_root / f"temp_restore_{int(time.time())}"
            
            with tarfile.open(compressed_file, 'r:gz') as tar:
                tar.extractall(temp_restore_path)
            
            # 백업 내용을 현재 디렉토리로 복원
            backup_content_path = temp_restore_path / backup_id
            
            if backup_info['type'] == 'full_backup':
                # 전체 복원
                logger.info("전체 시스템 복원 중...")
                
                # 기존 파일들 백업 후 삭제 (핵심 파일 제외)
                for item in Path('.').iterdir():
                    if item.name not in ['archive', '.git', '.kiro']:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                
                # 백업에서 복원
                for item in backup_content_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, item.name)
                    elif item.is_dir():
                        shutil.copytree(item, item.name)
            
            else:
                # 부분 복원 (단계별 백업)
                logger.info("부분 시스템 복원 중...")
                
                for file_path in backup_info.get('files', []):
                    source = backup_content_path / file_path
                    dest = Path(file_path)
                    
                    if source.exists():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, dest)
            
            # 임시 디렉토리 정리
            shutil.rmtree(temp_restore_path)
            
            logger.info(f"✅ 롤백 완료: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 롤백 실패: {e}")
            return False
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """백업 무결성 검증"""
        if backup_id not in self.metadata:
            return False
        
        backup_info = self.metadata[backup_id]
        compressed_file = Path(backup_info['compressed_file'])
        
        if not compressed_file.exists():
            return False
        
        try:
            current_checksum = self._calculate_checksum(compressed_file)
            return current_checksum == backup_info['checksum']
        except:
            return False

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='POSCO 시스템 백업 관리')
    parser.add_argument('--create-full', action='store_true', help='전체 백업 생성')
    parser.add_argument('--create-stage', type=str, help='단계별 백업 생성')
    parser.add_argument('--list', action='store_true', help='백업 목록 조회')
    parser.add_argument('--rollback', type=str, help='지정된 백업으로 롤백')
    parser.add_argument('--verify', type=str, help='백업 무결성 검증')
    
    args = parser.parse_args()
    
    backup_manager = SystemBackupManager()
    
    try:
        if args.create_full:
            backup_id = backup_manager.create_full_backup()
            print(f"✅ 전체 백업 생성 완료: {backup_id}")
            
        elif args.create_stage:
            backup_id = backup_manager.create_stage_backup(args.create_stage)
            print(f"✅ 단계별 백업 생성 완료: {backup_id}")
            
        elif args.list:
            backups = backup_manager.list_backups()
            print("\n📋 백업 목록:")
            print("-" * 80)
            for backup in backups:
                print(f"ID: {backup['id']}")
                print(f"유형: {backup['type']}")
                print(f"생성일: {backup['created_at']}")
                print(f"파일 수: {backup['file_count']:,}개")
                print(f"설명: {backup['description']}")
                print("-" * 80)
                
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
                
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"❌ 작업 실행 중 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()