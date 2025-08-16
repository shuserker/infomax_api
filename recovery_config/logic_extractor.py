#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원본 로직 추출 시스템

정상 커밋 a763ef84의 Python 파일들을 분석하여 핵심 로직을 추출하고
구조화된 형태로 저장하는 시스템입니다.

주요 기능:
- Python 파일 파싱 및 함수/클래스 추출
- 설정 파일 및 환경 변수 추출
- 의존성 관계 분석 및 매핑
- 추출된 로직의 구조화된 저장

작성자: AI Assistant
생성일: 2025-08-12
"""

import os
import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import configparser

from git_commit_analyzer import GitCommitAnalyzer


@dataclass
class FunctionInfo:
    """함수 정보 데이터 클래스"""
    name: str
    args: List[str]
    docstring: Optional[str]
    line_start: int
    line_end: int
    source_code: str
    decorators: List[str]
    is_async: bool


@dataclass
class ClassInfo:
    """클래스 정보 데이터 클래스"""
    name: str
    bases: List[str]
    docstring: Optional[str]
    line_start: int
    line_end: int
    methods: List[FunctionInfo]
    attributes: List[str]
    decorators: List[str]


@dataclass
class ModuleInfo:
    """모듈 정보 데이터 클래스"""
    file_path: str
    module_name: str
    docstring: Optional[str]
    imports: List[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    global_variables: Dict[str, Any]
    dependencies: Set[str]


@dataclass
class ConfigInfo:
    """설정 정보 데이터 클래스"""
    file_path: str
    config_type: str  # 'python', 'json', 'ini', 'env'
    content: Dict[str, Any]
    variables: Dict[str, Any]


class PythonASTAnalyzer:
    """Python AST 분석기"""
    
    def __init__(self):
        self.logger = logging.getLogger("PythonASTAnalyzer")
    
    def parse_file(self, file_path: Path) -> Optional[ModuleInfo]:
        """
        Python 파일을 파싱하여 모듈 정보 추출
        
        Args:
            file_path: 분석할 Python 파일 경로
            
        Returns:
            ModuleInfo 객체 또는 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            module_info = ModuleInfo(
                file_path=str(file_path),
                module_name=file_path.stem,
                docstring=ast.get_docstring(tree),
                imports=[],
                functions=[],
                classes=[],
                global_variables={},
                dependencies=set()
            )
            
            # AST 노드 순회하여 정보 추출
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info.imports.append(alias.name)
                        module_info.dependencies.add(alias.name.split('.')[0])
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info.imports.append(f"from {node.module} import {', '.join(alias.name for alias in node.names)}")
                        module_info.dependencies.add(node.module.split('.')[0])
                
                elif isinstance(node, ast.FunctionDef):
                    if self._is_top_level_function(node, tree):
                        func_info = self._extract_function_info(node, source_code)
                        module_info.functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    if self._is_top_level_class(node, tree):
                        class_info = self._extract_class_info(node, source_code)
                        module_info.classes.append(class_info)
                
                elif isinstance(node, ast.Assign):
                    if self._is_global_variable(node, tree):
                        var_info = self._extract_global_variable(node, source_code)
                        module_info.global_variables.update(var_info)
            
            return module_info
            
        except Exception as e:
            self.logger.error(f"Python 파일 파싱 실패 {file_path}: {e}")
            return None
    
    def _is_top_level_function(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """최상위 레벨 함수인지 확인"""
        for parent in ast.walk(tree):
            if hasattr(parent, 'body') and node in parent.body:
                return isinstance(parent, ast.Module)
        return False
    
    def _is_top_level_class(self, node: ast.ClassDef, tree: ast.AST) -> bool:
        """최상위 레벨 클래스인지 확인"""
        for parent in ast.walk(tree):
            if hasattr(parent, 'body') and node in parent.body:
                return isinstance(parent, ast.Module)
        return False
    
    def _is_global_variable(self, node: ast.Assign, tree: ast.AST) -> bool:
        """전역 변수인지 확인"""
        for parent in ast.walk(tree):
            if hasattr(parent, 'body') and node in parent.body:
                return isinstance(parent, ast.Module)
        return False
    
    def _extract_function_info(self, node: ast.FunctionDef, source_code: str) -> FunctionInfo:
        """함수 정보 추출"""
        args = [arg.arg for arg in node.args.args]
        decorators = [ast.unparse(decorator) for decorator in node.decorator_list]
        
        # 소스 코드에서 함수 부분 추출
        lines = source_code.split('\n')
        func_source = '\n'.join(lines[node.lineno-1:node.end_lineno])
        
        return FunctionInfo(
            name=node.name,
            args=args,
            docstring=ast.get_docstring(node),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            source_code=func_source,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )
    
    def _extract_class_info(self, node: ast.ClassDef, source_code: str) -> ClassInfo:
        """클래스 정보 추출"""
        bases = [ast.unparse(base) for base in node.bases]
        decorators = [ast.unparse(decorator) for decorator in node.decorator_list]
        
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, source_code)
                methods.append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return ClassInfo(
            name=node.name,
            bases=bases,
            docstring=ast.get_docstring(node),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            attributes=attributes,
            decorators=decorators
        )
    
    def _extract_global_variable(self, node: ast.Assign, source_code: str) -> Dict[str, Any]:
        """전역 변수 정보 추출"""
        variables = {}
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                try:
                    # 값을 문자열로 변환
                    value_str = ast.unparse(node.value)
                    variables[target.id] = value_str
                except:
                    variables[target.id] = "<복잡한 표현식>"
        
        return variables


