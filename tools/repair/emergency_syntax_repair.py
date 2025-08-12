#!/usr/bin/env python3
"""
Emergency syntax repair tool for deployment preparation
"""

import os
import sys
import re
from pathlib import Path

def fix_common_syntax_errors(file_path):
    """Fix common syntax errors in Python files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Invalid import statements
        content = re.sub(r'import import\s+(\w+)', r'import \1', content)
        
        # Fix 2: Invalid decimal literals (like .0_master)
        content = re.sub(r'(\w+)\.0_(\w+)', r'\1_v3_0_\2', content)
        
        # Fix 3: Invalid syntax in typing imports
        content = re.sub(r'from typing import ([^,\n]*\.md[^,\n]*),', r'from typing import ', content)
        
        # Fix 4: Fix regex patterns with unmatched brackets
        content = re.sub(r'\(r\'([^\']*)\[([^\]]*)\]([^\']*)\',', r"(r'\1\[\2\]\3',", content)
        
        # Fix 5: Fix unmatched parentheses in regex
        content = re.sub(r'r\'([^\']*)\(([^\']*)\[([^\']*)\]([^\']*)\',', r"r'\1(\2\[\3\]\4',", content)
        
        # Fix 6: Fix closing parenthesis issues
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip lines that are clearly problematic
            if 'deployment_verification_checklist.md' in line:
                continue
            if line.strip().startswith('import') and '.md' in line:
                continue
            if line.strip() == ')' and len(fixed_lines) > 0 and '[' in fixed_lines[-1] and ']' not in fixed_lines[-1]:
                # Fix unmatched bracket before closing paren
                fixed_lines[-1] = fixed_lines[-1].replace('[', '').replace('(', '')
                continue
                
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Only write if content changed
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(f'{file_path.suffix}.backup_emergency')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed: {file_path.name}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {str(e)}")
        return False

def main():
    """Main repair function"""
    print("🚨 Emergency Syntax Repair Tool")
    print("=" * 40)
    
    base_path = Path.cwd()
    python_files = list(base_path.glob("*.py"))
    
    fixed_count = 0
    
    for py_file in python_files:
        if py_file.name == 'emergency_syntax_repair.py':
            continue
            
        if fix_common_syntax_errors(py_file):
            fixed_count += 1
    
    print(f"\n📊 수리 완료: {fixed_count}개 파일 수정됨")
    
    # Test compilation of critical files
    critical_files = [
        'naming_convention_manager.py',
        'python_naming_standardizer.py', 
        'shell_batch_script_standardizer.py',
        'documentation_standardizer.py'
    ]
    
    print("\n🔍 핵심 파일 구문 검증...")
    for file_name in critical_files:
        file_path = base_path / file_name
        if file_path.exists():
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, '-m', 'py_compile', str(file_path)
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"✅ {file_name}: 구문 정상")
                else:
                    print(f"❌ {file_name}: 구문 오류 남음")
                    
            except Exception as e:
                print(f"⚠️ {file_name}: 검증 실패 - {str(e)}")

if __name__ == "__main__":
    main()