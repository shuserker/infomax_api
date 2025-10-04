fn main() {
    // 아이콘 파일이 없는 경우 빌드 스킵
    let icon_path = std::path::Path::new("icons/icon.ico");
    if !icon_path.exists() {
        println!("cargo:warning=icon.ico not found, skipping Windows resource compilation");
        return;
    }
    
    tauri_build::build()
}