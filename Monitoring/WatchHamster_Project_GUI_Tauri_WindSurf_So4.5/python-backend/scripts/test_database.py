"""
데이터베이스 무결성 및 성능 테스트
"""

import sqlite3
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db


def test_schema():
    """스키마 검증"""
    print("📋 스키마 검증")
    print("-" * 80)
    
    conn = sqlite3.connect('watchhamster.db')
    cursor = conn.cursor()
    
    # 테이블 목록
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"✅ 테이블 개수: {len(tables)}개")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count}개 레코드")
    
    conn.close()
    print()


def test_indexes():
    """인덱스 검증"""
    print("🔍 인덱스 검증")
    print("-" * 80)
    
    conn = sqlite3.connect('watchhamster.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL;")
    indexes = cursor.fetchall()
    
    print(f"✅ 인덱스 개수: {len(indexes)}개")
    for idx in indexes:
        print(f"   - {idx[0]} on {idx[1]}")
    
    conn.close()
    print()


def test_foreign_keys():
    """외래 키 검증"""
    print("🔗 외래 키 검증")
    print("-" * 80)
    
    conn = sqlite3.connect('watchhamster.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()
    
    if errors:
        print(f"❌ 외래 키 오류: {len(errors)}개")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ 외래 키 무결성: 정상")
    
    conn.close()
    print()


def test_integrity():
    """데이터 무결성 검증"""
    print("✅ 데이터 무결성 검증")
    print("-" * 80)
    
    conn = sqlite3.connect('watchhamster.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()[0]
    
    if result == "ok":
        print("✅ 데이터베이스 무결성: 정상")
    else:
        print(f"❌ 무결성 오류: {result}")
    
    conn.close()
    print()


def test_query_performance():
    """쿼리 성능 테스트"""
    print("⚡ 쿼리 성능 테스트")
    print("-" * 80)
    
    db = get_db()
    
    # 1. 회사 조회
    start = time.time()
    companies = db.get_all_companies()
    elapsed = (time.time() - start) * 1000
    print(f"✅ 회사 목록 조회: {elapsed:.2f}ms ({len(companies)}개)")
    
    # 2. 회사 상세 조회
    start = time.time()
    company = db.get_company('posco')
    elapsed = (time.time() - start) * 1000
    print(f"✅ 회사 상세 조회: {elapsed:.2f}ms")
    
    # 3. 웹훅 설정 조회
    start = time.time()
    webhooks = db.get_webhook_configs('posco')
    elapsed = (time.time() - start) * 1000
    print(f"✅ 웹훅 설정 조회: {elapsed:.2f}ms ({len(webhooks)}개)")
    
    # 4. API 설정 조회
    start = time.time()
    api_configs = db.get_api_configs('posco')
    elapsed = (time.time() - start) * 1000
    print(f"✅ API 설정 조회: {elapsed:.2f}ms ({len(api_configs)}개)")
    
    # 5. 웹훅 로그 조회
    start = time.time()
    logs = db.get_webhook_logs('posco', limit=100)
    elapsed = (time.time() - start) * 1000
    print(f"✅ 웹훅 로그 조회: {elapsed:.2f}ms ({len(logs)}개)")
    
    # 6. 통계 조회
    start = time.time()
    stats = db.get_webhook_stats('posco')
    elapsed = (time.time() - start) * 1000
    print(f"✅ 통계 조회: {elapsed:.2f}ms")
    
    print()


def test_data_consistency():
    """데이터 일관성 검증"""
    print("🔄 데이터 일관성 검증")
    print("-" * 80)
    
    conn = sqlite3.connect('watchhamster.db')
    cursor = conn.cursor()
    
    # 1. 고아 레코드 확인 (webhook_configs)
    cursor.execute("""
        SELECT COUNT(*) FROM webhook_configs 
        WHERE company_id NOT IN (SELECT id FROM companies)
    """)
    orphan_webhooks = cursor.fetchone()[0]
    
    if orphan_webhooks > 0:
        print(f"❌ 고아 웹훅 설정: {orphan_webhooks}개")
    else:
        print("✅ 웹훅 설정 일관성: 정상")
    
    # 2. 고아 레코드 확인 (api_configs)
    cursor.execute("""
        SELECT COUNT(*) FROM api_configs 
        WHERE company_id NOT IN (SELECT id FROM companies)
    """)
    orphan_apis = cursor.fetchone()[0]
    
    if orphan_apis > 0:
        print(f"❌ 고아 API 설정: {orphan_apis}개")
    else:
        print("✅ API 설정 일관성: 정상")
    
    # 3. 고아 레코드 확인 (webhook_logs)
    cursor.execute("""
        SELECT COUNT(*) FROM webhook_logs 
        WHERE company_id NOT IN (SELECT id FROM companies)
    """)
    orphan_logs = cursor.fetchone()[0]
    
    if orphan_logs > 0:
        print(f"❌ 고아 로그: {orphan_logs}개")
    else:
        print("✅ 로그 일관성: 정상")
    
    conn.close()
    print()


def test_posco_migration():
    """POSCO 마이그레이션 검증"""
    print("🏭 POSCO 마이그레이션 검증")
    print("-" * 80)
    
    db = get_db()
    
    # POSCO 회사 확인
    company = db.get_company('posco')
    if company:
        print(f"✅ POSCO 회사: {company['display_name']}")
        print(f"   - ID: {company['id']}")
        print(f"   - 활성: {company['is_active']}")
    else:
        print("❌ POSCO 회사 없음")
        return
    
    # 웹훅 설정 확인
    webhooks = db.get_webhook_configs('posco')
    print(f"✅ 웹훅 설정: {len(webhooks)}개")
    for wh in webhooks:
        print(f"   - {wh['channel_name']}: {wh['bot_name']}")
    
    # API 설정 확인
    api_configs = db.get_api_configs('posco')
    print(f"✅ API 설정: {len(api_configs)}개")
    for api in api_configs:
        print(f"   - {api['api_name']}: {api['api_url'][:50]}...")
    
    print()


def main():
    print("🔍 데이터베이스 무결성 검사 시작")
    print("=" * 80)
    print()
    
    try:
        test_schema()
        test_indexes()
        test_foreign_keys()
        test_integrity()
        test_data_consistency()
        test_posco_migration()
        test_query_performance()
        
        print("=" * 80)
        print("✅ 데이터베이스 무결성 검사 완료!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 검사 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
