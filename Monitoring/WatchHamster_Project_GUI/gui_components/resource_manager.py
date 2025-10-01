#!/usr/bin/env python3
"""
Resource Manager for POSCO News System GUI
Handles themes, internationalization, and configuration management
"""

import json
import os
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

class ResourceManager:
    """Manages GUI resources including themes, languages, and configurations"""
    
    def __init__(self, base_path: str = None):
        """Initialize resource manager
        
        Args:
            base_path: Base path for the GUI system (defaults to current directory)
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "config"
        self.assets_path = self.base_path / "assets"
        
        # Initialize configurations
        self.gui_config = {}
        self.posco_config = {}
        self.webhook_config = {}
        self.language_strings = {}
        self.message_templates = {}
        
        # Current settings
        self.current_theme = "default"
        self.current_language = "ko"
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load all configurations
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all configuration files"""
        try:
            self.load_gui_config()
            self.load_posco_config()
            self.load_webhook_config()
            self.load_language_strings()
            self.load_message_templates()
            
            # Set current settings from config
            self.current_theme = self.gui_config.get("gui_settings", {}).get("theme", "default")
            self.current_language = self.gui_config.get("internationalization", {}).get("default_language", "ko")
            
            self.logger.info("All configurations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {e}")
            self._create_default_configs()
    
    def load_gui_config(self):
        """Load GUI configuration"""
        config_file = self.config_path / "gui_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.gui_config = json.load(f)
        else:
            self.gui_config = self._get_default_gui_config()
            self.save_gui_config()
    
    def load_posco_config(self):
        """Load POSCO system configuration"""
        config_file = self.config_path / "posco_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.posco_config = json.load(f)
        else:
            self.posco_config = self._get_default_posco_config()
            self.save_posco_config()
    
    def load_webhook_config(self):
        """Load webhook configuration"""
        config_file = self.config_path / "webhook_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.webhook_config = json.load(f)
        else:
            self.webhook_config = self._get_default_webhook_config()
            self.save_webhook_config()
    
    def load_language_strings(self):
        """Load language strings"""
        lang_file = self.config_path / "language_strings.json"
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.language_strings = json.load(f)
        else:
            self.language_strings = self._get_default_language_strings()
            self.save_language_strings()
    
    def load_message_templates(self):
        """Load message templates"""
        template_file = self.config_path / "message_templates.json"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                self.message_templates = json.load(f)
        else:
            self.message_templates = {}
    
    def save_gui_config(self):
        """Save GUI configuration"""
        config_file = self.config_path / "gui_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.gui_config, f, indent=2, ensure_ascii=False)
    
    def save_posco_config(self):
        """Save POSCO configuration"""
        config_file = self.config_path / "posco_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.posco_config, f, indent=2, ensure_ascii=False)
    
    def save_webhook_config(self):
        """Save webhook configuration"""
        config_file = self.config_path / "webhook_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.webhook_config, f, indent=2, ensure_ascii=False)
    
    def save_language_strings(self):
        """Save language strings"""
        lang_file = self.config_path / "language_strings.json"
        lang_file.parent.mkdir(parents=True, exist_ok=True)
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(self.language_strings, f, indent=2, ensure_ascii=False)
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get color scheme for specified theme
        
        Args:
            theme_name: Name of theme (defaults to current theme)
            
        Returns:
            Dictionary of color values
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        theme_settings = self.gui_config.get("theme_settings", {})
        return theme_settings.get(theme_name, theme_settings.get("default", {}))
    
    def set_theme(self, theme_name: str):
        """Set current theme
        
        Args:
            theme_name: Name of theme to set
        """
        available_themes = self.gui_config.get("theme_settings", {}).get("available_themes", ["default"])
        if theme_name in available_themes:
            self.current_theme = theme_name
            self.gui_config["gui_settings"]["theme"] = theme_name
            self.save_gui_config()
            self.logger.info(f"Theme changed to: {theme_name}")
        else:
            self.logger.warning(f"Theme not available: {theme_name}")
    
    def get_string(self, key: str, language: str = None) -> str:
        """Get localized string
        
        Args:
            key: String key in dot notation (e.g., 'buttons.start')
            language: Language code (defaults to current language)
            
        Returns:
            Localized string or key if not found
        """
        if language is None:
            language = self.current_language
        
        # Get language strings
        lang_strings = self.language_strings.get(language, {})
        if not lang_strings:
            # Fallback to default language
            fallback_lang = self.gui_config.get("internationalization", {}).get("fallback_language", "en")
            lang_strings = self.language_strings.get(fallback_lang, {})
        
        # Navigate through nested keys
        keys = key.split('.')
        value = lang_strings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key  # Return key if not found
        
        return str(value) if value is not None else key
    
    def set_language(self, language: str):
        """Set current language
        
        Args:
            language: Language code to set
        """
        available_languages = self.gui_config.get("internationalization", {}).get("available_languages", ["ko", "en"])
        if language in available_languages:
            self.current_language = language
            self.gui_config["internationalization"]["default_language"] = language
            self.save_gui_config()
            self.logger.info(f"Language changed to: {language}")
        else:
            self.logger.warning(f"Language not available: {language}")
    
    def get_window_config(self) -> Dict[str, Any]:
        """Get window configuration"""
        return self.gui_config.get("gui_settings", {})
    
    def get_layout_config(self) -> Dict[str, Any]:
        """Get layout configuration"""
        return self.gui_config.get("layout_settings", {})
    
    def get_font_config(self) -> Tuple[str, int]:
        """Get font configuration
        
        Returns:
            Tuple of (font_family, font_size)
        """
        gui_settings = self.gui_config.get("gui_settings", {})
        font_family = gui_settings.get("font_family", "맑은 고딕")
        font_size = gui_settings.get("font_size", 10)
        return font_family, font_size
    
    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        """Get path to asset file
        
        Args:
            asset_type: Type of asset ('icons' or 'images')
            filename: Name of asset file
            
        Returns:
            Path to asset file
        """
        return self.assets_path / asset_type / filename
    
    def update_config(self, config_type: str, key: str, value: Any):
        """Update configuration value
        
        Args:
            config_type: Type of config ('gui', 'posco', 'webhook')
            key: Configuration key in dot notation
            value: New value
        """
        config_map = {
            'gui': self.gui_config,
            'posco': self.posco_config,
            'webhook': self.webhook_config
        }
        
        if config_type not in config_map:
            self.logger.error(f"Unknown config type: {config_type}")
            return
        
        config = config_map[config_type]
        keys = key.split('.')
        
        # Navigate to parent of target key
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        # Save the config
        if config_type == 'gui':
            self.save_gui_config()
        elif config_type == 'posco':
            self.save_posco_config()
        elif config_type == 'webhook':
            self.save_webhook_config()
        
        self.logger.info(f"Updated {config_type} config: {key} = {value}")
    
    def _create_default_configs(self):
        """Create default configurations if they don't exist"""
        self.gui_config = self._get_default_gui_config()
        self.posco_config = self._get_default_posco_config()
        self.webhook_config = self._get_default_webhook_config()
        self.language_strings = self._get_default_language_strings()
        
        # Save all configs
        self.save_gui_config()
        self.save_posco_config()
        self.save_webhook_config()
        self.save_language_strings()
    
    def _get_default_gui_config(self) -> Dict[str, Any]:
        """Get default GUI configuration"""
        return {
            "gui_settings": {
                "window_title": "POSCO 뉴스 시스템 관리자",
                "window_size": {"width": 1200, "height": 800},
                "theme": "default",
                "language": "ko",
                "font_family": "맑은 고딕",
                "font_size": 10
            },
            "theme_settings": {
                "available_themes": ["default", "dark", "light", "posco_corporate"],
                "default": {
                    "bg_color": "#f0f0f0",
                    "fg_color": "#000000",
                    "accent_color": "#0066cc"
                }
            },
            "internationalization": {
                "default_language": "ko",
                "available_languages": ["ko", "en"],
                "fallback_language": "en"
            }
        }
    
    def _get_default_posco_config(self) -> Dict[str, Any]:
        """Get default POSCO configuration"""
        return {
            "posco_system": {
                "system_name": "POSCO 뉴스 분석 시스템",
                "version": "1.0.0"
            }
        }
    
    def _get_default_webhook_config(self) -> Dict[str, Any]:
        """Get default webhook configuration"""
        return {
            "webhook_url": "",
            "webhook_settings": {
                "timeout": 15,
                "retry_attempts": 3
            }
        }
    
    def _get_default_language_strings(self) -> Dict[str, Any]:
        """Get default language strings"""
        return {
            "ko": {
                "app_title": "POSCO 뉴스 시스템 관리자",
                "buttons": {"start": "시작", "stop": "중지"}
            },
            "en": {
                "app_title": "POSCO News System Manager",
                "buttons": {"start": "Start", "stop": "Stop"}
            }
        }

