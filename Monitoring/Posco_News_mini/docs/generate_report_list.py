#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
리포트 목록 생성기

실제 파일 시스템에서 리포트 파일들을 스캔하여
JavaScript 코드로 변환합니다.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def get_file_size(filepath):
    """파일 크기를 읽기 쉬운 형태로 변환"""
    size = os.path.getsize(filepath)
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size // 1024}KB"
    else:
        return f"{size // (1024 * 1024)}MB"

def parse_filename(filename):
    """파일명에서 정보 추출"""
    # posco_analysis_newyork-market-watch_20250728_134934.html
    parts = filename.replace('.html', '').split('_')
    if len(parts) >= 4:
        news_type = parts[2]
        date_str = parts[3]
        time_str = parts[4] if len(parts) > 4 else "000000"
        
        # 날짜 파싱
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            date_formatted = date_obj.strftime("%Y-%m-%d")
            
            # 시간 파싱
            if len(time_str) == 6:
                time_obj = datetime.strptime(time_str, "%H%M%S")
                time_formatted = time_obj.strftime("%H:%M")
            else:
                time_formatted = "00:00"
                
        except ValueError:
            date_formatted = "2025-07-28"
            time_formatted = "00:00"
        
        return {
            'type': news_type.upper().replace('-', ' '),
            'date': date_formatted,
            'time': time_formatted
        }
    
    return {
        'type': 'UNKNOWN',
        'date': '2025-07-28',
        'time': '00:00'
    }

def generate_report_list():
    """리포트 목록 생성"""
    reports_dir = Path("reports")
    reports = []
    
    if reports_dir.exists():
        for file in reports_dir.glob("*.html"):
            if file.name.startswith("posco_analysis_"):
                file_info = parse_filename(file.name)
                file_size = get_file_size(file)
                
                # 제목 생성
                type_mapping = {
                    'NEWYORK MARKET WATCH': '뉴욕 시장 분석',
                    'EXCHANGE RATE': '환율 분석',
                    'KOSPI CLOSE': 'KOSPI 종가 분석'
                }
                title = type_mapping.get(file_info['type'], f"{file_info['type']} 분석")
                
                reports.append({
                    'title': title,
                    'type': file_info['type'],
                    'date': file_info['date'],
                    'time': file_info['time'],
                    'url': f"reports/{file.name}",
                    'size': file_size
                })
    
    # 날짜/시간 기준으로 정렬 (최신순)
    reports.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
    
    return reports

def generate_javascript():
    """JavaScript 코드 생성"""
    reports = generate_report_list()
    
    js_code = f"""
        // 사용 가능한 리포트 목록 가져오기
        function getAvailableReports() {{
            return {json.dumps(reports, ensure_ascii=False, indent=4)};
        }}
    """
    
    return js_code

def update_index_html():
    """index.html 파일 업데이트"""
    index_file = Path("index.html")
    
    if not index_file.exists():
        print("index.html 파일을 찾을 수 없습니다.")
        return
    
    # 기존 파일 읽기
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 새로운 JavaScript 코드 생성
    new_js = generate_javascript()
    
    # 기존 getAvailableReports 함수 교체
    import re
    pattern = r'function getAvailableReports\(\) \{[\s\S]*?\}'
    
    if re.search(pattern, content):
        content = re.sub(pattern, new_js.strip(), content)
    else:
        # 함수가 없으면 script 태그 끝에 추가
        content = content.replace('</script>', f'\n{new_js}\n</script>')
    
    # 파일 저장
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[SUCCESS] index.html 업데이트 완료 ({len(generate_report_list())}개 리포트)")

if __name__ == "__main__":
    update_index_html() 