class ConfigExtractor:
    """설정 파일 추출기"""
    
    def __init__(self):
        self.logger = logging.getLogger("ConfigExtractor")
    
    def extract_config_files(self, file_paths: List[Path]) -> List[ConfigInfo]:
        """
        설정 파일들에서 설정 정보 추출
        
        Args:
            file_paths: 설정 파일 경로 목록
            
        Returns:
            ConfigInfo 객체 목록
        """
        config_infos = []
        
        for file_path in file_paths:
            config_info = self._extract_single_config(file_path)
            if config_info:
                config_infos.append(config_info)
        
        return config_infos
    
    def _extract_single_config(self, file_path: Path) -> Optional[ConfigInfo]:
        """단일 설정 파일 분석"""
        try:
            suffix = file_path.suffix.lower()
            
            if suffix == '.py':
                return self._extract_python_config(file_path)
            elif suffix == '.json':
                return self._extract_json_config(file_path)
            elif suffix in ['.ini', '.cfg']:
                return self._extract_ini_config(file_path)
            elif suffix == '.env':
                return self._extract_env_config(file_path)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"설정 파일 추출 실패 {file_path}: {e}")
            return None
    
    def _extract_python_config(self, file_path: Path) -> ConfigInfo:
        """Python 설정 파일 분석"""
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        variables = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        try:
                            value_str = ast.unparse(node.value)
                            variables[target.id] = value_str
                        except:
                            variables[target.id] = "<복잡한 표현식>"
        
        return ConfigInfo(
            file_path=str(file_path),
            config_type='python',
            content={'source_code': source_code},
            variables=variables
        )
    
    def _extract_json_config(self, file_path: Path) -> ConfigInfo:
        """JSON 설정 파일 분석"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        return ConfigInfo(
            file_path=str(file_path),
            config_type='json',
            content=content,
            variables=self._flatten_dict(content)
        )
    
    def _extract_ini_config(self, file_path: Path) -> ConfigInfo:
        """INI 설정 파일 분석"""
        config = configparser.ConfigParser()
        config.read(file_path, encoding='utf-8')
        
        content = {}
        variables = {}
        
        for section_name in config.sections():
            section = dict(config[section_name])
            content[section_name] = section
            
            for key, value in section.items():
                variables[f"{section_name}.{key}"] = value
        
        return ConfigInfo(
            file_path=str(file_path),
            config_type='ini',
            content=content,
            variables=variables
        )
    
    def _extract_env_config(self, file_path: Path) -> ConfigInfo:
        """환경 변수 파일 분석"""
        variables = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        variables[key.strip()] = value.strip()
        
        return ConfigInfo(
            file_path=str(file_path),
            config_type='env',
            content={'raw_content': variables},
            variables=variables
        )
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """중첩된 딕셔너리를 평면화"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


