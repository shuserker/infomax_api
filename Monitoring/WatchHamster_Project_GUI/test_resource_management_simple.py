#!/usr/bin/env python3
"""
Simple test script for Resource Management System (no GUI)
Tests configuration loading, themes, and internationalization
"""

import os
import sys
import json
import logging

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_resource_manager():
    """Test resource manager functionality"""
    print("Testing Resource Manager...")
    
    try:
        from gui_components.resource_manager import ResourceManager
        
        # Create resource manager
        rm = ResourceManager(current_dir)
        
        # Test configuration loading
        assert rm.gui_config is not None, "GUI config not loaded"
        assert rm.posco_config is not None, "POSCO config not loaded"
        assert rm.webhook_config is not None, "Webhook config not loaded"
        assert rm.language_strings is not None, "Language strings not loaded"
        
        # Test theme functionality
        themes = rm.gui_config.get("theme_settings", {}).get("available_themes", [])
        assert len(themes) > 0, "No themes available"
        
        colors = rm.get_theme_colors("default")
        assert len(colors) > 0, "No theme colors found"
        
        # Test language functionality
        app_title_ko = rm.get_string("app_title", "ko")
        app_title_en = rm.get_string("app_title", "en")
        assert app_title_ko != app_title_en, "Language strings not different"
        
        # Test configuration updates
        rm.update_config("gui", "gui_settings.test_value", "test")
        assert rm.gui_config["gui_settings"]["test_value"] == "test", "Config update failed"
        
        print("✅ Resource Manager: OK")
        return True
        
    except Exception as e:
        print(f"❌ Resource Manager failed: {e}")
        return False

def test_configuration_files():
    """Test configuration file structure"""
    print("Testing Configuration Files...")
    
    try:
        config_dir = os.path.join(current_dir, "config")
        
        # Check required config files exist
        required_files = [
            "gui_config.json",
            "posco_config.json", 
            "webhook_config.json",
            "language_strings.json",
            "message_templates.json"
        ]
        
        for filename in required_files:
            filepath = os.path.join(config_dir, filename)
            if not os.path.exists(filepath):
                print(f"⚠️  Missing config file: {filename}")
                continue
            
            # Test JSON validity
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert isinstance(data, dict), f"Invalid JSON structure in {filename}"
        
        # Test GUI config structure
        gui_config_path = os.path.join(config_dir, "gui_config.json")
        if os.path.exists(gui_config_path):
            with open(gui_config_path, 'r', encoding='utf-8') as f:
                gui_config = json.load(f)
                
            # Check required sections
            required_sections = ["gui_settings", "theme_settings", "internationalization"]
            for section in required_sections:
                assert section in gui_config, f"Missing section: {section}"
        
        # Test language strings structure
        lang_strings_path = os.path.join(config_dir, "language_strings.json")
        if os.path.exists(lang_strings_path):
            with open(lang_strings_path, 'r', encoding='utf-8') as f:
                lang_strings = json.load(f)
                
            # Check required languages
            required_languages = ["ko", "en"]
            for lang in required_languages:
                assert lang in lang_strings, f"Missing language: {lang}"
                assert "app_title" in lang_strings[lang], f"Missing app_title in {lang}"
                assert "buttons" in lang_strings[lang], f"Missing buttons section in {lang}"
        
        print("✅ Configuration Files: OK")
        return True
        
    except Exception as e:
        print(f"❌ Configuration Files failed: {e}")
        return False

def test_asset_directories():
    """Test asset directory structure"""
    print("Testing Asset Directories...")
    
    try:
        assets_dir = os.path.join(current_dir, "assets")
        
        # Check asset directories exist
        required_dirs = ["icons", "images"]
        
        for dirname in required_dirs:
            dirpath = os.path.join(assets_dir, dirname)
            assert os.path.exists(dirpath), f"Missing asset directory: {dirname}"
            assert os.path.isdir(dirpath), f"Asset path is not a directory: {dirname}"
        
        print("✅ Asset Directories: OK")
        return True
        
    except Exception as e:
        print(f"❌ Asset Directories failed: {e}")
        return False

