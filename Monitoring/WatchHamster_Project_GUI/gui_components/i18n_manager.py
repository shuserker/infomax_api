#!/usr/bin/env python3
"""
Internationalization Manager for POSCO News System GUI
Provides multi-language support and localization functionality
"""

import tkinter as tk
from typing import Dict, Any, Callable, List, Optional
import logging
from datetime import datetime
import locale
from .resource_manager import get_resource_manager

class I18nManager:
    """Manages internationalization and localization"""
    
    def __init__(self):
        """Initialize i18n manager"""
        self.resource_manager = get_resource_manager()
        self.logger = logging.getLogger(__name__)
        self.localized_widgets = []  # List of widgets with localized text
        self.language_change_callbacks = []  # Callbacks for language changes
        
    def register_widget(self, widget: tk.Widget, text_key: str, widget_type: str = "text"):
        """Register a widget for automatic text updates
        
        Args:
            widget: Widget to register
            text_key: Key for localized text
            widget_type: Type of text update ('text', 'title', etc.)
        """
        self.localized_widgets.append((widget, text_key, widget_type))
        self.update_widget_text(widget, text_key, widget_type)
    
    def register_language_change_callback(self, callback: Callable):
        """Register a callback for language changes
        
        Args:
            callback: Function to call when language changes
        """
        self.language_change_callbacks.append(callback)
    
    def update_widget_text(self, widget: tk.Widget, text_key: str, widget_type: str = "text"):
        """Update widget text with localized string
        
        Args:
            widget: Widget to update
            text_key: Key for localized text
            widget_type: Type of text update
        """
        try:
            localized_text = self.get_string(text_key)
            
            if widget_type == "text":
                if hasattr(widget, 'configure'):
                    widget.configure(text=localized_text)
            elif widget_type == "title":
                if hasattr(widget, 'title'):
                    widget.title(localized_text)
                elif hasattr(widget, 'configure'):
                    widget.configure(text=localized_text)
            elif widget_type == "tooltip":
                # For tooltip text (would need tooltip implementation)
                pass
            
        except Exception as e:
            self.logger.error(f"Error updating widget text: {e}")
    
    def update_all_widgets(self):
        """Update all registered widgets with current language"""
        for widget, text_key, widget_type in self.localized_widgets:
            try:
                if widget.winfo_exists():  # Check if widget still exists
                    self.update_widget_text(widget, text_key, widget_type)
            except tk.TclError:
                # Widget has been destroyed, remove from list
                self.localized_widgets.remove((widget, text_key, widget_type))
    
    def change_language(self, language: str):
        """Change the current language
        
        Args:
            language: Language code to switch to
        """
        try:
            self.resource_manager.set_language(language)
            self.update_all_widgets()
            
            # Call language change callbacks
            for callback in self.language_change_callbacks:
                try:
                    callback(language)
                except Exception as e:
                    self.logger.error(f"Error in language change callback: {e}")
            
            self.logger.info(f"Language changed to: {language}")
            
        except Exception as e:
            self.logger.error(f"Error changing language: {e}")
    
    def get_string(self, key: str, language: str = None, **kwargs) -> str:
        """Get localized string with optional formatting
        
        Args:
            key: String key in dot notation
            language: Language code (defaults to current)
            **kwargs: Format arguments for string formatting
            
        Returns:
            Localized and formatted string
        """
        text = self.resource_manager.get_string(key, language)
        
        # Apply formatting if kwargs provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                self.logger.warning(f"String formatting error for key '{key}': {e}")
        
        return text
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        i18n_config = self.resource_manager.gui_config.get("internationalization", {})
        return i18n_config.get("available_languages", ["ko", "en"])
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.resource_manager.current_language
    
    def get_language_name(self, language_code: str) -> str:
        """Get display name for language code
        
        Args:
            language_code: Language code
            
        Returns:
            Display name for the language
        """
        language_names = {
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
            "zh": "中文",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch"
        }
        return language_names.get(language_code, language_code.upper())
    
    def format_datetime(self, dt: datetime, language: str = None) -> str:
        """Format datetime according to language preferences
        
        Args:
            dt: Datetime object to format
            language: Language code (defaults to current)
            
        Returns:
            Formatted datetime string
        """
        if language is None:
            language = self.get_current_language()
        
        i18n_config = self.resource_manager.gui_config.get("internationalization", {})
        date_formats = i18n_config.get("date_format", {})
        date_format = date_formats.get(language, "%Y-%m-%d %H:%M:%S")
        
        try:
            return dt.strftime(date_format)
        except Exception as e:
            self.logger.error(f"Error formatting datetime: {e}")
            return str(dt)
    
    def format_number(self, number: float, language: str = None) -> str:
        """Format number according to language preferences
        
        Args:
            number: Number to format
            language: Language code (defaults to current)
            
        Returns:
            Formatted number string
        """
        if language is None:
            language = self.get_current_language()
        
        i18n_config = self.resource_manager.gui_config.get("internationalization", {})
        number_formats = i18n_config.get("number_format", {})
        number_format = number_formats.get(language, "comma_separated")
        
        try:
            if number_format == "comma_separated":
                return f"{number:,.2f}"
            else:
                return str(number)
        except Exception as e:
            self.logger.error(f"Error formatting number: {e}")
            return str(number)
    
    def create_localized_label(self, parent: tk.Widget, text_key: str, **kwargs) -> tk.Label:
        """Create a label with localized text
        
        Args:
            parent: Parent widget
            text_key: Key for localized text
            **kwargs: Additional label options
            
        Returns:
            Localized label widget
        """
        text = self.get_string(text_key)
        label = tk.Label(parent, text=text, **kwargs)
        self.register_widget(label, text_key, "text")
        return label
    
    def create_localized_button(self, parent: tk.Widget, text_key: str, command: Callable = None, **kwargs) -> tk.Button:
        """Create a button with localized text
        
        Args:
            parent: Parent widget
            text_key: Key for localized text
            command: Button command
            **kwargs: Additional button options
            
        Returns:
            Localized button widget
        """
        text = self.get_string(text_key)
        button = tk.Button(parent, text=text, command=command, **kwargs)
        self.register_widget(button, text_key, "text")
        return button
    
    def create_language_menu(self, parent: tk.Widget) -> tk.OptionMenu:
        """Create a language selection menu
        
        Args:
            parent: Parent widget
            
        Returns:
            Language selection menu
        """
        available_languages = self.get_available_languages()
        current_language = self.get_current_language()
        
        # Create language options with display names
        language_var = tk.StringVar(value=self.get_language_name(current_language))
        language_options = [self.get_language_name(lang) for lang in available_languages]
        
        def on_language_change(selection):
            # Find language code from display name
            for lang_code in available_languages:
                if self.get_language_name(lang_code) == selection:
                    self.change_language(lang_code)
                    break
        
        menu = tk.OptionMenu(parent, language_var, *language_options, command=on_language_change)
        return menu
    
    def get_error_message(self, error_key: str, **kwargs) -> str:
        """Get localized error message
        
        Args:
            error_key: Error message key
            **kwargs: Format arguments
            
        Returns:
            Localized error message
        """
        return self.get_string(f"errors.{error_key}", **kwargs)
    
    def get_status_message(self, status_key: str, **kwargs) -> str:
        """Get localized status message
        
        Args:
            status_key: Status message key
            **kwargs: Format arguments
            
        Returns:
            Localized status message
        """
        return self.get_string(f"status.{status_key}", **kwargs)
    
    def get_tooltip_text(self, tooltip_key: str, **kwargs) -> str:
        """Get localized tooltip text
        
        Args:
            tooltip_key: Tooltip text key
            **kwargs: Format arguments
            
        Returns:
            Localized tooltip text
        """
        return self.get_string(f"tooltips.{tooltip_key}", **kwargs)