# Global resource manager instance
_resource_manager = None

def get_resource_manager() -> ResourceManager:
    """Get global resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager

def get_theme_colors(theme_name: str = None) -> Dict[str, str]:
    """Get theme colors (convenience function)"""
    return get_resource_manager().get_theme_colors(theme_name)

def get_string(key: str, language: str = None) -> str:
    """Get localized string (convenience function)"""
    return get_resource_manager().get_string(key, language)

def set_theme(theme_name: str):
    """Set theme (convenience function)"""
    get_resource_manager().set_theme(theme_name)

def set_language(language: str):
    """Set language (convenience function)"""
    get_resource_manager().set_language(language)

if __name__ == "__main__":
    # Test the resource manager
    rm = ResourceManager()
    
    print("=== Resource Manager Test ===")
    print(f"Current theme: {rm.current_theme}")
    print(f"Current language: {rm.current_language}")
    
    # Test theme colors
    colors = rm.get_theme_colors()
    print(f"Theme colors: {colors}")
    
    # Test localized strings
    print(f"App title (Korean): {rm.get_string('app_title', 'ko')}")
    print(f"App title (English): {rm.get_string('app_title', 'en')}")
    print(f"Start button: {rm.get_string('buttons.start')}")
    
    # Test theme switching
    rm.set_theme("dark")
    dark_colors = rm.get_theme_colors()
    print(f"Dark theme colors: {dark_colors}")
    
    print("Resource manager test completed successfully!")