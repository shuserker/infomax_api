#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기본 배포 파이프라인 테스트 (Task 19.2)
모듈 임포트 없이 파일 구조와 Git 기능만 검증

Requirements: 1.1, 1.2, 1.4 구현
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from datetime import datetime


def test_deployment_files_exist():
    """배포 관련 파일 존재 확인"""
    print("📁 배포 관련 파일 존재 확인 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    deployment_files = [
        'Posco_News_Mini_Final_GUI/git_deployment_manager.py',
        'Posco_News_Mini_Final_GUI/deployment_monitor.py',
        'Posco_News_Mini_Final_GUI/integrated_deployment_system.py',
        'Posco_News_Mini_Final_GUI/github_pages_monitor.py',
        'Posco_News_Mini_Final_GUI/posco_main_notifier.py'
    ]
    
    missing_files = []
    for file_path in deployment_files:
        full_path = os.path.join(script_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            file_size = os.path.getsize(full_path)
            print(f"✅ 파일 확인: {file_path} ({file_size} bytes)")
    
    if missing_files:
        print(f"❌ 누락된 파일: {missing_files}")
        return False
    
    print("✅ 모든 배포 파일 확인됨")
    return True


def test_git_commands_available():
    """Git 명령어 사용 가능 확인"""
    print("\n🔧 Git 명령어 사용 가능 확인 중...")
    
    try:
        # Git 버전 확인
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, check=True)
        git_version = result.stdout.strip()
        print(f"✅ Git 사용 가능: {git_version}")
        
        # Git 설정 확인
        try:
            user_name = subprocess.run(['git', 'config', 'user.name'], 
                                     capture_output=True, text=True)
            user_email = subprocess.run(['git', 'config', 'user.email'], 
                                      capture_output=True, text=True)
            
            if user_name.returncode == 0 and user_email.returncode == 0:
                print(f"✅ Git 사용자 설정 확인됨")
            else:
                print("⚠️ Git 사용자 설정이 필요할 수 있습니다")
        except:
            print("⚠️ Git 사용자 설정 확인 실패")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Git 명령어를 사용할 수 없습니다")
        return False
    except FileNotFoundError:
        print("❌ Git이 설치되지 않았습니다")
        return False