class DependencyAnalyzer:
    """의존성 분석기"""
    
    def __init__(self):
        self.logger = logging.getLogger("DependencyAnalyzer")
    
    def analyze_dependencies(self, modules: List[ModuleInfo]) -> Dict[str, Any]:
        """
        모듈 간 의존성 관계 분석
        
        Args:
            modules: 분석할 모듈 목록
            
        Returns:
            의존성 분석 결과
        """
        dependency_graph = {}
        external_dependencies = set()
        internal_dependencies = {}
        
        # 모듈명 매핑 생성
        module_names = {module.module_name for module in modules}
        
        for module in modules:
            module_deps = set()
            
            for dep in module.dependencies:
                if dep in module_names:
                    # 내부 의존성
                    module_deps.add(dep)
                else:
                    # 외부 의존성
                    external_dependencies.add(dep)
            
            internal_dependencies[module.module_name] = list(module_deps)
            dependency_graph[module.module_name] = {
                'file_path': module.file_path,
                'internal_deps': list(module_deps),
                'external_deps': [dep for dep in module.dependencies if dep not in module_names]
            }
        
        # 순환 의존성 검사
        circular_deps = self._find_circular_dependencies(internal_dependencies)
        
        return {
            'dependency_graph': dependency_graph,
            'external_dependencies': list(external_dependencies),
            'internal_dependencies': internal_dependencies,
            'circular_dependencies': circular_deps,
            'dependency_count': {
                'total_modules': len(modules),
                'external_deps': len(external_dependencies),
                'internal_connections': sum(len(deps) for deps in internal_dependencies.values())
            }
        }
    
    def _find_circular_dependencies(self, deps: Dict[str, List[str]]) -> List[List[str]]:
        """순환 의존성 찾기"""
        def dfs(node, path, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in deps.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor, path, visited, rec_stack)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # 순환 발견
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        visited = set()
        cycles = []
        
        for node in deps:
            if node not in visited:
                cycle = dfs(node, [], visited, set())
                if cycle:
                    cycles.append(cycle)
        
        return cycles


