#!/usr/bin/env python3
"""
Settings Dialog for POSCO News System GUI
Provides GUI for customizing themes, languages, and system settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, Optional
import logging
from .resource_manager import get_resource_manager
from .theme_manager import get_theme_manager
from .i18n_manager import get_i18n_manager

class SettingsDialog:
    """Settings dialog for GUI customization"""
    
    def __init__(self, parent: tk.Widget, on_settings_changed: Callable = None):
        """Initialize settings dialog
        
        Args:
            parent: Parent widget
            on_settings_changed: Callback when settings are changed
        """
        self.parent = parent
        self.on_settings_changed = on_settings_changed
        self.resource_manager = get_resource_manager()
        self.theme_manager = get_theme_manager()
        self.i18n_manager = get_i18n_manager()
        self.logger = logging.getLogger(__name__)
        
        self.dialog = None
        self.settings_vars = {}
        
    def show(self):
        """Show the settings dialog"""
        if self.dialog is not None:
            self.dialog.lift()
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.i18n_manager.get_string("settings.title", fallback="Settings"))
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
        self.load_current_settings()
        
        # Center dialog on parent
        self.center_dialog()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_appearance_tab(notebook)
        self.create_language_tab(notebook)
        self.create_system_tab(notebook)
        self.create_advanced_tab(notebook)
        
        # Create button frame
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Buttons
        tk.Button(button_frame, text=self.i18n_manager.get_string("buttons.ok", fallback="OK"),
                 command=self.on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text=self.i18n_manager.get_string("buttons.cancel", fallback="Cancel"),
                 command=self.on_cancel).pack(side=tk.RIGHT)
        tk.Button(button_frame, text=self.i18n_manager.get_string("buttons.apply", fallback="Apply"),
                 command=self.on_apply).pack(side=tk.RIGHT, padx=(0, 5))
        tk.Button(button_frame, text=self.i18n_manager.get_string("settings.reset", fallback="Reset to Defaults"),
                 command=self.on_reset).pack(side=tk.LEFT)
    
    def create_appearance_tab(self, notebook: ttk.Notebook):
        """Create appearance settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=self.i18n_manager.get_string("settings.appearance", fallback="Appearance"))
        
        # Theme selection
        theme_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.theme", fallback="Theme"))
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['theme'] = tk.StringVar()
        available_themes = self.theme_manager.get_available_themes()
        
        for i, theme in enumerate(available_themes):
            rb = tk.Radiobutton(theme_frame, text=theme.replace('_', ' ').title(),
                               variable=self.settings_vars['theme'], value=theme,
                               command=self.on_theme_preview)
            rb.pack(anchor=tk.W, padx=10, pady=2)
        
        # Font settings
        font_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.font", fallback="Font"))
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Font family
        tk.Label(font_frame, text=self.i18n_manager.get_string("settings.font_family", fallback="Font Family:")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['font_family'] = tk.StringVar()
        font_families = ["맑은 고딕", "Arial", "Helvetica", "Times New Roman", "Courier New"]
        font_combo = ttk.Combobox(font_frame, textvariable=self.settings_vars['font_family'],
                                 values=font_families, state="readonly")
        font_combo.pack(fill=tk.X, padx=10, pady=2)
        
        # Font size
        tk.Label(font_frame, text=self.i18n_manager.get_string("settings.font_size", fallback="Font Size:")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['font_size'] = tk.IntVar()
        font_size_spin = tk.Spinbox(font_frame, from_=8, to=20, textvariable=self.settings_vars['font_size'])
        font_size_spin.pack(fill=tk.X, padx=10, pady=2)
        
        # Window settings
        window_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.window", fallback="Window"))
        window_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Window size
        size_frame = tk.Frame(window_frame)
        size_frame.pack(fill=tk.X, padx=10, pady=2)
        
        tk.Label(size_frame, text=self.i18n_manager.get_string("settings.width", fallback="Width:")).pack(side=tk.LEFT)
        self.settings_vars['window_width'] = tk.IntVar()
        tk.Spinbox(size_frame, from_=800, to=2000, width=10, textvariable=self.settings_vars['window_width']).pack(side=tk.LEFT, padx=(5, 10))
        
        tk.Label(size_frame, text=self.i18n_manager.get_string("settings.height", fallback="Height:")).pack(side=tk.LEFT)
        self.settings_vars['window_height'] = tk.IntVar()
        tk.Spinbox(size_frame, from_=600, to=1500, width=10, textvariable=self.settings_vars['window_height']).pack(side=tk.LEFT, padx=5)
        
        # UI options
        self.settings_vars['enable_animations'] = tk.BooleanVar()
        tk.Checkbutton(window_frame, text=self.i18n_manager.get_string("settings.animations", fallback="Enable Animations"),
                      variable=self.settings_vars['enable_animations']).pack(anchor=tk.W, padx=10, pady=2)
        
        self.settings_vars['show_tooltips'] = tk.BooleanVar()
        tk.Checkbutton(window_frame, text=self.i18n_manager.get_string("settings.tooltips", fallback="Show Tooltips"),
                      variable=self.settings_vars['show_tooltips']).pack(anchor=tk.W, padx=10, pady=2)
    
    def create_language_tab(self, notebook: ttk.Notebook):
        """Create language settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=self.i18n_manager.get_string("settings.language", fallback="Language"))
        
        # Language selection
        lang_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.interface_language", fallback="Interface Language"))
        lang_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['language'] = tk.StringVar()
        available_languages = self.i18n_manager.get_available_languages()
        
        for lang_code in available_languages:
            lang_name = self.i18n_manager.get_language_name(lang_code)
            rb = tk.Radiobutton(lang_frame, text=f"{lang_name} ({lang_code})",
                               variable=self.settings_vars['language'], value=lang_code,
                               command=self.on_language_preview)
            rb.pack(anchor=tk.W, padx=10, pady=2)
        
        # Regional settings
        regional_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.regional", fallback="Regional Settings"))
        regional_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date format
        tk.Label(regional_frame, text=self.i18n_manager.get_string("settings.date_format", fallback="Date Format:")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['date_format'] = tk.StringVar()
        date_formats = ["%Y-%m-%d %H:%M:%S", "%Y년 %m월 %d일 %H:%M:%S", "%d/%m/%Y %H:%M:%S"]
        date_combo = ttk.Combobox(regional_frame, textvariable=self.settings_vars['date_format'],
                                 values=date_formats)
        date_combo.pack(fill=tk.X, padx=10, pady=2)
        
        # Number format
        tk.Label(regional_frame, text=self.i18n_manager.get_string("settings.number_format", fallback="Number Format:")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['number_format'] = tk.StringVar()
        number_formats = ["comma_separated", "space_separated", "period_separated"]
        number_combo = ttk.Combobox(regional_frame, textvariable=self.settings_vars['number_format'],
                                   values=number_formats, state="readonly")
        number_combo.pack(fill=tk.X, padx=10, pady=2)
    
    def create_system_tab(self, notebook: ttk.Notebook):
        """Create system settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=self.i18n_manager.get_string("settings.system", fallback="System"))
        
        # Monitoring settings
        monitor_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.monitoring", fallback="Monitoring"))
        monitor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Auto refresh interval
        tk.Label(monitor_frame, text=self.i18n_manager.get_string("settings.refresh_interval", fallback="Auto Refresh Interval (seconds):")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['auto_refresh_interval'] = tk.IntVar()
        tk.Spinbox(monitor_frame, from_=5, to=300, textvariable=self.settings_vars['auto_refresh_interval']).pack(fill=tk.X, padx=10, pady=2)
        
        # Log settings
        self.settings_vars['log_max_lines'] = tk.IntVar()
        tk.Label(monitor_frame, text=self.i18n_manager.get_string("settings.log_max_lines", fallback="Maximum Log Lines:")).pack(anchor=tk.W, padx=10, pady=2)
        tk.Spinbox(monitor_frame, from_=100, to=10000, textvariable=self.settings_vars['log_max_lines']).pack(fill=tk.X, padx=10, pady=2)
        
        # Deployment settings
        deploy_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.deployment", fallback="Deployment"))
        deploy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['auto_deploy'] = tk.BooleanVar()
        tk.Checkbutton(deploy_frame, text=self.i18n_manager.get_string("settings.auto_deploy", fallback="Enable Auto Deploy"),
                      variable=self.settings_vars['auto_deploy']).pack(anchor=tk.W, padx=10, pady=2)
        
        # Deploy timeout
        tk.Label(deploy_frame, text=self.i18n_manager.get_string("settings.deploy_timeout", fallback="Deploy Timeout (seconds):")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['deploy_timeout'] = tk.IntVar()
        tk.Spinbox(deploy_frame, from_=60, to=600, textvariable=self.settings_vars['deploy_timeout']).pack(fill=tk.X, padx=10, pady=2)
    
    def create_advanced_tab(self, notebook: ttk.Notebook):
        """Create advanced settings tab"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=self.i18n_manager.get_string("settings.advanced", fallback="Advanced"))
        
        # Git settings
        git_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.git", fallback="Git Settings"))
        git_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_vars['auto_stash'] = tk.BooleanVar()
        tk.Checkbutton(git_frame, text=self.i18n_manager.get_string("settings.auto_stash", fallback="Auto Stash Changes"),
                      variable=self.settings_vars['auto_stash']).pack(anchor=tk.W, padx=10, pady=2)
        
        # Max retries
        tk.Label(git_frame, text=self.i18n_manager.get_string("settings.max_retries", fallback="Max Retries:")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['max_retries'] = tk.IntVar()
        tk.Spinbox(git_frame, from_=1, to=10, textvariable=self.settings_vars['max_retries']).pack(fill=tk.X, padx=10, pady=2)
        
        # Webhook settings
        webhook_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.webhook", fallback="Webhook Settings"))
        webhook_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Webhook URL
        tk.Label(webhook_frame, text=self.i18n_manager.get_string("settings.webhook_url", fallback="Webhook URL:")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['webhook_url'] = tk.StringVar()
        tk.Entry(webhook_frame, textvariable=self.settings_vars['webhook_url']).pack(fill=tk.X, padx=10, pady=2)
        
        # Webhook timeout
        tk.Label(webhook_frame, text=self.i18n_manager.get_string("settings.webhook_timeout", fallback="Webhook Timeout (seconds):")).pack(anchor=tk.W, padx=10, pady=2)
        self.settings_vars['webhook_timeout'] = tk.IntVar()
        tk.Spinbox(webhook_frame, from_=5, to=60, textvariable=self.settings_vars['webhook_timeout']).pack(fill=tk.X, padx=10, pady=2)
        
        # Export/Import settings
        io_frame = tk.LabelFrame(frame, text=self.i18n_manager.get_string("settings.import_export", fallback="Import/Export"))
        io_frame.pack(fill=tk.X, padx=10, pady=5)
        
        button_frame = tk.Frame(io_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text=self.i18n_manager.get_string("settings.export", fallback="Export Settings"),
                 command=self.export_settings).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text=self.i18n_manager.get_string("settings.import", fallback="Import Settings"),
                 command=self.import_settings).pack(side=tk.LEFT)
    
    def load_current_settings(self):
        """Load current settings into dialog"""
        try:
            # GUI settings
            gui_settings = self.resource_manager.gui_config.get("gui_settings", {})
            self.settings_vars['theme'].set(gui_settings.get("theme", "default"))
            self.settings_vars['font_family'].set(gui_settings.get("font_family", "맑은 고딕"))
            self.settings_vars['font_size'].set(gui_settings.get("font_size", 10))
            
            window_size = gui_settings.get("window_size", {"width": 1200, "height": 800})
            self.settings_vars['window_width'].set(window_size.get("width", 1200))
            self.settings_vars['window_height'].set(window_size.get("height", 800))
            
            self.settings_vars['auto_refresh_interval'].set(gui_settings.get("auto_refresh_interval", 30))
            self.settings_vars['log_max_lines'].set(gui_settings.get("log_max_lines", 1000))
            self.settings_vars['enable_animations'].set(gui_settings.get("enable_animations", True))
            self.settings_vars['show_tooltips'].set(gui_settings.get("show_tooltips", True))
            
            # Language settings
            i18n_settings = self.resource_manager.gui_config.get("internationalization", {})
            self.settings_vars['language'].set(i18n_settings.get("default_language", "ko"))
            
            date_formats = i18n_settings.get("date_format", {})
            current_lang = self.settings_vars['language'].get()
            self.settings_vars['date_format'].set(date_formats.get(current_lang, "%Y-%m-%d %H:%M:%S"))
            
            number_formats = i18n_settings.get("number_format", {})
            self.settings_vars['number_format'].set(number_formats.get(current_lang, "comma_separated"))
            
            # Deployment settings
            deploy_settings = self.resource_manager.gui_config.get("deployment_settings", {})
            self.settings_vars['auto_deploy'].set(deploy_settings.get("auto_deploy", False))
            self.settings_vars['deploy_timeout'].set(deploy_settings.get("deploy_timeout", 300))
            
            # Git settings
            git_settings = self.resource_manager.gui_config.get("git_settings", {})
            self.settings_vars['auto_stash'].set(git_settings.get("auto_stash", True))
            self.settings_vars['max_retries'].set(git_settings.get("max_retries", 3))
            
            # Webhook settings
            webhook_settings = self.resource_manager.webhook_config.get("webhook_settings", {})
            self.settings_vars['webhook_url'].set(self.resource_manager.webhook_config.get("webhook_url", ""))
            self.settings_vars['webhook_timeout'].set(webhook_settings.get("timeout", 15))
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to configuration files"""
        try:
            # Update GUI settings
            gui_settings = self.resource_manager.gui_config.setdefault("gui_settings", {})
            gui_settings["theme"] = self.settings_vars['theme'].get()
            gui_settings["font_family"] = self.settings_vars['font_family'].get()
            gui_settings["font_size"] = self.settings_vars['font_size'].get()
            gui_settings["window_size"] = {
                "width": self.settings_vars['window_width'].get(),
                "height": self.settings_vars['window_height'].get()
            }
            gui_settings["auto_refresh_interval"] = self.settings_vars['auto_refresh_interval'].get()
            gui_settings["log_max_lines"] = self.settings_vars['log_max_lines'].get()
            gui_settings["enable_animations"] = self.settings_vars['enable_animations'].get()
            gui_settings["show_tooltips"] = self.settings_vars['show_tooltips'].get()
            
            # Update language settings
            i18n_settings = self.resource_manager.gui_config.setdefault("internationalization", {})
            new_language = self.settings_vars['language'].get()
            i18n_settings["default_language"] = new_language
            
            # Update date and number formats
            date_formats = i18n_settings.setdefault("date_format", {})
            date_formats[new_language] = self.settings_vars['date_format'].get()
            
            number_formats = i18n_settings.setdefault("number_format", {})
            number_formats[new_language] = self.settings_vars['number_format'].get()
            
            # Update deployment settings
            deploy_settings = self.resource_manager.gui_config.setdefault("deployment_settings", {})
            deploy_settings["auto_deploy"] = self.settings_vars['auto_deploy'].get()
            deploy_settings["deploy_timeout"] = self.settings_vars['deploy_timeout'].get()
            
            # Update git settings
            git_settings = self.resource_manager.gui_config.setdefault("git_settings", {})
            git_settings["auto_stash"] = self.settings_vars['auto_stash'].get()
            git_settings["max_retries"] = self.settings_vars['max_retries'].get()
            
            # Update webhook settings
            self.resource_manager.webhook_config["webhook_url"] = self.settings_vars['webhook_url'].get()
            webhook_settings = self.resource_manager.webhook_config.setdefault("webhook_settings", {})
            webhook_settings["timeout"] = self.settings_vars['webhook_timeout'].get()
            
            # Save all configurations
            self.resource_manager.save_gui_config()
            self.resource_manager.save_webhook_config()
            
            # Apply theme and language changes
            self.theme_manager.change_theme(self.settings_vars['theme'].get())
            self.i18n_manager.change_language(new_language)
            
            self.logger.info("Settings saved successfully")
            
            # Notify parent of changes
            if self.on_settings_changed:
                self.on_settings_changed()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def on_theme_preview(self):
        """Preview theme change"""
        theme_name = self.settings_vars['theme'].get()
        self.theme_manager.change_theme(theme_name)
    
    def on_language_preview(self):
        """Preview language change"""
        language = self.settings_vars['language'].get()
        self.i18n_manager.change_language(language)
    
    def on_ok(self):
        """Handle OK button"""
        self.save_settings()
        self.on_close()
    
    def on_cancel(self):
        """Handle Cancel button"""
        # Restore original settings
        self.resource_manager.load_all_configs()
        self.theme_manager.change_theme(self.resource_manager.current_theme)
        self.i18n_manager.change_language(self.resource_manager.current_language)
        self.on_close()
    
    def on_apply(self):
        """Handle Apply button"""
        self.save_settings()
    
    def on_reset(self):
        """Handle Reset button"""
        if messagebox.askyesno("Confirm Reset", 
                              self.i18n_manager.get_string("settings.confirm_reset", 
                                                          fallback="Reset all settings to defaults?")):
            self.resource_manager._create_default_configs()
            self.load_current_settings()
            messagebox.showinfo("Reset Complete", 
                               self.i18n_manager.get_string("settings.reset_complete",
                                                           fallback="Settings have been reset to defaults."))
    
    def export_settings(self):
        """Export settings to file"""
        try:
            filename = filedialog.asksaveasfilename(
                title=self.i18n_manager.get_string("settings.export_title", fallback="Export Settings"),
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                import json
                settings_data = {
                    "gui_config": self.resource_manager.gui_config,
                    "webhook_config": self.resource_manager.webhook_config,
                    "posco_config": self.resource_manager.posco_config
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Export Complete", 
                                   self.i18n_manager.get_string("settings.export_complete",
                                                               fallback="Settings exported successfully."))
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export settings: {e}")
    
    def import_settings(self):
        """Import settings from file"""
        try:
            filename = filedialog.askopenfilename(
                title=self.i18n_manager.get_string("settings.import_title", fallback="Import Settings"),
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # Update configurations
                if "gui_config" in settings_data:
                    self.resource_manager.gui_config.update(settings_data["gui_config"])
                if "webhook_config" in settings_data:
                    self.resource_manager.webhook_config.update(settings_data["webhook_config"])
                if "posco_config" in settings_data:
                    self.resource_manager.posco_config.update(settings_data["posco_config"])
                
                # Save and reload
                self.resource_manager.save_gui_config()
                self.resource_manager.save_webhook_config()
                self.resource_manager.save_posco_config()
                self.load_current_settings()
                
                messagebox.showinfo("Import Complete", 
                                   self.i18n_manager.get_string("settings.import_complete",
                                                               fallback="Settings imported successfully."))
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import settings: {e}")
    
    def on_close(self):
        """Handle dialog close"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None

if __name__ == "__main__":
    # Test the settings dialog
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("300x200")
    
    def show_settings():
        dialog = SettingsDialog(root)
        dialog.show()
    
    tk.Button(root, text="Open Settings", command=show_settings).pack(pady=50)
    
    root.mainloop()