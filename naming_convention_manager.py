#!/usr/bin/env python3
"""
POSCO 네이밍 컨벤션 관리 시스템
POSCO Naming Convention Management System

워치햄스터 v3.0 및 포스코 뉴스 var_250808 네이밍 규칙을 관리합니다.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import verify_folder_reorganization

class ComponentType(Enum):
    """컴포넌트 타입 정의"""
    WATCHHAMSTER = "watchhamster"
    POSCO_NEWS_250808 = "posco_news_250808"
    UNKNOWN = "unknown"

@dataclass
class NamingRule:
    """네이밍 규칙 데이터 모델"""
    component: ComponentType
    version: str
    file_pattern: str
    folder_pattern: str
    class_pattern: str
    variable_pattern: str
    comment_pattern: str

class NamingConventionManager:
    """네이밍 컨벤션 관리자"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[ComponentType, NamingRule]:
        """네이밍 규칙 초기화"""
        return {
            ComponentType.WATCHHAMSTER: NamingRule(
                component=ComponentType.WATCHHAMSTER,
                version="v3.0",
                file_pattern="WatchHamster_v3.var_0__{name}",
                folder_pattern="WatchHamster_v3.0",
                class_pattern="WatchHamsterV30{name}",
                variable_pattern="watchhamster_v3_0_{name}",
                comment_pattern="WatchHamster v3.0"
            ),
            ComponentType.POSCO_NEWS_250808: NamingRule(
                component=ComponentType.POSCO_NEWS_250808,
                version="var_250808",
                file_pattern="POSCO_News_250808_{name}",
                folder_pattern="POSCO_News_250808",
                class_pattern="PoscoNews250808{name}",
                variable_pattern="posco_news_250808_{name}",
                comment_pattern="POSCO News var_250808"
            )
        }
    
    def get_rule(self, component: ComponentType) -> Optional[NamingRule]:
        """컴포넌트별 네이밍 규칙 반환"""
        return self.rules.get(component)
    
    def detect_component_type(self, text: str) -> ComponentType:
        """텍스트에서 컴포넌트 타입 감지"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['watchhamster', 'watch_hamster']):
            return ComponentType.WATCHHAMSTER
        elif any(keyword in text_lower for keyword in ['posco_news', 'posco news']):
            return ComponentType.POSCO_NEWS_250808
        else:
            return ComponentType.UNKNOWN
    
    def standardize_filename(self, filename: str, component: ComponentType) -> str:
        """파일명 표준화"""
        rule = self.get_rule(component)
        if not rule:
            return filename
        
        # 기존 버전 정보 제거
        clean_name = self._clean_version_info(filename)
        
        # 새로운 패턴 적용
        if component == ComponentType.WATCHHAMSTER:
            return f"WatchHamster_v3.var_0__{clean_name}"
        elif component == ComponentType.POSCO_NEWS_250808:
            return f"POSCO_News_250808_{clean_name}"
        
        return filename
    
    def standardize_class_name(self, class_name: str, component: ComponentType) -> str:
        """클래스명 표준화"""
        rule = self.get_rule(component)
        if not rule:
            return class_name
        
        # 기존 버전 정보 제거
        clean_name = self._clean_version_info(class_name)
        
        # 새로운 패턴 적용
        if component == ComponentType.WATCHHAMSTER:
            return f"WatchHamsterV30{clean_name}"
        elif component == ComponentType.POSCO_NEWS_250808:
            return f"PoscoNews250808{clean_name}"
        
        return class_name
    
    def standardize_variable_name(self, var_name: str, component: ComponentType) -> str:
        """변수명 표준화"""
        rule = self.get_rule(component)
        if not rule:
            return var_name
        
        # 기존 버전 정보 제거
        clean_name = self._clean_version_info(var_name)
        
        # 새로운 패턴 적용
        if component == ComponentType.WATCHHAMSTER:
            return f"watchhamster_v3_0_{clean_name}"
        elif component == ComponentType.POSCO_NEWS_250808:
            return f"posco_news_250808_{clean_name}"
        
        return var_name
    
    def _clean_version_info(self, name: str) -> str:
        """이름에서 버전 정보 제거"""
        # 일반적인 버전 패턴들 제거
        patterns = [
            r'_v/d+(/./d+)*',  # _v2, _v2.0
            r'_/d{6}',         # _250808
            r'_mini',          # _mini
            r'V/d+',           # V2, V30
            r'v/d+(/./d+)*'    # v2, v3.0
        ]
        
        clean_name = name
        for pattern in patterns:
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
        
        # 연속된 언더스코어 정리
        clean_name = re.sub(r'_+', '_', clean_name)
        clean_name = clean_name.strip('_')
        
        return clean_name or name  # 빈 문자열이면 원본 반환

# 전역 인스턴스
naming_manager = NamingConventionManager()

def get_naming_manager() -> NamingConventionManager:
    """네이밍 매니저 인스턴스 반환"""
    return naming_manager