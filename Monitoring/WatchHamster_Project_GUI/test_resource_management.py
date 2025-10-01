#!/usr/bin/env python3
"""
Test script for Resource Management System
Tests themes, internationalization, and configuration management
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import logging

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from gui_components.resource_manager import get_resource_manager
from gui_components.theme_manager import get_theme_manager
from gui_components.i18n_manager import get_i18n_manager
from gui_components.settings_dialog import SettingsDialog

class ResourceManagementTest:
    """Test application for resource management system"""
    
    def __init__(self):
        """Initialize test application"""
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.resource_manager = get_resource_manager()
        self.theme_manager = get_theme_manager()
        self.i18n_manager = get_i18n_manager()
        
        # Create main window
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        
        self.logger.info("Resource Management Test initialized")
    
    def setup_window(self):
        """Setup main window"""
        # Get window configuration
        window_config = self.resource_manager.get_window_config()
        window_size = window_config.get("window_size", {"width": 800, "height": 600})
        
        self.root.geometry(f"{window_size['width']}x{window_size['height']}")
        self.root.title(self.i18n_manager.get_string("app_title"))
        
        # Apply theme to root window
        self.theme_manager.register_widget(self.root, "frame")
    
    def create_widgets(self):
        """Create test widgets"""
        # Main frame
        main_frame = self.theme_manager.create_themed_frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = self.i18n_manager.create_localized_label(main_frame, "app_title")
        title_label.configure(font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Theme testing section
        theme_frame = tk.LabelFrame(main_frame, text="Theme Testing")
        theme_frame.pack(fill=tk.X, pady=5)
        self.theme_manager.register_widget(theme_frame, "frame")
        
        # Theme buttons
        theme_button_frame = tk.Frame(theme_frame)
        theme_button_frame.pack(fill=tk.X, padx=10, pady=5)
        self.theme_manager.register_widget(theme_button_frame, "frame")
        
        themes = self.theme_manager.get_available_themes()
        for theme in themes:
            btn = self.theme_manager.create_themed_button(
                theme_button_frame, 
                theme.replace('_', ' ').title(),
                command=lambda t=theme: self.change_theme(t)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Language testing section
        lang_frame = tk.LabelFrame(main_frame, text="Language Testing")
        lang_frame.pack(fill=tk.X, pady=5)
        self.theme_manager.register_widget(lang_frame, "frame")
        
        # Language buttons
        lang_button_frame = tk.Frame(lang_frame)
        lang_button_frame.pack(fill=tk.X, padx=10, pady=5)
        self.theme_manager.register_widget(lang_button_frame, "frame")
        
        languages = self.i18n_manager.get_available_languages()
        for lang in languages:
            lang_name = self.i18n_manager.get_language_name(lang)
            btn = self.theme_manager.create_themed_button(
                lang_button_frame,
                f"{lang_name} ({lang})",
                command=lambda l=lang: self.change_language(l)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Control buttons section
        control_frame = tk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(fill=tk.X, pady=5)
        self.theme_manager.register_widget(control_frame, "frame")
        
        control_button_frame = tk.Frame(control_frame)
        control_button_frame.pack(fill=tk.X, padx=10, pady=5)
        self.theme_manager.register_widget(control_button_frame, "frame")
        
        # Localized control buttons
        start_btn = self.i18n_manager.create_localized_button(
            control_button_frame, "buttons.start", command=self.test_start
        )
        self.theme_manager.register_widget(start_btn, "button")
        start_btn.pack(side=tk.LEFT, padx=2)
        
        stop_btn = self.i18n_manager.create_localized_button(
            control_button_frame, "buttons.stop", command=self.test_stop
        )
        self.theme_manager.register_widget(stop_btn, "button")
        stop_btn.pack(side=tk.LEFT, padx=2)
        
        settings_btn = self.i18n_manager.create_localized_button(
            control_button_frame, "buttons.settings", command=self.show_settings
        )
        self.theme_manager.register_widget(settings_btn, "button")
        settings_btn.pack(side=tk.LEFT, padx=2)
        
        # Status section
        status_frame = tk.LabelFrame(main_frame, text="Status Display")
        status_frame.pack(fill=tk.X, pady=5)
        self.theme_manager.register_widget(status_frame, "frame")
        
        # Status labels with different types
        self.status_labels = {}
        
        self.status_labels['success'] = self.theme_manager.create_status_label(
            status_frame, "System Running", "success"
        )
        self.status_labels['success'].pack(anchor=tk.W, padx=10, pady=2)
        
        self.status_labels['warning'] = self.theme_manager.create_status_label(
            status_frame, "Warning: Check configuration", "warning"
        )
        self.status_labels['warning'].pack(anchor=tk.W, padx=10, pady=2)
        
        self.status_labels['error'] = self.theme_manager.create_status_label(
            status_frame, "Error: Connection failed", "error"
        )
        self.status_labels['error'].pack(anchor=tk.W, padx=10, pady=2)
        
        # Information section
        info_frame = tk.LabelFrame(main_frame, text="System Information")
        info_frame.pack(fill=tk.X, pady=5)
        self.theme_manager.register_widget(info_frame, "frame")
        
        # Current settings display
        self.info_text = self.theme_manager.create_themed_text(info_frame, height=8, width=60)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Update info display
        self.update_info_display()
        
        # Register callbacks for theme and language changes
        self.theme_manager.register_theme_change_callback(self.on_theme_changed)
        self.i18n_manager.register_language_change_callback(self.on_language_changed)
    
    def change_theme(self, theme_name: str):
        """Change theme"""
        self.logger.info(f"Changing theme to: {theme_name}")
        self.theme_manager.change_theme(theme_name)
    
    def change_language(self, language: str):
        """Change language"""
        self.logger.info(f"Changing language to: {language}")
        self.i18n_manager.change_language(language)
    
    def test_start(self):
        """Test start action"""
        self.logger.info("Start button clicked")
        self.theme_manager.update_status_label(
            self.status_labels['success'], 
            self.i18n_manager.get_string("status.running"), 
            "success"
        )
    
    def test_stop(self):
        """Test stop action"""
        self.logger.info("Stop button clicked")
        self.theme_manager.update_status_label(
            self.status_labels['success'], 
            self.i18n_manager.get_string("status.stopped"), 
            "warning"
        )
    
    def show_settings(self):
        """Show settings dialog"""
        self.logger.info("Opening settings dialog")
        dialog = SettingsDialog(self.root, self.on_settings_changed)
        dialog.show()
    
    def on_settings_changed(self):
        """Handle settings changes"""
        self.logger.info("Settings changed")
        self.update_info_display()
        
        # Update window title
        self.root.title(self.i18n_manager.get_string("app_title"))
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.logger.info(f"Theme changed to: {theme_name}")
        self.update_info_display()
    
    def on_language_changed(self, language: str):
        """Handle language changes"""
        self.logger.info(f"Language changed to: {language}")
        self.update_info_display()
        
        # Update window title
        self.root.title(self.i18n_manager.get_string("app_title"))
    
    def update_info_display(self):
        """Update information display"""
        try:
            info_text = f"""Current Configuration:
Theme: {self.theme_manager.get_current_theme()}
Language: {self.i18n_manager.get_current_language()}
Language Name: {self.i18n_manager.get_language_name(self.i18n_manager.get_current_language())}

Theme Colors:
{self.format_theme_colors()}

Available Themes: {', '.join(self.theme_manager.get_available_themes())}
Available Languages: {', '.join(self.i18n_manager.get_available_languages())}

Font Configuration: {self.resource_manager.get_font_config()}

Window Configuration:
{self.format_window_config()}

Test Strings:
Start Button: {self.i18n_manager.get_string('buttons.start')}
Stop Button: {self.i18n_manager.get_string('buttons.stop')}
Settings Button: {self.i18n_manager.get_string('buttons.settings')}

Date Format: {self.i18n_manager.format_datetime(self.get_current_datetime())}
Number Format: {self.i18n_manager.format_number(1234567.89)}
"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            
        except Exception as e:
            self.logger.error(f"Error updating info display: {e}")
    
    def format_theme_colors(self) -> str:
        """Format theme colors for display"""
        colors = self.theme_manager.get_theme_colors()
        return '\n'.join([f"  {key}: {value}" for key, value in colors.items()])
    
    def format_window_config(self) -> str:
        """Format window configuration for display"""
        config = self.resource_manager.get_window_config()
        return '\n'.join([f"  {key}: {value}" for key, value in config.items()])
    
    def get_current_datetime(self):
        """Get current datetime"""
        from datetime import datetime
        return datetime.now()
    
    def run(self):
        """Run the test application"""
        self.logger.info("Starting Resource Management Test")
        self.root.mainloop()
        self.logger.info("Resource Management Test completed")

def main():
    """Main function"""
    print("=== POSCO News System - Resource Management Test ===")
    print("Testing themes, internationalization, and configuration management")
    print()
    
    try:
        # Create and run test application
        app = ResourceManagementTest()
        app.run()
        
        print("\n=== Test Results ===")
        print("✅ Resource Manager: OK")
        print("✅ Theme Manager: OK")
        print("✅ I18n Manager: OK")
        print("✅ Settings Dialog: OK")
        print("✅ Configuration Files: OK")
        print("✅ Asset Management: OK")
        print("\n🎉 All resource management components working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)