# Global i18n manager instance
_i18n_manager = None

def get_i18n_manager() -> I18nManager:
    """Get global i18n manager instance"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager

def get_string(key: str, language: str = None, **kwargs) -> str:
    """Get localized string (convenience function)"""
    return get_i18n_manager().get_string(key, language, **kwargs)

def change_language(language: str):
    """Change language (convenience function)"""
    get_i18n_manager().change_language(language)

if __name__ == "__main__":
    # Test the i18n manager
    import tkinter as tk
    
    root = tk.Tk()
    root.title("I18n Manager Test")
    root.geometry("400x300")
    
    i18n = get_i18n_manager()
    
    # Create test widgets
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Localized label
    title_label = i18n.create_localized_label(frame, "app_title")
    title_label.pack(pady=5)
    
    # Localized buttons
    start_button = i18n.create_localized_button(frame, "buttons.start")
    start_button.pack(pady=2)
    
    stop_button = i18n.create_localized_button(frame, "buttons.stop")
    stop_button.pack(pady=2)
    
    # Language selection menu
    lang_label = tk.Label(frame, text="Language:")
    lang_label.pack(pady=2)
    
    lang_menu = i18n.create_language_menu(frame)
    lang_menu.pack(pady=2)
    
    # Test datetime formatting
    now = datetime.now()
    datetime_label = tk.Label(frame, text=f"Current time: {i18n.format_datetime(now)}")
    datetime_label.pack(pady=5)
    
    # Test number formatting
    number_label = tk.Label(frame, text=f"Number: {i18n.format_number(1234567.89)}")
    number_label.pack(pady=2)
    
    # Update datetime and number labels when language changes
    def update_labels(language):
        datetime_label.configure(text=f"Current time: {i18n.format_datetime(now)}")
        number_label.configure(text=f"Number: {i18n.format_number(1234567.89)}")
    
    i18n.register_language_change_callback(update_labels)
    
    root.mainloop()