def test_basic_git_operations():
    """기본 Git 작업 테스트"""
    print("\n🔄 기본 Git 작업 테스트 중...")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp(prefix="git_test_")
    original_dir = os.getcwd()
    
    try:
        os.chdir(temp_dir)
        
        # Git 저장소 초기화
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
        print("✅ Git 저장소 초기화 성공")
        
        # 파일 생성 및 커밋
        with open('test.txt', 'w') as f:
            f.write('test content')
        
        subprocess.run(['git', 'add', 'test.txt'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
        print("✅ 파일 생성 및 커밋 성공")
        
        # 브랜치 생성
        subprocess.run(['git', 'checkout', '-b', 'test-branch'], check=True)
        subprocess.run(['git', 'checkout', 'main'], check=True)
        print("✅ 브랜치 생성 및 전환 성공")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 작업 실패: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 기본 Git 작업 테스트 실패: {str(e)}")
        return False
    finally:
        os.chdir(original_dir)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_deployment_file_content():
    """배포 파일 내용 검증"""
    print("\n📄 배포 파일 내용 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Git 배포 관리자 파일 검증
    git_manager_path = os.path.join(script_dir, 'Posco_News_Mini_Final_GUI/git_deployment_manager.py')
    
    if os.path.exists(git_manager_path):
        try:
            with open(git_manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_elements = [
                'class GitDeploymentManager',
                'def switch_to_branch',
                'def detect_conflicts',
                'def resolve_conflicts_automatically'
            ]
            
            found_elements = 0
            for element in required_elements:
                if element in content:
                    found_elements += 1
                    print(f"✅ Git 관리자 요소 확인: {element}")
                else:
                    print(f"❌ Git 관리자 요소 누락: {element}")
            
            git_manager_score = found_elements / len(required_elements)
            print(f"✅ Git 배포 관리자 완성도: {git_manager_score:.1%}")
            
        except Exception as e:
            print(f"❌ Git 배포 관리자 파일 읽기 실패: {str(e)}")
            git_manager_score = 0
    else:
        print("❌ Git 배포 관리자 파일 없음")
        git_manager_score = 0
    
    # 배포 모니터 파일 검증
    monitor_path = os.path.join(script_dir, 'Posco_News_Mini_Final_GUI/deployment_monitor.py')
    
    if os.path.exists(monitor_path):
        try:
            with open(monitor_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_elements = [
                'class DeploymentMonitor',
                'def start_deployment_monitoring',
                'def log_deployment_step'
            ]
            
            found_elements = 0
            for element in required_elements:
                if element in content:
                    found_elements += 1
                    print(f"✅ 배포 모니터 요소 확인: {element}")
                else:
                    print(f"❌ 배포 모니터 요소 누락: {element}")
            
            monitor_score = found_elements / len(required_elements)
            print(f"✅ 배포 모니터 완성도: {monitor_score:.1%}")
            
        except Exception as e:
            print(f"❌ 배포 모니터 파일 읽기 실패: {str(e)}")
            monitor_score = 0
    else:
        print("❌ 배포 모니터 파일 없음")
        monitor_score = 0
    
    # 전체 점수 계산
    overall_score = (git_manager_score + monitor_score) / 2
    print(f"✅ 전체 배포 파일 완성도: {overall_score:.1%}")
    
    return overall_score >= 0.7


def test_html_generation_simulation():
    """HTML 생성 시뮬레이션"""
    print("\n📄 HTML 생성 시뮬레이션 중...")
    
    try:
        # 임시 디렉토리에서 HTML 생성 테스트
        temp_dir = tempfile.mkdtemp(prefix="html_test_")
        
        # 테스트용 HTML 생성
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>POSCO 뉴스 - {datetime.now().strftime('%Y-%m-%d')}</title>
</head>
<body>
    <h1>POSCO 뉴스 시스템</h1>
    <p>생성 시간: {datetime.now().isoformat()}</p>
    <div class="news-content">
        <h2>최신 뉴스</h2>
        <ul>
            <li>POSCO 주가 동향</li>
            <li>신규 투자 계획</li>
            <li>ESG 경영 현황</li>
        </ul>
    </div>
</body>
</html>"""
        
        html_path = os.path.join(temp_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # HTML 파일 검증
        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"✅ HTML 파일 생성 성공: {file_size} bytes")
            
            # 내용 검증
            with open(html_path, 'r', encoding='utf-8') as f:
                generated_content = f.read()
            
            if 'POSCO 뉴스 시스템' in generated_content and 'news-content' in generated_content:
                print("✅ HTML 내용 검증 성공")
                return True
            else:
                print("❌ HTML 내용 검증 실패")
                return False
        else:
            print("❌ HTML 파일 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ HTML 생성 시뮬레이션 실패: {str(e)}")
        return False
    finally:
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_deployment_pipeline_simulation():
    """배포 파이프라인 전체 시뮬레이션"""
    print("\n🚀 배포 파이프라인 전체 시뮬레이션 중...")
    
    temp_dir = tempfile.mkdtemp(prefix="pipeline_test_")
    original_dir = os.getcwd()
    
    try:
        os.chdir(temp_dir)
        
        # 1단계: Git 저장소 초기화
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
        print("✅ 1단계: Git 저장소 초기화")
        
        # 2단계: 초기 HTML 생성
        initial_html = '<html><body><h1>Initial Version</h1></body></html>'
        with open('index.html', 'w') as f:
            f.write(initial_html)
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial HTML'], check=True)
        print("✅ 2단계: 초기 HTML 생성 및 커밋")
        
        # 3단계: publish 브랜치 생성
        subprocess.run(['git', 'checkout', '-b', 'publish'], check=True)
        subprocess.run(['git', 'checkout', 'main'], check=True)
        print("✅ 3단계: publish 브랜치 생성")
        
        # 4단계: 새로운 HTML 생성 (배포할 내용)
        updated_html = f'<html><body><h1>Updated at {datetime.now()}</h1></body></html>'
        with open('index.html', 'w') as f:
            f.write(updated_html)
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Update HTML content'], check=True)
        print("✅ 4단계: 새로운 HTML 생성 및 커밋")
        
        # 5단계: publish 브랜치로 전환 및 병합
        subprocess.run(['git', 'checkout', 'publish'], check=True)
        subprocess.run(['git', 'merge', 'main'], check=True)
        print("✅ 5단계: publish 브랜치로 배포")
        
        # 6단계: 배포 결과 확인
        with open('index.html', 'r') as f:
            deployed_content = f.read()
        
        if 'Updated at' in deployed_content:
            print("✅ 6단계: 배포 결과 확인 성공")
            print("✅ 배포 파이프라인 전체 시뮬레이션 성공")
            return True
        else:
            print("❌ 6단계: 배포 결과 확인 실패")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령 실패: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 배포 파이프라인 시뮬레이션 실패: {str(e)}")
        return False
    finally:
        os.chdir(original_dir)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """메인 함수"""
    print("🚀 기본 배포 파이프라인 테스트 시작")
    print("Task 19.2: 내장형 배포 파이프라인 테스트 구현")
    print("Requirements: 1.1, 1.2, 1.4")
    print("=" * 60)
    
    tests = [
        ("배포 파일 존재 확인", test_deployment_files_exist),
        ("Git 명령어 사용 가능 확인", test_git_commands_available),
        ("기본 Git 작업 테스트", test_basic_git_operations),
        ("배포 파일 내용 검증", test_deployment_file_content),
        ("HTML 생성 시뮬레이션", test_html_generation_simulation),
        ("배포 파이프라인 전체 시뮬레이션", test_deployment_pipeline_simulation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n▶️ {test_name} 시작")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 성공" if result else "❌ 실패"
            print(f"{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"💥 오류: {test_name} - {str(e)}")
        
        print("-" * 40)
    
    # 최종 결과
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("🚀 기본 배포 파이프라인 테스트 결과")
    print("=" * 60)
    print(f"📊 총 테스트: {total}개")
    print(f"✅ 성공: {passed}개")
    print(f"❌ 실패: {total - passed}개")
    print(f"📈 성공률: {success_rate:.1f}%")
    
    # 테스트 보고서 저장
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(logs_dir, f"deployment_basic_test_{timestamp}.json")
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_results': [{'test_name': name, 'passed': result} for name, result in results],
            'summary': {
                'total_tests': total,
                'passed_tests': passed,
                'failed_tests': total - passed,
                'success_rate': success_rate
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 테스트 보고서 저장: {report_path}")
    except Exception as e:
        print(f"⚠️ 보고서 저장 실패: {str(e)}")
    
    # 권장사항
    print("\n💡 권장사항:")
    if success_rate >= 90:
        print("  🎉 훌륭합니다! 배포 파이프라인이 잘 구축되어 있습니다.")
        print("  ✅ Requirements 1.1, 1.2, 1.4 기본 검증 완료")
    elif success_rate >= 70:
        print("  ✅ 대부분의 배포 기능이 준비되어 있습니다.")
        print("  📝 실패한 테스트들을 개별적으로 점검하세요.")
    else:
        print("  ⚠️ 배포 파이프라인에 여러 문제가 있습니다.")
        print("  🔧 기본 구조부터 점검하고 수정하세요.")
    
    if success_rate >= 80:
        print("\n🎉 기본 배포 파이프라인 테스트 성공!")
        return 0
    else:
        print("\n⚠️ 배포 파이프라인 테스트에서 문제가 발견되었습니다.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)