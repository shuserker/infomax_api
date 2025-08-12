#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모니터 파일의 f-string 줄바꿈 문제 수정
"""

import re
import os

def fix_fstring_line_breaks(file_path):
    """f-string에서 잘못된 줄바꿈을 수정"""
    
    print(f"📝 {file_path} 파일의 f-string 줄바꿈 문제 수정 중...")
    
    # 백업 생성
    backup_path = file_path + '.backup_before_fix'
    if not os.path.exists(backup_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 백업 생성: {backup_path}")
    
    # 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 문제가 되는 패턴들 수정
    fixes = [
        # f-string에서 줄바꿈 문자가 따옴표 밖에 있는 경우
        (r'f"([^"]*)\n"', r'f"\1\\n"'),
        
        # 여러 줄 f-string에서 줄바꿈 처리
        (r'f"([^"]*)\n([^"]*)"', r'f"\1\\n\2"'),
        
        # 백슬래시 뒤에 잘못된 줄바꿈
        (r'\\n"\.join', r'\"\\n\".join'),
        
        # 따옴표가 제대로 닫히지 않은 f-string
        (r'f"([^"]*)\n\s*"', r'f"\1\\n"'),
    ]
    
    original_content = content
    
    # 각 패턴별로 수정
    for pattern, replacement in fixes:
        matches = re.findall(pattern, content)
        if matches:
            print(f"🔧 패턴 '{pattern}' 발견: {len(matches)}개")
            content = re.sub(pattern, replacement, content)
    
    # 수동으로 알려진 문제들 수정
    manual_fixes = [
        # 특정 줄의 문제들
        ('f"⚠️ POSCO WatchHamster v3.0.0 성능 알림\n\n"', 'f"⚠️ POSCO WatchHamster v3.0.0 성능 알림\\n\\n"'),
        ('f"📅 시간: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\n"', 'f"📅 시간: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\\n"'),
        ('f"📊 현재 상태:\n"', 'f"📊 현재 상태:\\n"'),
        ('f"  • CPU 사용률: {current_stats.get(\'cpu_percent\', 0):.1f}%\n"', 'f"  • CPU 사용률: {current_stats.get(\'cpu_percent\', 0):.1f}%\\n"'),
        ('f"  • 메모리 사용률: {current_stats.get(\'memory_percent\', 0):.1f}%\n"', 'f"  • 메모리 사용률: {current_stats.get(\'memory_percent\', 0):.1f}%\\n"'),
        ('f"  • 프로세스 수: {current_stats.get(\'process_count\', 0)}개\n"', 'f"  • 프로세스 수: {current_stats.get(\'process_count\', 0)}개\\n"'),
        ('f"  • 성능 수준: {performance_summary.get(\'performance_level\', \'unknown\')}\n\n"', 'f"  • 성능 수준: {performance_summary.get(\'performance_level\', \'unknown\')}\\n\\n"'),
        ('f"🔧 권장사항 ({len(recommendations)}개):\n"', 'f"🔧 권장사항 ({len(recommendations)}개):\\n"'),
        ('f"  {i}. {priority_emoji} {rec.title}\n"', 'f"  {i}. {priority_emoji} {rec.title}\\n"'),
        ('f"     예상 효과: {rec.estimated_improvement}\n"', 'f"     예상 효과: {rec.estimated_improvement}\\n"'),
        ('f"  ... 외 {len(recommendations) - 3}개 추가 권장사항\n"', 'f"  ... 외 {len(recommendations) - 3}개 추가 권장사항\\n"'),
        ('f"\n💡 자세한 내용은 성능 모니터링 로그를 확인하세요."', 'f"\\n💡 자세한 내용은 성능 모니터링 로그를 확인하세요."'),
        ('f"📈 POSCO WatchHamster v3.0.0 성능 개선 보고\n\n"', 'f"📈 POSCO WatchHamster v3.0.0 성능 개선 보고\\n\\n"'),
        ('f"📅 시간: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\n"', 'f"📅 시간: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\\n"'),
        ('f"🎯 주요 개선사항:\n{improvement_summary}\n\n"', 'f"🎯 주요 개선사항:\\n{improvement_summary}\\n\\n"'),
    ]
    
    for old, new in manual_fixes:
        if old in content:
            print(f"🔧 수동 수정: {old[:50]}...")
            content = content.replace(old, new)
    
    # 더 일반적인 패턴으로 f-string 내의 줄바꿈 수정
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # f-string이 시작되고 끝나지 않은 경우 찾기
        if 'f"' in line and line.count('"') % 2 == 1:
            # 다음 줄에서 따옴표를 찾아서 합치기
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('"') or ('"' in next_line and not next_line.startswith('f"')):
                    # 줄바꿈을 \\n으로 변경하고 합치기
                    combined = line + '\\n' + next_line
                    fixed_lines.append(combined)
                    lines[i + 1] = ''  # 다음 줄은 빈 줄로 만들기
                    continue
        
        if line:  # 빈 줄이 아닌 경우만 추가
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 변경사항이 있는지 확인
    if content != original_content:
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 파일 수정 완료: {file_path}")
        
        # 문법 검사
        try:
            import py_compile
            py_compile.compile(file_path, doraise=True)
            print("✅ 문법 검사 통과")
            return True
        except py_compile.PyCompileError as e:
            print(f"❌ 문법 오류 여전히 존재: {e}")
            return False
    else:
        print("ℹ️ 변경사항 없음")
        return True

def main():
    """메인 실행 함수"""
    monitor_file = 'core/monitoring/monitor_WatchHamster_v3.0.py'
    
    if not os.path.exists(monitor_file):
        print(f"❌ 파일 없음: {monitor_file}")
        return False
    
    success = fix_fstring_line_breaks(monitor_file)
    
    if success:
        print("🎉 f-string 줄바꿈 문제 수정 완료!")
    else:
        print("⚠️ 일부 문제가 남아있을 수 있습니다.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)