def test_theme_functionality():
    """Test theme functionality without GUI"""
    print("Testing Theme Functionality...")
    
    try:
        from gui_components.resource_manager import ResourceManager
        
        rm = ResourceManager(current_dir)
        
        # Test available themes
        theme_settings = rm.gui_config.get("theme_settings", {})
        available_themes = theme_settings.get("available_themes", [])
        assert len(available_themes) >= 4, "Not enough themes available"
        
        expected_themes = ["default", "dark", "light", "posco_corporate"]
        for theme in expected_themes:
            assert theme in available_themes, f"Missing theme: {theme}"
        
        # Test theme colors
        for theme in expected_themes:
            colors = rm.get_theme_colors(theme)
            assert len(colors) > 0, f"No colors for theme: {theme}"
            
            # Check required color keys
            required_colors = ["bg_color", "fg_color", "accent_color"]
            for color_key in required_colors:
                assert color_key in colors, f"Missing color {color_key} in theme {theme}"
        
        # Test theme switching
        original_theme = rm.current_theme
        rm.set_theme("dark")
        assert rm.current_theme == "dark", "Theme switching failed"
        rm.set_theme(original_theme)  # Restore
        
        print("✅ Theme Functionality: OK")
        return True
        
    except Exception as e:
        print(f"❌ Theme Functionality failed: {e}")
        return False

def test_internationalization():
    """Test internationalization functionality"""
    print("Testing Internationalization...")
    
    try:
        from gui_components.resource_manager import ResourceManager
        
        rm = ResourceManager(current_dir)
        
        # Test available languages
        i18n_config = rm.gui_config.get("internationalization", {})
        available_languages = i18n_config.get("available_languages", [])
        assert len(available_languages) >= 2, "Not enough languages available"
        assert "ko" in available_languages, "Korean language missing"
        assert "en" in available_languages, "English language missing"
        
        # Test language strings
        for lang in available_languages:
            app_title = rm.get_string("app_title", lang)
            assert app_title != "app_title", f"Language string not found for {lang}"
            
            start_button = rm.get_string("buttons.start", lang)
            assert start_button != "buttons.start", f"Button string not found for {lang}"
        
        # Test language switching
        original_language = rm.current_language
        rm.set_language("en")
        assert rm.current_language == "en", "Language switching failed"
        rm.set_language(original_language)  # Restore
        
        # Test string formatting
        test_string = rm.get_string("app_title", "ko")
        assert isinstance(test_string, str), "String not returned as string type"
        
        print("✅ Internationalization: OK")
        return True
        
    except Exception as e:
        print(f"❌ Internationalization failed: {e}")
        return False

def test_posco_config():
    """Test POSCO-specific configuration"""
    print("Testing POSCO Configuration...")
    
    try:
        config_path = os.path.join(current_dir, "config", "posco_config.json")
        assert os.path.exists(config_path), "POSCO config file missing"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            posco_config = json.load(f)
        
        # Check required sections
        required_sections = [
            "posco_system",
            "data_sources", 
            "analysis_settings",
            "report_generation",
            "business_rules",
            "integration"
        ]
        
        for section in required_sections:
            assert section in posco_config, f"Missing POSCO config section: {section}"
        
        # Check system info
        system_info = posco_config["posco_system"]
        assert "system_name" in system_info, "Missing system name"
        assert "version" in system_info, "Missing version"
        
        # Check data sources
        data_sources = posco_config["data_sources"]
        required_sources = ["kospi_api", "exchange_api"]
        for source in required_sources:
            assert source in data_sources, f"Missing data source: {source}"
        
        print("✅ POSCO Configuration: OK")
        return True
        
    except Exception as e:
        print(f"❌ POSCO Configuration failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== POSCO News System - Resource Management Test (Simple) ===")
    print("Testing configuration files, themes, and internationalization")
    print()
    
    # Run all tests
    tests = [
        test_configuration_files,
        test_asset_directories,
        test_resource_manager,
        test_theme_functionality,
        test_internationalization,
        test_posco_config
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=== Test Results Summary ===")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed!")
        print("\n✅ Resource Management System is working correctly!")
        print("✅ Configuration files are properly structured")
        print("✅ Theme system is functional")
        print("✅ Internationalization is working")
        print("✅ Asset directories are set up")
        print("✅ POSCO-specific configuration is complete")
        return True
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)