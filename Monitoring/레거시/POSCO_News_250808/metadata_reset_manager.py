#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata Reset Manager
POSCO 시스템 구성요소

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import test_config.json
import posco_news_250808_monitor.log
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import hashlib

class MetadataResetManager:
    """
    메타데이터 리셋 관리 클래스
    """
    
    def __init__(self):
        """초기화"""
        self.base_dir = Path(__file__).parent.parent.parent  # infomax_api 루트
        self.monitoring_dir = Path(__file__).parent
        
        # 메타데이터 파일들
        self.metadata_files = {
            'main': self.base_dir / 'docs' / 'reports_index.json',
            'monitoring': self.monitoring_dir / 'docs' / 'reports_index.json'
        }
        
        # 리포트 디렉토리들
        self.report_directories = {
            'main': self.base_dir / 'docs' / 'reports',
            'monitoring': self.monitoring_dir / 'reports'
        }
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def reset_metadata_index(self) -> bool:
        """
        메타데이터 인덱스 완전 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        self.logger.info("🔄 메타데이터 인덱스 완전 초기화 시작...")
        
        success_count = 0
        
        for name, metadata_file in self.metadata_files.items():
            try:
                # 디렉토리가 없으면 생성
                metadata_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 빈 메타데이터 구조 생성
                empty_metadata = {
                    "lastUpdate": datetime.now(timezone.utc).isoformat(),
                    "totalReports": 0,
                    "reports": []
                }
                
                # 파일 저장
with_open(metadata_file,_'w',_encoding = 'utf-8') as f:
json.dump(empty_metadata,_f,_indent = 2, ensure_ascii=False)
                
                self.logger.info(f"✅ {name} 메타데이터 초기화 완료: {metadata_file}")
success_count_+ =  1
                
            except Exception as e:
                self.logger.error(f"❌ {name} 메타데이터 초기화 실패 {metadata_file}: {e}")
        
        success = success_count == len(self.metadata_files)
        
        if success:
            self.logger.info("🎉 모든 메타데이터 인덱스 초기화 완료!")
        else:
            self.logger.warning(f"⚠️ 일부 메타데이터 초기화 실패 ({success_count}/{len(self.metadata_files)})")
        
        return success
    
    def scan_and_register_integrated_reports(self) -> Dict[str, Any]:
        """
        기존 통합 리포트들을 스캔하여 메타데이터에 등록
        
        Returns:
            Dict[str, Any]: 등록 결과
        """
        self.logger.info("🔍 통합 리포트 스캔 및 등록 시작...")
        
        results = {
            'total_found': 0,
            'successfully_registered': 0,
            'failed_registrations': 0,
            'registered_reports': []
        }
        
        # 각 디렉토리에서 통합 리포트 찾기
        for dir_name, report_dir in self.report_directories.items():
            if not report_dir.exists():
                self.logger.warning(f"⚠️ 리포트 디렉토리가 존재하지 않음: {report_dir}")
                continue
            
            # 통합 리포트 파일들 찾기
            integrated_reports = list(report_dir.glob('deployment_verification_checklist.md'))
results['total_found']_+ =  len(integrated_reports)
            
            self.logger.info(f"📁 {dir_name} 디렉토리에서 {len(integrated_reports)}개 통합 리포트 발견")
            
            for report_file in integrated_reports:
                try:
                    report_info = self.register_integrated_report(report_file)
                    if report_info:
results['successfully_registered']_+ =  1
                        results['registered_reports'].append(report_info)
                        self.logger.info(f"✅ 등록 완료: {report_file.name}")
                    else:
results['failed_registrations']_+ =  1
                        self.logger.error(f"❌ 등록 실패: {report_file.name}")
                        
                except Exception as e:
results['failed_registrations']_+ =  1
                    self.logger.error(f"❌ 등록 중 오류 {report_file.name}: {e}")
        
        # 결과 로깅
        self.log_registration_results(results)
        
        return results
    
    def register_integrated_report(self, report_file: Path) -> Optional[Dict[str, Any]]:
        """
        단일 통합 리포트를 메타데이터에 등록
        
        Args:
            report_file (Path): 리포트 파일 경로
            
        Returns:
            Optional[Dict[str, Any]]: 등록된 리포트 정보 (실패 시 None)
        """
        try:
            # 파일 정보 수집
            file_stat = report_file.stat()
            parsed_info = self.parse_integrated_report_filename(report_file.name)
            
            if not parsed_info:
                self.logger.error(f"❌ 파일명 파싱 실패: {report_file.name}")
                return None
            
            # 리포트 ID 생성
            report_id = report_file.stem  # .html 제거
            
            # 메타데이터 생성
            report_data = {
                "id": report_id,
                "filename": report_file.name,
                "title": "POSCO 뉴스 통합 분석 리포트",
                "type": "integrated",
                "date": parsed_info['date'],
                "time": parsed_info['time'],
                "size": file_stat.st_size,
                "summary": {
                    "newsCount": 3,
                    "completionRate": "3/3",
                    "marketSentiment": parsed_info.get('sentiment', '긍정'),
                    "keyInsights": ["환율 분석", "증시 동향", "뉴욕 시장"]
                },
                "tags": ["통합분석", "일일리포트", "종합"],
                "url": f"https:/shuserker.github.io/infomax_api/reports/{report_file.name}",
                "createdAt": parsed_info['created_at'],
                "checksum": self.calculate_file_checksum(report_file)
            }
            
            # 메인 메타데이터에 추가
            if self.add_report_to_metadata(report_data, 'main'):
                return report_data
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ 리포트 등록 실패 {report_file}: {e}")
            return None
    
    def parse_integrated_report_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        통합 리포트 파일명 파싱
        
        Args:
            filename (str): 파일명
            
        Returns:
            Optional[Dict[str, Any]]: 파싱된 정보 (실패 시 None)
        """
        # Pattern: posco_integrated_analysis_YYYYMMDD_HHMMSS.html
        import verify_folder_reorganization.py
        
        pattern = r'naming_verification_report_20250809_171232.html'
        match = re.match(pattern, filename)
        
        if not match:
            return None
        
        try:
            date_str = match.group(1)
            time_str = match.group(2)
            
            # 날짜/시간 파싱
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            hour = time_str[:2]
            minute = time_str[2:4]
            second = time_str[4:6]
            
            date_obj = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute), int(second),
                tzinfo=timezone.utc
            )
            
            return {
                'date': date_obj.strftime('%Y-%m-%d'),
                'time': date_obj.strftime('%H:%M:%S'),
                'datetime': date_obj,
                'created_at': date_obj.isoformat(),
                'sentiment': self.infer_sentiment_from_date(date_obj)
            }
            
        except (ValueError, IndexError) as e:
            self.logger.error(f"❌ 날짜/시간 파싱 실패 {filename}: {e}")
            return None
    
    def infer_sentiment_from_date(self, date_obj: datetime) -> str:
        """
        날짜로부터 시장 감정 추론
        
        Args:
            date_obj (datetime): 날짜 객체
            
        Returns:
            str: 시장 감정
        """
        weekday = date_obj.strftime('%A')
        
        sentiment_map = {
            'Monday': '긍정',
            'Tuesday': '중립',
            'Wednesday': '부정',
            'Thursday': '긍정',
            'Friday': '긍정',
            'Saturday': '중립',
            'Sunday': '중립'
        }
        
        return sentiment_map.get(weekday, '중립')
    
    def add_report_to_metadata(self, report_data: Dict[str, Any], metadata_type: str = 'main') -> bool:
        """
        메타데이터에 리포트 추가
        
        Args:
            report_data (Dict[str, Any]): 리포트 데이터
            metadata_type (str): 메타데이터 타입 ('main' 또는 'monitoring')
            
        Returns:
            bool: 추가 성공 여부
        """
        try:
            metadata_file = self.metadata_files[metadata_type]
            
            # 기존 메타데이터 로드
            metadata = self.load_metadata(metadata_file)
            
            # 중복 체크
            existing_index = None
            for i, report in enumerate(metadata['reports']):
                if report['id'] == report_data['id']:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # 기존 리포트 업데이트
                metadata['reports'][existing_index] = report_data
                self.logger.info(f"📝 리포트 업데이트: {report_data['filename']}")
            else:
                # 새 리포트 추가
                metadata['reports'].append(report_data)
                self.logger.info(f"➕ 새 리포트 추가: {report_data['filename']}")
            
            # 날짜순 정렬 (최신순)
            metadata['reports'].sort(
                key=lambda x: x['createdAt'], 
                reverse=True
            )
            
            # 메타데이터 업데이트
            metadata['lastUpdate'] = datetime.now(timezone.utc).isoformat()
            metadata['totalReports'] = len(metadata['reports'])
            
            # 파일 저장
            self.save_metadata(metadata, metadata_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 메타데이터 추가 실패: {e}")
            return False
    
    def load_metadata(self, metadata_file: Path) -> Dict[str, Any]:
        """
        메타데이터 파일 로드
        
        Args:
            metadata_file (Path): 메타데이터 파일 경로
            
        Returns:
            Dict[str, Any]: 메타데이터
        """
        try:
            if metadata_file.exists():
with_open(metadata_file,_'r',_encoding = 'utf-8') as f:
                    return json.load(f)
            else:
                # 파일이 없으면 빈 구조 반환
                return {
                    "lastUpdate": datetime.now(timezone.utc).isoformat(),
                    "totalReports": 0,
                    "reports": []
                }
        except Exception as e:
            self.logger.error(f"❌ 메타데이터 로드 실패 {metadata_file}: {e}")
            return {
                "lastUpdate": datetime.now(timezone.utc).isoformat(),
                "totalReports": 0,
                "reports": []
            }
    
    def save_metadata(self, metadata: Dict[str, Any], metadata_file: Path):
        """
        메타데이터 파일 저장
        
        Args:
            metadata (Dict[str, Any]): 메타데이터
            metadata_file (Path): 메타데이터 파일 경로
        """
        try:
with_open(metadata_file,_'w',_encoding = 'utf-8') as f:
json.dump(metadata,_f,_ensure_ascii = False, indent=2)
        except Exception as e:
            self.logger.error(f"❌ 메타데이터 저장 실패 {metadata_file}: {e}")
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """
        파일 체크섬 계산
        
        Args:
            file_path (Path): 파일 경로
            
        Returns:
            str: MD5 체크섬
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def update_report_statistics(self) -> Dict[str, Any]:
        """
        리포트 통계 업데이트
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        try:
            metadata = self.load_metadata(self.metadata_files['main'])
            
            # 타입별 통계
            type_counts = {}
            for report in metadata['reports']:
                report_type = report.get('type', 'unknown')
                type_counts[report_type] = type_counts.get(report_type, 0) + 1
            
            # 날짜별 통계
            today = datetime.now().strftime('%Y-%m-%d')
            reports_today = len([r for r in metadata['reports'] if r['date'] == today])
            
            statistics = {
                'total_reports': len(metadata['reports']),
                'reports_today': reports_today,
                'type_distribution': type_counts,
                'last_update': metadata.get('lastUpdate'),
                'integrated_reports': type_counts.get('integrated', 0)
            }
            
            self.logger.info(f"📊 통계 업데이트 완료: {statistics}")
            return statistics
            
        except Exception as e:
            self.logger.error(f"❌ 통계 업데이트 실패: {e}")
            return {}
    
    def validate_metadata_integrity(self) -> Dict[str, bool]:
        """
        메타데이터 무결성 검증
        
        Returns:
            Dict[str, bool]: 검증 결과
        """
        self.logger.info("🔍 메타데이터 무결성 검증 시작...")
        
        results = {}
        
        for name, metadata_file in self.metadata_files.items():
            try:
                metadata = self.load_metadata(metadata_file)
                
                # 기본 구조 검증
                required_fields = ['lastUpdate', 'totalReports', 'reports']
                structure_valid = all(field in metadata for field in required_fields)
                
                # 리포트 개수 일치 검증
                count_valid = metadata['totalReports'] == len(metadata['reports'])
                
                # 각 리포트 필드 검증
                reports_valid = True
                for report in metadata['reports']:
                    required_report_fields = ['id', 'filename', 'title', 'type', 'date']
                    if not all(field in report for field in required_report_fields):
                        reports_valid = False
                        break
                
                results[name] = structure_valid and count_valid and reports_valid
                
                if results[name]:
                    self.logger.info(f"✅ {name} 메타데이터 무결성 검증 통과")
                else:
                    self.logger.error(f"❌ {name} 메타데이터 무결성 검증 실패")
                    
            except Exception as e:
                self.logger.error(f"❌ {name} 메타데이터 검증 중 오류: {e}")
                results[name] = False
        
        return results
    
    def log_registration_results(self, results: Dict[str, Any]):
        """
        등록 결과 로깅
        
        Args:
            results (Dict[str, Any]): 등록 결과
        """
self.logger.info("/n"_+_" = "*60)
        self.logger.info("📋 통합 리포트 등록 결과 요약")
        self.logger.info("="*60)
        self.logger.info(f"🔍 발견된 리포트: {results['total_found']}개")
        self.logger.info(f"✅ 성공적으로 등록: {results['successfully_registered']}개")
        self.logger.info(f"❌ 등록 실패: {results['failed_registrations']}개")
        
        if results['successfully_registered'] > 0:
            self.logger.info(f"📊 성공률: {results['successfully_registered']/results['total_found']*100:.1f}%")
            
            self.logger.info("/n📁 등록된 리포트:")
            for report in results['registered_reports']:
                self.logger.info(f"  📅 {report['date']}: {report['filename']}")
        
        if results['successfully_registered'] > 0:
            self.logger.info(f"/n🎉 총 {results['successfully_registered']}개의 통합 리포트가 메타데이터에 등록되었습니다!")
        else:
            self.logger.warning("/n⚠️ 등록된 리포트가 없습니다.")

def main():
    """메인 실행 함수"""
    manager = MetadataResetManager()
    
    # 1. 메타데이터 초기화
    print("🔄 메타데이터 초기화 중...")
    reset_success = manager.reset_metadata_index()
    
    # 2. 통합 리포트 스캔 및 등록
    print("🔍 통합 리포트 스캔 및 등록 중...")
    registration_results = manager.scan_and_register_integrated_reports()
    
    # 3. 통계 업데이트
    print("📊 통계 업데이트 중...")
    statistics = manager.update_report_statistics()
    
    # 4. 무결성 검증
    print("🔍 메타데이터 무결성 검증 중...")
    integrity_results = manager.validate_metadata_integrity()
    
    return {
        'reset_success': reset_success,
        'registration_results': registration_results,
        'statistics': statistics,
        'integrity_results': integrity_results
    }

if __name__ == "__main__":
    main()