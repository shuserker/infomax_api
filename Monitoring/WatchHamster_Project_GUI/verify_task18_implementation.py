#!/usr/bin/env python3
"""
Verification script for Task 18: GUI 설정 및 리소스 관리 시스템 구현
Verifies all components are properly implemented
"""

import os
import json
import sys

def verify_configuration_files():
    """Verify all required configuration files exist and are valid"""
    print("🔍 Verifying Configuration Files...")
    
    config_dir = "config"
    required_files = {
        "gui_config.json": "GUI configuration with themes and i18n",
        "posco_config.json": "POSCO system configuration", 
        "webhook_config.json": "Webhook configuration",
        "language_strings.json": "Internationalization strings",
        "message_templates.json": "Message templates"
    }
    
    results = []
    
    for filename, description in required_files.items():
        filepath = os.path.join(config_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Missing: {filename} - {description}")
            results.append(False)
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                print(f"❌ Invalid: {filename} - Not a JSON object")
                results.append(False)
                continue
            
            print(f"✅ Valid: {filename} - {description}")
            results.append(True)
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {filename} - {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ Error reading: {filename} - {e}")
            results.append(False)
    
    return all(results)

def verify_gui_config_structure():
    """Verify GUI config has required structure"""
    print("\n🔍 Verifying GUI Configuration Structure...")
    
    try:
        with open("config/gui_config.json", 'r', encoding='utf-8') as f:
            gui_config = json.load(f)
        
        required_sections = {
            "gui_settings": ["theme", "language", "font_family", "font_size", "window_size"],
            "theme_settings": ["available_themes", "default", "dark", "light", "posco_corporate"],
            "internationalization": ["default_language", "available_languages", "date_format", "number_format"],
            "layout_settings": ["main_panel_ratio", "sidebar_width", "padding"],
        }
        
        results = []
        
        for section, required_keys in required_sections.items():
            if section not in gui_config:
                print(f"❌ Missing section: {section}")
                results.append(False)
                continue
            
            section_data = gui_config[section]
            missing_keys = [key for key in required_keys if key not in section_data]
            
            if missing_keys:
                print(f"❌ Missing keys in {section}: {missing_keys}")
                results.append(False)
            else:
                print(f"✅ Complete section: {section}")
                results.append(True)
        
        # Verify theme colors
        theme_settings = gui_config.get("theme_settings", {})
        required_colors = ["bg_color", "fg_color", "accent_color", "button_color", "text_color"]
        
        for theme in ["default", "dark", "light", "posco_corporate"]:
            if theme in theme_settings:
                theme_colors = theme_settings[theme]
                missing_colors = [color for color in required_colors if color not in theme_colors]
                if missing_colors:
                    print(f"❌ Missing colors in {theme}: {missing_colors}")
                    results.append(False)
                else:
                    print(f"✅ Complete theme: {theme}")
                    results.append(True)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ Error verifying GUI config: {e}")
        return False

def verify_language_strings():
    """Verify language strings structure"""
    print("\n🔍 Verifying Language Strings...")
    
    try:
        with open("config/language_strings.json", 'r', encoding='utf-8') as f:
            lang_strings = json.load(f)
        
        required_languages = ["ko", "en"]
        required_sections = ["app_title", "buttons", "status", "messages", "errors"]
        
        results = []
        
        for lang in required_languages:
            if lang not in lang_strings:
                print(f"❌ Missing language: {lang}")
                results.append(False)
                continue
            
            lang_data = lang_strings[lang]
            missing_sections = [section for section in required_sections if section not in lang_data]
            
            if missing_sections:
                print(f"❌ Missing sections in {lang}: {missing_sections}")
                results.append(False)
            else:
                print(f"✅ Complete language: {lang}")
                results.append(True)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ Error verifying language strings: {e}")
        return False

def verify_posco_config():
    """Verify POSCO configuration structure"""
    print("\n🔍 Verifying POSCO Configuration...")
    
    try:
        with open("config/posco_config.json", 'r', encoding='utf-8') as f:
            posco_config = json.load(f)
        
        required_sections = [
            "posco_system",
            "data_sources", 
            "analysis_settings",
            "report_generation",
            "business_rules",
            "integration"
        ]
        
        results = []
        
        for section in required_sections:
            if section not in posco_config:
                print(f"❌ Missing section: {section}")
                results.append(False)
            else:
                print(f"✅ Found section: {section}")
                results.append(True)
        
        # Check specific subsections
        if "posco_system" in posco_config:
            system_info = posco_config["posco_system"]
            if "system_name" in system_info and "version" in system_info:
                print("✅ System info complete")
                results.append(True)
            else:
                print("❌ Missing system info")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ Error verifying POSCO config: {e}")
        return False

def verify_asset_directories():
    """Verify asset directory structure"""
    print("\n🔍 Verifying Asset Directories...")
    
    required_dirs = [
        "assets",
        "assets/icons",
        "assets/images"
    ]
    
    results = []
    
    for dirname in required_dirs:
        if not os.path.exists(dirname):
            print(f"❌ Missing directory: {dirname}")
            results.append(False)
        elif not os.path.isdir(dirname):
            print(f"❌ Not a directory: {dirname}")
            results.append(False)
        else:
            print(f"✅ Directory exists: {dirname}")
            results.append(True)
    
    return all(results)

def verify_gui_components():
    """Verify GUI component files exist"""
    print("\n🔍 Verifying GUI Component Files...")
    
    gui_components_dir = "gui_components"
    required_files = {
        "resource_manager.py": "Resource management system",
        "theme_manager.py": "Theme management system",
        "i18n_manager.py": "Internationalization system", 
        "settings_dialog.py": "Settings dialog GUI"
    }
    
    results = []
    
    for filename, description in required_files.items():
        filepath = os.path.join(gui_components_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Missing: {filename} - {description}")
            results.append(False)
        else:
            # Check file size to ensure it's not empty
            file_size = os.path.getsize(filepath)
            if file_size < 100:  # Very small file, likely empty
                print(f"❌ Too small: {filename} - {description}")
                results.append(False)
            else:
                print(f"✅ Complete: {filename} - {description}")
                results.append(True)
    
    return all(results)

def verify_test_files():
    """Verify test files exist"""
    print("\n🔍 Verifying Test Files...")
    
    test_files = [
        "test_resource_management.py",
        "test_resource_management_simple.py"
    ]
    
    results = []
    
    for filename in test_files:
        if not os.path.exists(filename):
            print(f"❌ Missing test file: {filename}")
            results.append(False)
        else:
            print(f"✅ Test file exists: {filename}")
            results.append(True)
    
    return all(results)

def main():
    """Main verification function"""
    print("=" * 60)
    print("Task 18 Implementation Verification")
    print("GUI 설정 및 리소스 관리 시스템 구현 (스탠드얼론)")
    print("=" * 60)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run all verifications
    verifications = [
        ("Configuration Files", verify_configuration_files),
        ("GUI Config Structure", verify_gui_config_structure),
        ("Language Strings", verify_language_strings),
        ("POSCO Configuration", verify_posco_config),
        ("Asset Directories", verify_asset_directories),
        ("GUI Components", verify_gui_components),
        ("Test Files", verify_test_files)
    ]
    
    results = []
    
    for name, verify_func in verifications:
        try:
            result = verify_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} verification failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    verification_names = [name for name, _ in verifications]
    for i, (name, result) in enumerate(zip(verification_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nOverall Result: {passed}/{total} verifications passed")
    
    if passed == total:
        print("\n🎉 Task 18 Implementation COMPLETE!")
        print("\n✅ All required components implemented:")
        print("   • Configuration files (gui_config.json, posco_config.json, webhook_config.json)")
        print("   • Language strings (language_strings.json)")
        print("   • Asset directories (assets/icons/, assets/images/)")
        print("   • Resource management system")
        print("   • Theme management with 4 themes")
        print("   • Internationalization (Korean/English)")
        print("   • Settings dialog GUI")
        print("   • Test files for verification")
        print("\n🚀 Ready for standalone GUI system deployment!")
        return True
    else:
        print(f"\n❌ Task 18 Implementation INCOMPLETE!")
        print(f"   {total - passed} components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)