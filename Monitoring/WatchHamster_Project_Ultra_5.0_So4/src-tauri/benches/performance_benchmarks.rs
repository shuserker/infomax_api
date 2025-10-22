use criterion::{black_box, criterion_group, criterion_main, Criterion};
use std::time::Duration;
use tempfile::TempDir;
use std::fs;

// 벤치마크를 위한 기본 설정
fn setup_temp_environment() -> TempDir {
    let temp_dir = TempDir::new().unwrap();
    
    // 테스트용 파일들 생성
    for i in 0..100 {
        let file_path = temp_dir.path().join(format!("test_file_{}.txt", i));
        fs::write(&file_path, format!("Test content for file {}", i)).unwrap();
    }
    
    // 테스트용 디렉토리들 생성
    for i in 0..10 {
        let dir_path = temp_dir.path().join(format!("test_dir_{}", i));
        fs::create_dir(&dir_path).unwrap();
        
        // 각 디렉토리에 파일들 생성
        for j in 0..10 {
            let file_path = dir_path.join(format!("nested_file_{}.txt", j));
            fs::write(&file_path, format!("Nested content {} in dir {}", j, i)).unwrap();
        }
    }
    
    temp_dir
}

// 파일 시스템 작업 벤치마크
fn benchmark_filesystem_operations(c: &mut Criterion) {
    let temp_dir = setup_temp_environment();
    let base_path = temp_dir.path();
    
    // 파일 읽기 벤치마크
    c.bench_function("file_read_single", |b| {
        let file_path = base_path.join("test_file_0.txt");
        b.iter(|| {
            let content = fs::read_to_string(&file_path).unwrap();
            black_box(content);
        });
    });
    
    // 여러 파일 읽기 벤치마크
    c.bench_function("file_read_multiple", |b| {
        b.iter(|| {
            for i in 0..10 {
                let file_path = base_path.join(format!("test_file_{}.txt", i));
                let content = fs::read_to_string(&file_path).unwrap();
                black_box(content);
            }
        });
    });
    
    // 디렉토리 목록 조회 벤치마크
    c.bench_function("directory_listing", |b| {
        b.iter(|| {
            let entries = fs::read_dir(base_path).unwrap();
            let count = entries.count();
            black_box(count);
        });
    });
    
    // 파일 쓰기 벤치마크
    c.bench_function("file_write", |b| {
        let mut counter = 0;
        b.iter(|| {
            let file_path = base_path.join(format!("benchmark_write_{}.txt", counter));
            fs::write(&file_path, format!("Benchmark content {}", counter)).unwrap();
            counter += 1;
            black_box(counter);
        });
    });
    
    // 파일 복사 벤치마크
    c.bench_function("file_copy", |b| {
        let source_path = base_path.join("test_file_0.txt");
        let mut counter = 0;
        b.iter(|| {
            let dest_path = base_path.join(format!("benchmark_copy_{}.txt", counter));
            fs::copy(&source_path, &dest_path).unwrap();
            counter += 1;
            black_box(counter);
        });
    });
}

// 시스템 정보 수집 벤치마크
fn benchmark_system_info(c: &mut Criterion) {
    // 호스트명 조회 벤치마크
    c.bench_function("hostname_lookup", |b| {
        b.iter(|| {
            let hostname = gethostname::gethostname();
            black_box(hostname);
        });
    });
    
    // 환경 변수 수집 벤치마크
    c.bench_function("env_vars_collection", |b| {
        b.iter(|| {
            let env_vars: std::collections::HashMap<String, String> = std::env::vars().collect();
            black_box(env_vars);
        });
    });
    
    // 현재 디렉토리 조회 벤치마크
    c.bench_function("current_dir_lookup", |b| {
        b.iter(|| {
            let current_dir = std::env::current_dir().unwrap();
            black_box(current_dir);
        });
    });
    
    // 시스템 상수 접근 벤치마크
    c.bench_function("system_constants", |b| {
        b.iter(|| {
            let os = std::env::consts::OS;
            let arch = std::env::consts::ARCH;
            let family = std::env::consts::FAMILY;
            black_box((os, arch, family));
        });
    });
}

