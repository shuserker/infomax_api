#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pages 자동 배포 시스템 (올바른 버전)
HTML 리포트만 publish 브랜치에 배포하여 외부 접근 가능한 공개 URL 생성
"""

import os
import subprocess
import shutil
from pathlib import Path
import time

class GitHubPagesDeployer:
    """GitHub Pages 배포 관리 클래스"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent  # infomax_api 루트
        self.reports_dir = Path(__file__).parent / 'reports'
        
    def deploy_report(self, report_filename):
        """
        개별 리포트를 GitHub Pages에 배포
        
        Args:
            report_filename (str): 배포할 리포트 파일명
            
        Returns:
            str: 배포된 URL 또는 None
        """
        try:
            source_file = self.reports_dir / report_filename
            if not source_file.exists():
                print(f"❌ 리포트 파일을 찾을 수 없음: {report_filename}")
                return None
            
            # Git에 추가 및 커밋
            if self._git_commit_report(report_filename):
                # GitHub Pages URL 반환
                return f"https://shuserker.github.io/infomax_api/reports/{report_filename}"
            else:
                return None
                
        except Exception as e:
            print(f"❌ 리포트 배포 실패: {e}")
            return None
    
    def _git_commit_report(self, report_filename):
        """리포트를 publish 브랜치에만 배포"""
        try:
            os.chdir(self.repo_root)
            
            # 현재 브랜치 확인
            current_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True).stdout.strip()
            
            # publish 브랜치로 전환
            try:
                subprocess.run(['git', 'checkout', 'publish'], check=True)
            except subprocess.CalledProcessError:
                print("❌ publish 브랜치로 전환 실패")
                return False
            
            # reports 디렉토리 생성
            os.makedirs('reports', exist_ok=True)
            
            # 리포트 파일만 복사
            source_file = self.reports_dir / report_filename
            dest_file = Path('reports') / report_filename
            
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                
                # 간단한 index.html 생성
                self._create_publish_index()
                
                # Git에 추가 및 커밋
                subprocess.run(['git', 'add', 'reports/', 'index.html'], check=True)
                commit_message = f"Add report: {report_filename}"
                
                # 변경사항이 있는지 확인
                result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
                if result.returncode == 0:
                    print("📋 변경사항 없음 - 이미 최신 상태")
                    subprocess.run(['git', 'checkout', current_branch], check=True)
                    return True
                
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                
                # publish 브랜치에 푸시
                try:
                    subprocess.run(['git', 'push', 'origin', 'publish'], 
                                 check=True, timeout=30)
                    print(f"✅ 리포트 publish 브랜치에 푸시 완료: {report_filename}")
                    
                    # 원래 브랜치로 돌아가기
                    subprocess.run(['git', 'checkout', current_branch], check=True)
                    return True
                    
                except subprocess.TimeoutExpired:
                    print("⚠️ Git 푸시 타임아웃")
                    subprocess.run(['git', 'checkout', current_branch], check=True)
                    return False
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ Git 푸시 실패: {e}")
                    subprocess.run(['git', 'checkout', current_branch], check=True)
                    return False
            else:
                print(f"❌ 리포트 파일을 찾을 수 없음: {report_filename}")
                subprocess.run(['git', 'checkout', current_branch], check=True)
                return False
                
        except Exception as e:
            print(f"❌ Git 작업 실패: {e}")
            return False
    
    def _create_publish_index(self):
        """publish 브랜치용 간단한 index.html 생성"""
        # 현재 reports 디렉토리의 HTML 파일 목록 생성
        reports_dir = Path('reports')
        html_files = list(reports_dir.glob('*.html')) if reports_dir.exists() else []
        html_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        reports_list = ""
        for html_file in html_files[:20]:  # 최근 20개만
            filename = html_file.name
            file_time = time.ctime(html_file.stat().st_mtime)
            
            # 뉴스 타입 추출
            if 'exchange-rate' in filename:
                news_type = '💱 서환마감'
            elif 'kospi-close' in filename:
                news_type = '📈 증시마감'
            elif 'newyork-market-watch' in filename:
                news_type = '🌆 뉴욕마켓워치'
            else:
                news_type = '📰 뉴스'
            
            reports_list += f"""
            <div class="report-item">
                <div class="report-title">{news_type} 분석 리포트</div>
                <div class="report-meta">생성일: {file_time}</div>
                <a href="./reports/{filename}" class="report-link">📊 리포트 보기</a>
            </div>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 POSCO 뉴스 분석 리포트</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .report-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #4facfe;
        }}
        .report-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .report-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .report-link {{
            display: inline-block;
            background: #4facfe;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 500;
        }}
        .report-link:hover {{
            background: #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 POSCO 뉴스 AI 분석 리포트</h1>
            <p>실시간 시장 분석 및 투자 인사이트</p>
        </div>
        <div class="content">
            <h2>📋 최근 분석 리포트</h2>
            {reports_list}
        </div>
    </div>
</body>
</html>"""
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

# 전역 인스턴스
deployer = GitHubPagesDeployer()

def deploy_report_to_github(report_filename):
    """리포트를 GitHub Pages에 배포"""
    return deployer.deploy_report(report_filename)

if __name__ == "__main__":
    # 테스트 실행
    print("GitHub Pages 배포 시스템 준비 완료")