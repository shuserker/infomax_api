#!/usr/bin/env python3
"""
Theme Manager for POSCO News System GUI
Provides theme switching and customization functionality
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional
import logging
from .resource_manager import get_resource_manager

class ThemeManager:
    """Manages GUI themes and provides theme switching functionality"""
    
    def __init__(self):
        """Initialize theme manager"""
        self.resource_manager = get_resource_manager()
        self.logger = logging.getLogger(__name__)
        self.themed_widgets = []  # List of widgets to update when theme changes
        self.theme_change_callbacks = []  # Callbacks to call when theme changes
        
    def register_widget(self, widget: tk.Widget, widget_type: str = "default"):
        """Register a widget for theme updates
        
        Args:
            widget: Tkinter widget to register
            widget_type: Type of widget for specific styling
        """
        self.themed_widgets.append((widget, widget_type))
        self.apply_theme_to_widget(widget, widget_type)
    
    def register_theme_change_callback(self, callback: Callable):
        """Register a callback to be called when theme changes
        
        Args:
            callback: Function to call when theme changes
        """
        self.theme_change_callbacks.append(callback)
    
    def apply_theme_to_widget(self, widget: tk.Widget, widget_type: str = "default"):
        """Apply current theme to a widget
        
        Args:
            widget: Widget to apply theme to
            widget_type: Type of widget for specific styling
        """
        try:
            colors = self.resource_manager.get_theme_colors()
            
            # Base styling for all widgets
            base_config = {
                'bg': colors.get('bg_color', '#f0f0f0'),
                'fg': colors.get('fg_color', '#000000')
            }
            
            # Widget-specific styling
            if widget_type == "button":
                base_config.update({
                    'bg': colors.get('button_color', '#e0e0e0'),
                    'activebackground': colors.get('accent_color', '#0066cc'),
                    'activeforeground': colors.get('bg_color', '#f0f0f0'),
                    'relief': 'raised',
                    'borderwidth': 1
                })
            elif widget_type == "entry":
                base_config.update({
                    'bg': colors.get('bg_color', '#ffffff'),
                    'fg': colors.get('text_color', '#333333'),
                    'insertbackground': colors.get('text_color', '#333333'),
                    'selectbackground': colors.get('accent_color', '#0066cc'),
                    'selectforeground': colors.get('bg_color', '#ffffff')
                })
            elif widget_type == "text":
                base_config.update({
                    'bg': colors.get('bg_color', '#ffffff'),
                    'fg': colors.get('text_color', '#333333'),
                    'insertbackground': colors.get('text_color', '#333333'),
                    'selectbackground': colors.get('accent_color', '#0066cc'),
                    'selectforeground': colors.get('bg_color', '#ffffff')
                })
            elif widget_type == "label":
                base_config.update({
                    'fg': colors.get('text_color', '#333333')
                })
            elif widget_type == "frame":
                base_config.update({
                    'relief': 'flat',
                    'borderwidth': 0
                })
            elif widget_type == "listbox":
                base_config.update({
                    'bg': colors.get('bg_color', '#ffffff'),
                    'fg': colors.get('text_color', '#333333'),
                    'selectbackground': colors.get('accent_color', '#0066cc'),
                    'selectforeground': colors.get('bg_color', '#ffffff')
                })
            elif widget_type == "menu":
                base_config.update({
                    'bg': colors.get('button_color', '#e0e0e0'),
                    'fg': colors.get('text_color', '#333333'),
                    'activebackground': colors.get('accent_color', '#0066cc'),
                    'activeforeground': colors.get('bg_color', '#ffffff')
                })
            elif widget_type == "status":
                base_config.update({
                    'bg': colors.get('button_color', '#e0e0e0'),
                    'fg': colors.get('text_color', '#333333'),
                    'relief': 'sunken',
                    'borderwidth': 1
                })
            elif widget_type == "error":
                base_config.update({
                    'fg': colors.get('error_color', '#cc0000')
                })
            elif widget_type == "success":
                base_config.update({
                    'fg': colors.get('success_color', '#00cc00')
                })
            elif widget_type == "warning":
                base_config.update({
                    'fg': colors.get('warning_color', '#ff9900')
                })
            
            # Apply configuration to widget
            widget.configure(**base_config)
            
        except Exception as e:
            self.logger.error(f"Error applying theme to widget: {e}")
    
    def apply_theme_to_all_widgets(self):
        """Apply current theme to all registered widgets"""
        for widget, widget_type in self.themed_widgets:
            try:
                if widget.winfo_exists():  # Check if widget still exists
                    self.apply_theme_to_widget(widget, widget_type)
            except tk.TclError:
                # Widget has been destroyed, remove from list
                self.themed_widgets.remove((widget, widget_type))
    
    def change_theme(self, theme_name: str):
        """Change the current theme
        
        Args:
            theme_name: Name of theme to switch to
        """
        try:
            self.resource_manager.set_theme(theme_name)
            self.apply_theme_to_all_widgets()
            
            # Call theme change callbacks
            for callback in self.theme_change_callbacks:
                try:
                    callback(theme_name)
                except Exception as e:
                    self.logger.error(f"Error in theme change callback: {e}")
            
            self.logger.info(f"Theme changed to: {theme_name}")
            
        except Exception as e:
            self.logger.error(f"Error changing theme: {e}")
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        theme_settings = self.resource_manager.gui_config.get("theme_settings", {})
        return theme_settings.get("available_themes", ["default"])
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.resource_manager.current_theme
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Get colors for specified theme"""
        return self.resource_manager.get_theme_colors(theme_name)
    
    def create_themed_button(self, parent: tk.Widget, text: str, command: Callable = None, **kwargs) -> tk.Button:
        """Create a themed button
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            **kwargs: Additional button options
            
        Returns:
            Themed button widget
        """
        button = tk.Button(parent, text=text, command=command, **kwargs)
        self.register_widget(button, "button")
        return button
    
    def create_themed_label(self, parent: tk.Widget, text: str, **kwargs) -> tk.Label:
        """Create a themed label
        
        Args:
            parent: Parent widget
            text: Label text
            **kwargs: Additional label options
            
        Returns:
            Themed label widget
        """
        label = tk.Label(parent, text=text, **kwargs)
        self.register_widget(label, "label")
        return label
    
    def create_themed_entry(self, parent: tk.Widget, **kwargs) -> tk.Entry:
        """Create a themed entry
        
        Args:
            parent: Parent widget
            **kwargs: Additional entry options
            
        Returns:
            Themed entry widget
        """
        entry = tk.Entry(parent, **kwargs)
        self.register_widget(entry, "entry")
        return entry
    
    def create_themed_text(self, parent: tk.Widget, **kwargs) -> tk.Text:
        """Create a themed text widget
        
        Args:
            parent: Parent widget
            **kwargs: Additional text options
            
        Returns:
            Themed text widget
        """
        text = tk.Text(parent, **kwargs)
        self.register_widget(text, "text")
        return text
    
    def create_themed_frame(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        """Create a themed frame
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame options
            
        Returns:
            Themed frame widget
        """
        frame = tk.Frame(parent, **kwargs)
        self.register_widget(frame, "frame")
        return frame
    
    def create_themed_listbox(self, parent: tk.Widget, **kwargs) -> tk.Listbox:
        """Create a themed listbox
        
        Args:
            parent: Parent widget
            **kwargs: Additional listbox options
            
        Returns:
            Themed listbox widget
        """
        listbox = tk.Listbox(parent, **kwargs)
        self.register_widget(listbox, "listbox")
        return listbox
    
    def create_status_label(self, parent: tk.Widget, text: str, status_type: str = "default", **kwargs) -> tk.Label:
        """Create a status label with appropriate coloring
        
        Args:
            parent: Parent widget
            text: Label text
            status_type: Type of status ('error', 'success', 'warning', 'default')
            **kwargs: Additional label options
            
        Returns:
            Themed status label
        """
        label = tk.Label(parent, text=text, **kwargs)
        widget_type = status_type if status_type in ["error", "success", "warning"] else "label"
        self.register_widget(label, widget_type)
        return label
    
    def update_status_label(self, label: tk.Label, text: str, status_type: str = "default"):
        """Update a status label with new text and status type
        
        Args:
            label: Label widget to update
            text: New text
            status_type: New status type
        """
        label.configure(text=text)
        widget_type = status_type if status_type in ["error", "success", "warning"] else "label"
        self.apply_theme_to_widget(label, widget_type)

# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

if __name__ == "__main__":
    # Test the theme manager
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Theme Manager Test")
    root.geometry("400x300")
    
    tm = get_theme_manager()
    
    # Create test widgets
    frame = tm.create_themed_frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    label = tm.create_themed_label(frame, "Theme Manager Test")
    label.pack(pady=5)
    
    button1 = tm.create_themed_button(frame, "Default Theme", 
                                     command=lambda: tm.change_theme("default"))
    button1.pack(pady=2)
    
    button2 = tm.create_themed_button(frame, "Dark Theme", 
                                     command=lambda: tm.change_theme("dark"))
    button2.pack(pady=2)
    
    button3 = tm.create_themed_button(frame, "POSCO Corporate Theme", 
                                     command=lambda: tm.change_theme("posco_corporate"))
    button3.pack(pady=2)
    
    # Status labels
    success_label = tm.create_status_label(frame, "Success Status", "success")
    success_label.pack(pady=2)
    
    error_label = tm.create_status_label(frame, "Error Status", "error")
    error_label.pack(pady=2)
    
    warning_label = tm.create_status_label(frame, "Warning Status", "warning")
    warning_label.pack(pady=2)
    
    root.mainloop()