class LogicExtractor:
    """원본 로직 추출 시스템 메인 클래스"""
    
    def __init__(self, target_commit: str = "a763ef84be08b5b1dab0c0ba20594b141baec7ab"):
        """
        로직 추출기 초기화
        
        Args:
            target_commit: 분석할 커밋 해시
        """
        self.target_commit = target_commit
        self.git_analyzer = GitCommitAnalyzer()
        self.ast_analyzer = PythonASTAnalyzer()
        self.config_extractor = ConfigExtractor()
        self.dependency_analyzer = DependencyAnalyzer()
        
        self.logger = self._setup_logger()
        
        # 출력 디렉토리 설정
        self.output_dir = Path("recovery_config/extracted_logic")
        self.output_dir.mkdir(exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger("LogicExtractor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def extract_from_commit(self) -> Dict[str, Any]:
        """
        지정된 커밋에서 원본 로직 추출
        
        Returns:
            추출된 로직 정보
        """
        self.logger.info(f"커밋 {self.target_commit}에서 원본 로직 추출 시작")
        
        # 1. 커밋 체크아웃 및 파일 목록 가져오기
        files = self.git_analyzer.get_files_in_commit(self.target_commit)
        if not files:
            return {'error': '커밋 파일 목록을 가져올 수 없습니다'}
        
        # 2. 핵심 로직 파일 식별
        core_files = self.git_analyzer.identify_core_logic_files(files)
        self.logger.info(f"핵심 로직 파일 {len(core_files)}개 식별")
        
        # 3. Python 파일 분석
        python_files = [f for f in core_files if f.endswith('.py')]
        modules = self._analyze_python_files(python_files)
        
        # 4. 설정 파일 분석
        config_files = self._identify_config_files(files)
        configs = self.config_extractor.extract_config_files(config_files)
        
        # 5. 의존성 분석
        dependency_analysis = self.dependency_analyzer.analyze_dependencies(modules)
        
        # 6. 스크립트 파일 분석
        script_files = [f for f in core_files if f.endswith(('.sh', '.bat', '.command'))]
        scripts = self._analyze_script_files(script_files)
        
        extraction_result = {
            'extraction_info': {
                'target_commit': self.target_commit,
                'extraction_timestamp': datetime.now().isoformat(),
                'total_files': len(files),
                'core_files': len(core_files),
                'python_files': len(python_files),
                'config_files': len(config_files),
                'script_files': len(script_files)
            },
            'modules': [asdict(module) for module in modules],
            'configs': [asdict(config) for config in configs],
            'scripts': scripts,
            'dependency_analysis': dependency_analysis,
            'file_structure': self._analyze_file_structure(files)
        }
        
        self.logger.info("원본 로직 추출 완료")
        return extraction_result
    
    def _analyze_python_files(self, python_files: List[str]) -> List[ModuleInfo]:
        """Python 파일들 분석"""
        modules = []
        
        for file_path in python_files:
            # 커밋에서 파일 내용 가져오기
            content = self._get_file_content_from_commit(file_path)
            if content:
                # 임시 파일로 저장하여 분석
                temp_file = self.output_dir / f"temp_{Path(file_path).name}"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                module_info = self.ast_analyzer.parse_file(temp_file)
                if module_info:
                    # 원본 경로로 복원
                    module_info.file_path = file_path
                    modules.append(module_info)
                
                # 임시 파일 삭제
                temp_file.unlink()
        
        self.logger.info(f"Python 모듈 {len(modules)}개 분석 완료")
        return modules
    
    def _identify_config_files(self, files: List[str]) -> List[Path]:
        """설정 파일들 식별"""
        config_patterns = [
            r'.*config.*\.py$',
            r'.*settings.*\.py$',
            r'.*\.json$',
            r'.*\.ini$',
            r'.*\.cfg$',
            r'.*\.env$',
            r'requirements\.txt$'
        ]
        
        config_files = []
        for file_path in files:
            if any(re.match(pattern, file_path, re.IGNORECASE) for pattern in config_patterns):
                # 백업 파일 제외
                if not any(exclude in file_path.lower() for exclude in ['backup', 'temp', 'test']):
                    config_files.append(Path(file_path))
        
        return config_files
    
    def _analyze_script_files(self, script_files: List[str]) -> List[Dict[str, Any]]:
        """스크립트 파일들 분석"""
        scripts = []
        
        for file_path in script_files:
            content = self._get_file_content_from_commit(file_path)
            if content:
                script_info = {
                    'file_path': file_path,
                    'file_type': Path(file_path).suffix,
                    'content': content,
                    'commands': self._extract_commands_from_script(content),
                    'variables': self._extract_variables_from_script(content)
                }
                scripts.append(script_info)
        
        self.logger.info(f"스크립트 파일 {len(scripts)}개 분석 완료")
        return scripts
    
    def _extract_commands_from_script(self, content: str) -> List[str]:
        """스크립트에서 명령어 추출"""
        commands = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('::'):
                # 주석이 아닌 실행 가능한 라인
                if any(cmd in line.lower() for cmd in ['python', 'pip', 'git', 'cd', 'echo', 'set']):
                    commands.append(line)
        
        return commands
    
    def _extract_variables_from_script(self, content: str) -> Dict[str, str]:
        """스크립트에서 변수 추출"""
        variables = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Windows batch 변수 (set VAR=value)
            if line.startswith('set ') and '=' in line:
                var_part = line[4:]  # 'set ' 제거
                if '=' in var_part:
                    key, value = var_part.split('=', 1)
                    variables[key.strip()] = value.strip()
            
            # Shell 변수 (VAR=value)
            elif '=' in line and not line.startswith('#'):
                if not any(cmd in line.lower() for cmd in ['if', 'for', 'while', 'echo']):
                    key, value = line.split('=', 1)
                    if key.strip().isidentifier():
                        variables[key.strip()] = value.strip()
        
        return variables
    
    def _analyze_file_structure(self, files: List[str]) -> Dict[str, Any]:
        """파일 구조 분석"""
        structure = {
            'directories': set(),
            'file_types': {},
            'depth_analysis': {},
            'naming_patterns': {}
        }
        
        for file_path in files:
            path_obj = Path(file_path)
            
            # 디렉토리 추가
            for parent in path_obj.parents:
                if str(parent) != '.':
                    structure['directories'].add(str(parent))
            
            # 파일 타입 분석
            suffix = path_obj.suffix.lower()
            if suffix:
                structure['file_types'][suffix] = structure['file_types'].get(suffix, 0) + 1
            
            # 깊이 분석
            depth = len(path_obj.parts) - 1
            structure['depth_analysis'][depth] = structure['depth_analysis'].get(depth, 0) + 1
            
            # 네이밍 패턴 분석
            name = path_obj.stem.lower()
            if 'posco' in name:
                structure['naming_patterns']['posco'] = structure['naming_patterns'].get('posco', 0) + 1
            if 'news' in name:
                structure['naming_patterns']['news'] = structure['naming_patterns'].get('news', 0) + 1
            if 'monitor' in name:
                structure['naming_patterns']['monitor'] = structure['naming_patterns'].get('monitor', 0) + 1
        
        # set을 list로 변환 (JSON 직렬화를 위해)
        structure['directories'] = sorted(list(structure['directories']))
        
        return structure
    
    def _get_file_content_from_commit(self, file_path: str) -> Optional[str]:
        """커밋에서 특정 파일의 내용 가져오기"""
        success, stdout, stderr = self.git_analyzer.execute_git_command([
            'git', 'show', f'{self.target_commit}:{file_path}'
        ])
        
        if success:
            return stdout
        else:
            self.logger.warning(f"파일 내용 가져오기 실패 {file_path}: {stderr}")
            return None
    
    def save_extracted_logic(self, extraction_result: Dict[str, Any]) -> None:
        """추출된 로직을 구조화된 형태로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 직렬화를 위해 set을 list로 변환
        def convert_sets_to_lists(obj):
            if isinstance(obj, dict):
                return {k: convert_sets_to_lists(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets_to_lists(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            else:
                return obj
        
        serializable_result = convert_sets_to_lists(extraction_result)
        
        # 1. 전체 결과를 JSON으로 저장
        main_output = self.output_dir / f"extracted_logic_{timestamp}.json"
        with open(main_output, 'w', encoding='utf-8') as f:
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
        
        # 2. 모듈별로 개별 파일로 저장
        modules_dir = self.output_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        
        for module_data in serializable_result['modules']:
            module_file = modules_dir / f"{module_data['module_name']}.json"
            with open(module_file, 'w', encoding='utf-8') as f:
                json.dump(module_data, f, ensure_ascii=False, indent=2)
        
        # 3. 설정 파일들 저장
        configs_dir = self.output_dir / "configs"
        configs_dir.mkdir(exist_ok=True)
        
        for config_data in serializable_result['configs']:
            config_name = Path(config_data['file_path']).stem
            config_file = configs_dir / f"{config_name}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 4. 스크립트 파일들 저장
        scripts_dir = self.output_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script_data in serializable_result['scripts']:
            script_name = Path(script_data['file_path']).stem
            script_file = scripts_dir / f"{script_name}.json"
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        # 5. 의존성 분석 결과 저장
        dependency_file = self.output_dir / f"dependency_analysis_{timestamp}.json"
        with open(dependency_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_result['dependency_analysis'], f, ensure_ascii=False, indent=2)
        
        # 6. 요약 보고서 생성
        self._generate_extraction_summary(serializable_result, timestamp)
        
        self.logger.info(f"추출된 로직 저장 완료: {self.output_dir}")
    
    def _generate_extraction_summary(self, extraction_result: Dict[str, Any], timestamp: str) -> None:
        """추출 요약 보고서 생성"""
        summary_file = self.output_dir / f"extraction_summary_{timestamp}.md"
        
        info = extraction_result['extraction_info']
        modules = extraction_result['modules']
        configs = extraction_result['configs']
        scripts = extraction_result['scripts']
        deps = extraction_result['dependency_analysis']
        
        summary_content = f"""# 원본 로직 추출 요약 보고서

## 추출 정보
- **대상 커밋**: {info['target_commit']}
- **추출 시간**: {info['extraction_timestamp']}
- **총 파일 수**: {info['total_files']}개
- **핵심 파일 수**: {info['core_files']}개

## 분석 결과

### Python 모듈 ({len(modules)}개)
"""
        
        for module in modules:
            summary_content += f"""
#### {module['module_name']}
- **파일 경로**: {module['file_path']}
- **함수 수**: {len(module['functions'])}개
- **클래스 수**: {len(module['classes'])}개
- **의존성**: {len(module['dependencies'])}개
"""
            
            if module['functions']:
                summary_content += "- **주요 함수**:\n"
                for func in module['functions'][:5]:  # 상위 5개만 표시
                    summary_content += f"  - `{func['name']}({', '.join(func['args'])})`\n"
            
            if module['classes']:
                summary_content += "- **클래스**:\n"
                for cls in module['classes']:
                    summary_content += f"  - `{cls['name']}` (메서드 {len(cls['methods'])}개)\n"
        
        summary_content += f"""

### 설정 파일 ({len(configs)}개)
"""
        
        for config in configs:
            summary_content += f"""
#### {Path(config['file_path']).name}
- **타입**: {config['config_type']}
- **변수 수**: {len(config['variables'])}개
- **경로**: {config['file_path']}
"""
        
        summary_content += f"""

### 스크립트 파일 ({len(scripts)}개)
"""
        
        for script in scripts:
            summary_content += f"""
#### {Path(script['file_path']).name}
- **타입**: {script['file_type']}
- **명령어 수**: {len(script['commands'])}개
- **변수 수**: {len(script['variables'])}개
"""
        
        summary_content += f"""

### 의존성 분석
- **총 모듈 수**: {deps['dependency_count']['total_modules']}개
- **외부 의존성**: {deps['dependency_count']['external_deps']}개
- **내부 연결**: {deps['dependency_count']['internal_connections']}개
- **순환 의존성**: {len(deps['circular_dependencies'])}개

#### 외부 의존성 목록
"""
        
        for dep in sorted(deps['external_dependencies']):
            summary_content += f"- {dep}\n"
        
        if deps['circular_dependencies']:
            summary_content += "\n#### 순환 의존성 경고\n"
            for cycle in deps['circular_dependencies']:
                summary_content += f"- {' → '.join(cycle)}\n"
        
        summary_content += f"""

## 파일 구조 분석
- **디렉토리 수**: {len(extraction_result['file_structure']['directories'])}개
- **파일 타입별 분포**:
"""
        
        for file_type, count in sorted(extraction_result['file_structure']['file_types'].items()):
            summary_content += f"  - {file_type}: {count}개\n"
        
        summary_content += """

## 다음 단계
1. 추출된 로직을 기반으로 핵심 모듈 복원
2. 설정 파일들을 현재 환경에 맞게 조정
3. 의존성 문제 해결
4. 통합 테스트 실행

---
*이 보고서는 자동으로 생성되었습니다.*
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        self.logger.info(f"추출 요약 보고서 생성: {summary_file}")


def main():
    """메인 실행 함수"""
    print("🔍 원본 로직 추출 시스템 시작")
    print("=" * 50)
    
    extractor = LogicExtractor()
    
    try:
        # 1. 원본 로직 추출
        print("📋 1단계: 정상 커밋에서 원본 로직 추출")
        extraction_result = extractor.extract_from_commit()
        
        if 'error' in extraction_result:
            print(f"❌ 오류: {extraction_result['error']}")
            return
        
        info = extraction_result['extraction_info']
        print(f"✅ 로직 추출 완료:")
        print(f"   - 총 파일: {info['total_files']}개")
        print(f"   - 핵심 파일: {info['core_files']}개")
        print(f"   - Python 모듈: {info['python_files']}개")
        print(f"   - 설정 파일: {info['config_files']}개")
        print(f"   - 스크립트 파일: {info['script_files']}개")
        
        # 2. 의존성 분석 결과 출력
        print("\n🔗 2단계: 의존성 분석 결과")
        deps = extraction_result['dependency_analysis']
        print(f"✅ 의존성 분석 완료:")
        print(f"   - 외부 의존성: {deps['dependency_count']['external_deps']}개")
        print(f"   - 내부 연결: {deps['dependency_count']['internal_connections']}개")
        
        if deps['circular_dependencies']:
            print(f"   ⚠️ 순환 의존성: {len(deps['circular_dependencies'])}개 발견")
        
        # 3. 추출된 로직 저장
        print("\n💾 3단계: 추출된 로직 저장")
        extractor.save_extracted_logic(extraction_result)
        print("✅ 로직 저장 완료")
        
        print("\n" + "=" * 50)
        print("🎉 원본 로직 추출 시스템 실행 완료!")
        print("\n📁 출력 파일:")
        print(f"   - 추출된 로직: {extractor.output_dir}")
        print(f"   - 모듈별 분석: {extractor.output_dir}/modules/")
        print(f"   - 설정 파일: {extractor.output_dir}/configs/")
        print(f"   - 스크립트 파일: {extractor.output_dir}/scripts/")
        
    except Exception as e:
        print(f"❌ 원본 로직 추출 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()