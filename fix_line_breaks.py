#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
줄바꿈 문자 수정 스크립트
/n을 \n으로 수정
"""

import os
import re

def fix_line_breaks(file_path: str) -> bool:
    """파일의 잘못된 줄바꿈 문자 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # /n을 \n으로 수정
        fixed_content = content.replace('/n', '\\n')
        
        # 변경사항이 있는지 확인
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"✅ 줄바꿈 문자 수정 완료: {file_path}")
            return True
        else:
            print(f"ℹ️ 수정할 줄바꿈 문자가 없습니다: {file_path}")
            return True
            
    except Exception as e:
        print(f"❌ 줄바꿈 문자 수정 실패: {e}")
        return False

if __name__ == "__main__":
    success = fix_line_breaks("core/monitoring/config.py")
    exit(0 if success else 1)