// 문자열 처리 벤치마크
fn benchmark_string_operations(c: &mut Criterion) {
    let test_strings: Vec<String> = (0..1000)
        .map(|i| format!("Test string number {} with some additional content", i))
        .collect();
    
    // 문자열 연결 벤치마크
    c.bench_function("string_concatenation", |b| {
        b.iter(|| {
            let mut result = String::new();
            for s in &test_strings[0..100] {
                result.push_str(s);
                result.push('\n');
            }
            black_box(result);
        });
    });
    
    // 문자열 검색 벤치마크
    c.bench_function("string_search", |b| {
        b.iter(|| {
            let mut count = 0;
            for s in &test_strings {
                if s.contains("number") {
                    count += 1;
                }
            }
            black_box(count);
        });
    });
    
    // JSON 직렬화 벤치마크
    c.bench_function("json_serialization", |b| {
        use serde_json;
        use std::collections::HashMap;
        
        let mut data = HashMap::new();
        for i in 0..100 {
            data.insert(format!("key_{}", i), format!("value_{}", i));
        }
        
        b.iter(|| {
            let json = serde_json::to_string(&data).unwrap();
            black_box(json);
        });
    });
    
    // JSON 역직렬화 벤치마크
    c.bench_function("json_deserialization", |b| {
        use serde_json;
        use std::collections::HashMap;
        
        let mut data = HashMap::new();
        for i in 0..100 {
            data.insert(format!("key_{}", i), format!("value_{}", i));
        }
        let json = serde_json::to_string(&data).unwrap();
        
        b.iter(|| {
            let parsed: HashMap<String, String> = serde_json::from_str(&json).unwrap();
            black_box(parsed);
        });
    });
}

// 비동기 작업 벤치마크
fn benchmark_async_operations(c: &mut Criterion) {
    let rt = tokio::runtime::Runtime::new().unwrap();
    
    // 단순 비동기 작업 벤치마크
    c.bench_function("simple_async_task", |b| {
        b.to_async(&rt).iter(|| async {
            tokio::time::sleep(Duration::from_nanos(1)).await;
            black_box(42);
        });
    });
    
    // 여러 비동기 작업 동시 실행 벤치마크
    c.bench_function("concurrent_async_tasks", |b| {
        b.to_async(&rt).iter(|| async {
            let tasks: Vec<_> = (0..10)
                .map(|i| {
                    tokio::spawn(async move {
                        tokio::time::sleep(Duration::from_nanos(i)).await;
                        i * 2
                    })
                })
                .collect();
            
            let results: Vec<_> = futures::future::join_all(tasks)
                .await
                .into_iter()
                .map(|r| r.unwrap())
                .collect();
            
            black_box(results);
        });
    });
    
    // 채널 통신 벤치마크
    c.bench_function("channel_communication", |b| {
        b.to_async(&rt).iter(|| async {
            let (tx, mut rx) = tokio::sync::mpsc::channel(100);
            
            // 송신 작업
            let sender = tokio::spawn(async move {
                for i in 0..100 {
                    tx.send(i).await.unwrap();
                }
            });
            
            // 수신 작업
            let receiver = tokio::spawn(async move {
                let mut sum = 0;
                while let Some(value) = rx.recv().await {
                    sum += value;
                }
                sum
            });
            
            sender.await.unwrap();
            let result = receiver.await.unwrap();
            black_box(result);
        });
    });
}

// 메모리 작업 벤치마크
fn benchmark_memory_operations(c: &mut Criterion) {
    // 벡터 할당 및 조작 벤치마크
    c.bench_function("vector_operations", |b| {
        b.iter(|| {
            let mut vec = Vec::with_capacity(1000);
            for i in 0..1000 {
                vec.push(i);
            }
            
            vec.sort();
            vec.reverse();
            
            let sum: i32 = vec.iter().sum();
            black_box(sum);
        });
    });
    
    // HashMap 작업 벤치마크
    c.bench_function("hashmap_operations", |b| {
        b.iter(|| {
            let mut map = std::collections::HashMap::with_capacity(1000);
            
            // 삽입
            for i in 0..1000 {
                map.insert(format!("key_{}", i), i);
            }
            
            // 조회
            let mut sum = 0;
            for i in 0..1000 {
                if let Some(value) = map.get(&format!("key_{}", i)) {
                    sum += value;
                }
            }
            
            black_box(sum);
        });
    });
    
    // 문자열 할당 벤치마크
    c.bench_function("string_allocation", |b| {
        b.iter(|| {
            let mut strings = Vec::with_capacity(1000);
            for i in 0..1000 {
                strings.push(format!("String number {} with additional content", i));
            }
            
            let total_length: usize = strings.iter().map(|s| s.len()).sum();
            black_box(total_length);
        });
    });
}

// 벤치마크 그룹 정의
criterion_group!(
    benches,
    benchmark_filesystem_operations,
    benchmark_system_info,
    benchmark_string_operations,
    benchmark_async_operations,
    benchmark_memory_operations
);

criterion_main!(benches);

// 필요한 외부 크레이트들
extern crate gethostname;
extern crate serde_json;