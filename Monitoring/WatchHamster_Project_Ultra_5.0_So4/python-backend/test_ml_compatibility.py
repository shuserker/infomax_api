"""
AI/ML 패키지 호환성 테스트
WatchHamster Ultra 5.0 환경 설정 검증
"""

import sys
import importlib

def test_package_import(package_name, version_attr='__version__'):
    """패키지 임포트 및 버전 확인"""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, version_attr, 'Unknown')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: Import 실패 - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: 경고 - {e}")
        return True

def test_sklearn_basic():
    """scikit-learn 기본 기능 테스트"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.cluster import KMeans
        
        # TF-IDF 테스트
        vectorizer = TfidfVectorizer(max_features=10)
        test_docs = ["테스트 문서 1", "테스트 문서 2", "다른 테스트"]
        X = vectorizer.fit_transform(test_docs)
        print(f"✅ TF-IDF 벡터화 성공: {X.shape}")
        
        # LDA 테스트
        lda = LatentDirichletAllocation(n_components=2, random_state=42)
        lda.fit(X)
        print(f"✅ LDA 토픽 모델링 성공: {lda.n_components} 토픽")
        
        # K-Means 테스트
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(X.toarray())
        print(f"✅ K-Means 클러스터링 성공: {kmeans.n_clusters} 클러스터")
        
        return True
    except Exception as e:
        print(f"❌ scikit-learn 기능 테스트 실패: {e}")
        return False

def test_numpy_pandas():
    """numpy와 pandas 호환성 테스트"""
    try:
        import numpy as np
        import pandas as pd
        
        # numpy 테스트
        arr = np.array([1, 2, 3, 4, 5])
        print(f"✅ numpy 배열 생성 성공: {arr.shape}")
        
        # pandas 테스트
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        print(f"✅ pandas DataFrame 생성 성공: {df.shape}")
        
        return True
    except Exception as e:
        print(f"❌ numpy/pandas 테스트 실패: {e}")
        return False

def test_existing_packages():
    """기존 패키지와의 호환성 테스트"""
    try:
        import fastapi
        import pydantic
        import psutil
        
        print(f"✅ 기존 패키지 호환성 확인 완료")
        print(f"   - FastAPI: {fastapi.__version__}")
        print(f"   - Pydantic: {pydantic.__version__}")
        print(f"   - psutil: {psutil.__version__}")
        
        return True
    except Exception as e:
        print(f"❌ 기존 패키지 호환성 문제: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("WatchHamster Ultra 5.0 - AI/ML 패키지 호환성 테스트")
    print("=" * 60)
    print()
    
    print("📦 패키지 버전 확인:")
    print("-" * 60)
    results = []
    
    # 필수 패키지 확인
    packages = [
        ('sklearn', '__version__'),
        ('numpy', '__version__'),
        ('pandas', '__version__'),
        ('joblib', '__version__'),
        ('scipy', '__version__')
    ]
    
    for pkg, ver_attr in packages:
        results.append(test_package_import(pkg, ver_attr))
    
    print()
    print("🧪 기능 테스트:")
    print("-" * 60)
    
    # scikit-learn 기능 테스트
    results.append(test_sklearn_basic())
    print()
    
    # numpy/pandas 테스트
    results.append(test_numpy_pandas())
    print()
    
    # 기존 패키지 호환성
    results.append(test_existing_packages())
    print()
    
    # 결과 요약
    print("=" * 60)
    print("테스트 결과 요약:")
    print("-" * 60)
    passed = sum(results)
    total = len(results)
    print(f"통과: {passed}/{total}")
    
    if passed == total:
        print("✅ 모든 테스트 통과! AI/ML 환경 설정 완료")
        return 0
    else:
        print(f"⚠️  {total - passed}개 테스트 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
