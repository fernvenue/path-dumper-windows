#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
import json
import locale
import os
import shutil
import threading
import tkinter as tk

class Localizer:
    def __init__(self, locale=None):
        if locale is None:
            locale = self.detect_system_locale()
        self.locale = locale
        self.translations = {}
        self.load_translations()
    
    def detect_system_locale(self):
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                if system_locale.startswith('zh_CN') or system_locale.startswith('zh_Hans'):
                    return 'zh_Hans'
                elif system_locale.startswith('zh_TW') or system_locale.startswith('zh_Hant'):
                    return 'zh_Hant'
                elif system_locale.startswith('en'):
                    return 'en'
            return 'en'
        except:
            return 'en'
    
    def load_translations(self):
        try:
            locale_file = Path(__file__).parent / 'locales' / f'{self.locale}.json'
            if locale_file.exists():
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
        except Exception as e:
            print(f"Failed to load locale {self.locale}: {e}")
            if self.locale != 'en':
                self.locale = 'en'
                self.load_translations()
    
    def get(self, key, default=None):
        return self.translations.get(key, default or key)


class PathDumper:
    def __init__(self):
        self.localizer = Localizer()
        self.setup_presets()
        self.setup_gui()
        self.is_processing = False
    
    def setup_presets(self):
        self.replace_presets = {
            'preset_video': 'mp4,mkv,avi,mov,wmv,flv,webm,m4v,3gp,ts,vob,rmvb',
            'preset_audio': 'mp3,flac,wav,aac,ogg,wma,m4a,ape,dts,ac3',
            'preset_image': 'jpg,jpeg,png,gif,bmp,tiff,svg,webp,raw,cr2,nef',
            'preset_archive': 'zip,rar,7z,tar,gz,bz2,xz,iso,dmg,img',
            'preset_executable': 'exe,msi,deb,rpm,pkg,app,dmg,bin,run'
        }
        
        self.keep_presets = {
            'preset_document': 'txt,doc,docx,pdf,rtf,odt,pages,md,rst',
            'preset_config': 'json,xml,yaml,yml,ini,cfg,conf,toml,properties',
            'preset_code': 'py,js,html,css,cpp,c,h,java,php,rb,go,rs',
            'preset_subtitle': 'srt,ass,ssa,vtt,sub,sbv,lrc,idx,sup',
            'preset_database': 'db,sqlite,sqlite3,sql,mdb,accdb,dbf'
        }
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(self.localizer.get('app_title', 'Path Dumper'))
        self.root.geometry('720x800')
        self.root.resizable(True, True)
        self.root.minsize(600, 700)
        
        container = ttk.Frame(self.root)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(1, weight=1)
        
        self.source_label = ttk.Label(main_frame, text=self.localizer.get('source_dir'))
        self.source_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.source_var = tk.StringVar()
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var, width=50)
        self.source_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_source_btn = ttk.Button(source_frame, text=self.localizer.get('browse'), 
                  command=self.browse_source)
        self.browse_source_btn.grid(row=0, column=1)
        
        self.output_label = ttk.Label(main_frame, text=self.localizer.get('output_dir'))
        self.output_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.output_var = tk.StringVar()
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=50)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_output_btn = ttk.Button(output_frame, text=self.localizer.get('browse'), 
                  command=self.browse_output)
        self.browse_output_btn.grid(row=0, column=1)
        
        self.size_label = ttk.Label(main_frame, text=self.localizer.get('size_threshold'))
        self.size_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.size_var = tk.StringVar(value="30")
        size_spinbox = ttk.Spinbox(size_frame, from_=1, to=1000, width=10, 
                                  textvariable=self.size_var)
        size_spinbox.grid(row=0, column=0, padx=(0, 5))
        ttk.Label(size_frame, text="MB").grid(row=0, column=1)
        
        self.exclude_label = ttk.Label(main_frame, text=self.localizer.get('exclude_dirs'))
        self.exclude_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        self.exclude_frame = ttk.LabelFrame(main_frame, padding="5")
        self.exclude_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.exclude_frame.columnconfigure(1, weight=1)
        
        self.exclude_manual_label = ttk.Label(self.exclude_frame, text=self.localizer.get('exclude_dirs_manual'))
        self.exclude_manual_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.exclude_var = tk.StringVar()
        self.exclude_entry = ttk.Entry(self.exclude_frame, textvariable=self.exclude_var, width=50)
        self.exclude_entry.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        button_frame = ttk.Frame(self.exclude_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.add_exclude_btn = ttk.Button(button_frame, text=self.localizer.get('add_exclude_dir'), 
                                         command=self.add_exclude_directory)
        self.add_exclude_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.remove_exclude_btn = ttk.Button(button_frame, text=self.localizer.get('remove_exclude_dir'), 
                                            command=self.remove_exclude_directory)
        self.remove_exclude_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_exclude_btn = ttk.Button(button_frame, text=self.localizer.get('clear_exclude_dirs'), 
                                           command=self.clear_exclude_directories)
        self.clear_exclude_btn.pack(side=tk.LEFT)
        
        self.exclude_selected_label = ttk.Label(self.exclude_frame, text=self.localizer.get('exclude_dirs_selected'))
        self.exclude_selected_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 2))
        
        list_frame = ttk.Frame(self.exclude_frame)
        list_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.exclude_listbox = tk.Listbox(list_frame, height=4, selectmode=tk.EXTENDED)
        self.exclude_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        exclude_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.exclude_listbox.yview)
        exclude_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.exclude_listbox.configure(yscrollcommand=exclude_scrollbar.set)
        
        self.selected_exclude_dirs = []
        
        self.force_replace_label = ttk.Label(main_frame, text=self.localizer.get('force_replace_exts'))
        self.force_replace_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        replace_preset_frame = ttk.Frame(main_frame)
        replace_preset_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.replace_preset_label = ttk.Label(replace_preset_frame, text=self.localizer.get('preset_replace'))
        self.replace_preset_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.replace_preset_var = tk.StringVar()
        self.replace_preset_combo = ttk.Combobox(replace_preset_frame, textvariable=self.replace_preset_var,
                                               values=self.get_localized_preset_names(self.replace_presets), 
                                               width=15, state='readonly')
        self.replace_preset_combo.grid(row=0, column=1, padx=(0, 5))
        
        self.apply_replace_preset_btn = ttk.Button(replace_preset_frame, text=self.localizer.get('apply_preset'),
                                                 command=self.apply_replace_preset)
        self.apply_replace_preset_btn.grid(row=0, column=2)
        
        self.force_replace_var = tk.StringVar()
        self.force_replace_entry = ttk.Entry(main_frame, textvariable=self.force_replace_var, width=50)
        self.force_replace_entry.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.force_keep_label = ttk.Label(main_frame, text=self.localizer.get('force_keep_exts'))
        self.force_keep_label.grid(row=11, column=0, sticky=tk.W, pady=(0, 5))
        
        keep_preset_frame = ttk.Frame(main_frame)
        keep_preset_frame.grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.keep_preset_label = ttk.Label(keep_preset_frame, text=self.localizer.get('preset_keep'))
        self.keep_preset_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.keep_preset_var = tk.StringVar()
        self.keep_preset_combo = ttk.Combobox(keep_preset_frame, textvariable=self.keep_preset_var,
                                            values=self.get_localized_preset_names(self.keep_presets), 
                                            width=15, state='readonly')
        self.keep_preset_combo.grid(row=0, column=1, padx=(0, 5))
        
        self.apply_keep_preset_btn = ttk.Button(keep_preset_frame, text=self.localizer.get('apply_preset'),
                                              command=self.apply_keep_preset)
        self.apply_keep_preset_btn.grid(row=0, column=2)
        
        self.force_keep_var = tk.StringVar()
        self.force_keep_entry = ttk.Entry(main_frame, textvariable=self.force_keep_var, width=50)
        self.force_keep_entry.grid(row=13, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.language_label = ttk.Label(main_frame, text=self.localizer.get('language'))
        self.language_label.grid(row=14, column=0, sticky=tk.W, pady=(10, 5))
        
        self.language_map = {
            'English': 'en',
            '简体中文': 'zh_Hans', 
            '繁體中文': 'zh_Hant'
        }
        self.reverse_language_map = {v: k for k, v in self.language_map.items()}
        
        current_display = self.reverse_language_map.get(self.localizer.locale, 'English')
        self.language_var = tk.StringVar(value=current_display)
        language_combo = ttk.Combobox(main_frame, textvariable=self.language_var,
                                     values=list(self.language_map.keys()), width=15, state='readonly')
        language_combo.grid(row=15, column=0, sticky=tk.W, pady=(0, 10))
        language_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=16, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_var = tk.StringVar(value=self.localizer.get('ready'))
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=17, column=0, columnspan=2, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=18, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text=self.localizer.get('start_dump'), 
                                      command=self.start_dump)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.about_button = ttk.Button(button_frame, text=self.localizer.get('about'), 
                  command=self.show_about)
        self.about_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.exit_button = ttk.Button(button_frame, text=self.localizer.get('exit'), 
                  command=self.root.quit)
        self.exit_button.pack(side=tk.LEFT)
        
        self.log_frame = ttk.LabelFrame(main_frame, text=self.localizer.get('log'), padding="5")
        self.log_frame.grid(row=19, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(self.log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.log("Path Dumper started - Ready to process directories")
        self.log("Select source directory and output directory to begin")
    
    def get_localized_preset_names(self, presets_dict):
        return [self.localizer.get(key, key) for key in presets_dict.keys()]
    
    def get_preset_key_by_display_name(self, display_name, presets_dict):
        for key in presets_dict.keys():
            if self.localizer.get(key, key) == display_name:
                return key
        return None
    
    def browse_source(self):
        directory = filedialog.askdirectory(
            title=self.localizer.get('select_source_dir'))
        if directory:
            self.source_var.set(directory)
    
    def browse_output(self):
        directory = filedialog.askdirectory(
            title=self.localizer.get('select_output_dir'))
        if directory:
            self.output_var.set(directory)
    
    def add_exclude_directory(self):
        if hasattr(self, 'source_var') and self.source_var.get():
            initial_dir = self.source_var.get()
        else:
            initial_dir = os.path.expanduser("~")
        
        directory = filedialog.askdirectory(
            title=self.localizer.get('select_exclude_dir'),
            initialdir=initial_dir)
        
        if directory:
            source_dir = self.source_var.get()
            if source_dir and directory.startswith(source_dir):
                rel_path = os.path.relpath(directory, source_dir)
                if rel_path not in self.selected_exclude_dirs:
                    self.selected_exclude_dirs.append(rel_path)
                    self.update_exclude_listbox()
            else:
                if directory not in self.selected_exclude_dirs:
                    self.selected_exclude_dirs.append(directory)
                    self.update_exclude_listbox()
    
    def remove_exclude_directory(self):
        selection = self.exclude_listbox.curselection()
        if selection:
            for index in reversed(selection):
                del self.selected_exclude_dirs[index]
            self.update_exclude_listbox()
    
    def clear_exclude_directories(self):
        self.selected_exclude_dirs.clear()
        self.update_exclude_listbox()
    
    def update_exclude_listbox(self):
        self.exclude_listbox.delete(0, tk.END)
        for directory in self.selected_exclude_dirs:
            self.exclude_listbox.insert(tk.END, directory)
    
    def apply_replace_preset(self):
        display_name = self.replace_preset_var.get()
        preset_key = self.get_preset_key_by_display_name(display_name, self.replace_presets)
        
        if preset_key and preset_key in self.replace_presets:
            extensions = self.replace_presets[preset_key]
            current_text = self.force_replace_var.get().strip()
            
            if current_text:
                existing_exts = set(ext.strip().lower() for ext in current_text.split(',') if ext.strip())
                new_exts = set(ext.strip().lower() for ext in extensions.split(',') if ext.strip())
                merged_exts = sorted(existing_exts.union(new_exts))
                self.force_replace_var.set(','.join(merged_exts))
            else:
                self.force_replace_var.set(extensions)
            
            self.log(f"Applied force replace preset: {display_name}")
    
    def apply_keep_preset(self):
        display_name = self.keep_preset_var.get()
        preset_key = self.get_preset_key_by_display_name(display_name, self.keep_presets)
        
        if preset_key and preset_key in self.keep_presets:
            extensions = self.keep_presets[preset_key]
            current_text = self.force_keep_var.get().strip()
            
            if current_text:
                existing_exts = set(ext.strip().lower() for ext in current_text.split(',') if ext.strip())
                new_exts = set(ext.strip().lower() for ext in extensions.split(',') if ext.strip())
                merged_exts = sorted(existing_exts.union(new_exts))
                self.force_keep_var.set(','.join(merged_exts))
            else:
                self.force_keep_var.set(extensions)
            
            self.log(f"Applied force keep preset: {display_name}")
    
    def change_language(self, event=None):
        display_name = self.language_var.get()
        new_locale = self.language_map.get(display_name, 'en')
        self.localizer = Localizer(new_locale)
        self.update_ui_text()
    
    def update_ui_text(self):
        self.root.title(self.localizer.get('app_title', 'Path Dumper'))
        
        self.source_label.config(text=self.localizer.get('source_dir'))
        self.output_label.config(text=self.localizer.get('output_dir'))
        self.size_label.config(text=self.localizer.get('size_threshold'))
        self.exclude_label.config(text=self.localizer.get('exclude_dirs'))
        self.exclude_manual_label.config(text=self.localizer.get('exclude_dirs_manual'))
        self.exclude_selected_label.config(text=self.localizer.get('exclude_dirs_selected'))
        self.force_replace_label.config(text=self.localizer.get('force_replace_exts'))
        self.replace_preset_label.config(text=self.localizer.get('preset_replace'))
        self.force_keep_label.config(text=self.localizer.get('force_keep_exts'))
        self.keep_preset_label.config(text=self.localizer.get('preset_keep'))
        self.language_label.config(text=self.localizer.get('language'))
        
        self.browse_source_btn.config(text=self.localizer.get('browse'))
        self.browse_output_btn.config(text=self.localizer.get('browse'))
        self.add_exclude_btn.config(text=self.localizer.get('add_exclude_dir'))
        self.remove_exclude_btn.config(text=self.localizer.get('remove_exclude_dir'))
        self.clear_exclude_btn.config(text=self.localizer.get('clear_exclude_dirs'))
        self.apply_replace_preset_btn.config(text=self.localizer.get('apply_preset'))
        self.apply_keep_preset_btn.config(text=self.localizer.get('apply_preset'))
        self.start_button.config(text=self.localizer.get('start_dump'))
        self.about_button.config(text=self.localizer.get('about'))
        self.exit_button.config(text=self.localizer.get('exit'))
        
        self.log_frame.config(text=self.localizer.get('log'))
        
        current_status = self.status_var.get()
        if current_status == "Ready" or current_status == "就绪" or current_status == "就緒":
            self.status_var.set(self.localizer.get('ready'))
        
        self.replace_preset_combo['values'] = self.get_localized_preset_names(self.replace_presets)
        self.keep_preset_combo['values'] = self.get_localized_preset_names(self.keep_presets)
    
    def show_about(self):
        about_text = self.localizer.get('about_text', """Path Dumper v1.0

A tool for creating directory structure archives with large file placeholders.

Features:
• Preserves complete directory structure
• Replaces large files with placeholders
• Configurable size threshold (default 30MB)
• Multi-language support
• Creates compressed ZIP archives

Perfect for backing up media library structures like Jellyfin, Plex, etc.

Usage:
1. Select source directory to archive
2. Choose output ZIP file location  
3. Set large file size threshold
4. Click 'Start Dump' to begin

Large files will be replaced with text placeholders containing original size and path information.""")
        
        about_text = about_text.replace('\\n', '\n')
        
        messagebox.showinfo(self.localizer.get('about'), about_text)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            lines = int(self.log_text.index(tk.END).split('.')[0])
            if lines > 1000:
                self.log_text.delete('1.0', '500.0')
        
        try:
            if threading.current_thread() == threading.main_thread():
                update_log()
            else:
                self.root.after(0, update_log)
        except:
            pass
    
    def start_dump(self):
        if self.is_processing:
            return
        
        source_dir = self.source_var.get().strip()
        output_dir = self.output_var.get().strip()
        
        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror(self.localizer.get('error'), 
                               self.localizer.get('invalid_source_dir'))
            return
        
        if not output_dir:
            messagebox.showerror(self.localizer.get('error'), 
                               self.localizer.get('invalid_output_dir'))
            return
        
        try:
            size_threshold = float(self.size_var.get()) * 1024 * 1024
        except ValueError:
            messagebox.showerror(self.localizer.get('error'), 
                               self.localizer.get('invalid_size'))
            return
        
        exclude_dirs = []
        
        exclude_text = self.exclude_var.get().strip()
        if exclude_text:
            manual_dirs = [d.strip() for d in exclude_text.split(',') if d.strip()]
            exclude_dirs.extend(manual_dirs)
        
        exclude_dirs.extend(self.selected_exclude_dirs)
        
        seen = set()
        exclude_dirs = [x for x in exclude_dirs if not (x in seen or seen.add(x))]
        
        force_replace_exts = []
        force_text = self.force_replace_var.get().strip()
        if force_text:
            force_replace_exts = [ext.strip().lower() for ext in force_text.split(',') if ext.strip()]
            force_replace_exts = [ext if ext.startswith('.') else '.' + ext for ext in force_replace_exts]
        
        force_keep_exts = []
        keep_text = self.force_keep_var.get().strip()
        if keep_text:
            force_keep_exts = [ext.strip().lower() for ext in keep_text.split(',') if ext.strip()]
            force_keep_exts = [ext if ext.startswith('.') else '.' + ext for ext in force_keep_exts]
        
        self.is_processing = True
        self.start_button.config(state='disabled')
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.perform_dump, 
                                args=(source_dir, output_dir, size_threshold, exclude_dirs, force_replace_exts, force_keep_exts))
        thread.daemon = True
        thread.start()
    
    def perform_dump(self, source_dir, output_dir, size_threshold, exclude_dirs, force_replace_exts, force_keep_exts):
        try:
            self.log(f"Starting sync process...")
            self.log(f"Source: {source_dir}")
            self.log(f"Output: {output_dir}")
            self.log(f"Size threshold: {size_threshold / (1024*1024):.1f} MB")
            if exclude_dirs:
                self.log(f"Excluded directories: {', '.join(exclude_dirs)}")
            if force_replace_exts:
                self.log(f"Force replace extensions: {', '.join(force_replace_exts)}")
            if force_keep_exts:
                self.log(f"Force keep extensions: {', '.join(force_keep_exts)}")
            
            source_path = Path(source_dir).resolve()
            output_path = Path(output_dir).resolve()
            
            try:
                output_path.relative_to(source_path)
                messagebox.showerror(self.localizer.get('error'), 
                                   self.localizer.get('output_inside_source'))
                return
            except ValueError:
                pass
            
            try:
                source_path.relative_to(output_path)
                messagebox.showerror(self.localizer.get('error'), 
                                   self.localizer.get('source_inside_output'))
                return
            except ValueError:
                pass
            
            if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
                messagebox.showerror(self.localizer.get('error'), 
                                   self.localizer.get('invalid_source_dir'))
                return
            
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                test_files = list(os.listdir(source_dir))[:5]
                self.log(f"Directory access test passed, found {len(test_files)} test items")
            except PermissionError:
                messagebox.showerror(self.localizer.get('error'), 
                                   self.localizer.get('permission_denied'))
                return
            
            self.status_var.set(self.localizer.get('scanning_files'))
            self.log(self.localizer.get('start_scanning'))
            
            all_files = []
            skipped_files = []
            excluded_count = 0
            processed_dirs = 0
            
            for root, dirs, files in os.walk(source_dir):
                rel_root = os.path.relpath(root, source_dir)
                should_exclude = False
                
                for exclude_dir in exclude_dirs:
                    exclude_dir = exclude_dir.replace('\\', os.sep).replace('/', os.sep)
                    rel_root_normalized = rel_root.replace('\\', os.sep).replace('/', os.sep)
                    
                    if (rel_root_normalized == exclude_dir or
                        rel_root_normalized.startswith(exclude_dir + os.sep) or
                        exclude_dir.startswith(rel_root_normalized + os.sep) or
                        (os.sep + exclude_dir + os.sep) in (os.sep + rel_root_normalized + os.sep) or
                        exclude_dir in os.path.basename(root)):
                        should_exclude = True
                        break
                
                if should_exclude:
                    dirs.clear()
                    excluded_count += len(files)
                    continue
                
                dirs_to_remove = []
                for d in dirs:
                    for exclude_dir in exclude_dirs:
                        exclude_dir = exclude_dir.replace('\\', os.sep).replace('/', os.sep)
                        if (d == exclude_dir or 
                            exclude_dir == os.path.join(rel_root, d) or
                            exclude_dir in d):
                            dirs_to_remove.append(d)
                            break
                
                for d in dirs_to_remove:
                    if d in dirs:
                        dirs.remove(d)
                
                processed_dirs += 1
                if processed_dirs % 10 == 0:
                    self.log(f"Scanning... processed {processed_dirs} directories, found {len(all_files)} files")
                
                try:
                    root_str = str(root)
                    for file in files:
                        try:
                            file_path = os.path.join(root_str, file)
                            if os.path.exists(file_path) and os.path.isfile(file_path):
                                all_files.append(file_path)
                            else:
                                skipped_files.append(file_path)
                        except (UnicodeDecodeError, OSError) as e:
                            skipped_files.append(f"{root}/{file} (encoding error)")
                            continue
                except Exception as e:
                    self.log(f"Error accessing directory {root}: {e}")
                    continue
            
            total_files = len(all_files)
            if skipped_files:
                self.log(f"Skipped {len(skipped_files)} inaccessible files")
            if excluded_count > 0:
                self.log(f"{self.localizer.get('excluded_dirs')}: {excluded_count} files")
            
            self.log(f"{self.localizer.get('found_files')}: {total_files}")
            
            if total_files > 10000:
                warning_msg = (
                    f"Large library detected: {total_files} files\n\n"
                    "Processing may take 30+ minutes.\n"
                    "The tool will show progress updates.\n"
                    "Please be patient and don't close the window."
                )
                self.log(f"PERFORMANCE WARNING: {warning_msg}")
            elif total_files > 5000:
                self.log(f"Large library notice: {total_files} files - may take 10-30 minutes")
            
            self.status_var.set(self.localizer.get('creating_dump'))
            
            processed = 0
            large_files_count = 0
            force_replaced_count = 0
            force_kept_count = 0
            error_files = []
            last_log_time = 0
            log_interval = 1.0
            
            for file_path in all_files:
                try:
                    try:
                        rel_path = os.path.relpath(file_path, source_dir)
                    except ValueError:
                        rel_path = file_path.replace(source_dir, '').lstrip(os.sep)
                    
                    dest_path = os.path.join(output_dir, rel_path)
                    
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file_path)[1].lower()
                    except (OSError, IOError) as e:
                        with open(dest_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Error accessing file\n")
                            f.write(f"# Original path: {file_path}\n")
                            f.write(f"# Error: {e}\n")
                        processed += 1
                        continue
                    
                    force_keep = file_ext in force_keep_exts
                    
                    force_replace = file_ext in force_replace_exts
                    
                    if force_keep:
                        try:
                            shutil.copy2(file_path, dest_path)
                            force_kept_count += 1
                            
                            current_time = datetime.now().timestamp()
                            if current_time - last_log_time > log_interval:
                                self.log(f"{self.localizer.get('force_kept_file')}: {rel_path}")
                                last_log_time = current_time
                        except (OSError, IOError, PermissionError) as e:
                            with open(dest_path, 'w', encoding='utf-8') as f:
                                f.write(f"# Copy failed for force-keep file\n")
                                f.write(f"# Original size: {file_size} bytes\n")
                                f.write(f"# Original path: {file_path}\n")
                                f.write(f"# Error: {e}\n")
                            error_files.append(file_path)
                    elif force_replace or file_size > size_threshold:
                        with open(dest_path, 'w', encoding='utf-8') as f:
                            if force_replace:
                                f.write(f"# Placeholder for force-replaced file\n")
                                f.write(f"# Extension: {file_ext}\n")
                            else:
                                f.write(f"# Placeholder for large file\n")
                            f.write(f"# Original size: {file_size} bytes\n")
                            f.write(f"# Original path: {file_path}\n")
                        
                        if force_replace:
                            force_replaced_count += 1
                        else:
                            large_files_count += 1
                        
                        current_time = datetime.now().timestamp()
                        if current_time - last_log_time > log_interval:
                            if force_replace:
                                self.log(f"{self.localizer.get('force_replaced_file')}: {rel_path}")
                            else:
                                self.log(f"{self.localizer.get('replaced_large_file')}: {rel_path} ({file_size} bytes)")
                            last_log_time = current_time
                    else:
                        try:
                            shutil.copy2(file_path, dest_path)
                        except (OSError, IOError, PermissionError) as e:
                            with open(dest_path, 'w', encoding='utf-8') as f:
                                f.write(f"# Copy failed for file\n")
                                f.write(f"# Original size: {file_size} bytes\n")
                                f.write(f"# Original path: {file_path}\n")
                                f.write(f"# Error: {e}\n")
                            error_files.append(file_path)
                    
                    processed += 1
                    
                    if total_files > 0 and processed % 10 == 0:
                        progress = (processed / total_files) * 100
                        def update_progress():
                            self.progress_var.set(progress)
                        self.root.after(0, update_progress)
                    
                    if processed % 50 == 0:
                        progress_percent = int((processed / total_files) * 100) if total_files > 0 else 0
                        self.log(f"Processing... {processed}/{total_files} files ({progress_percent}%) - {large_files_count} large, {force_replaced_count} force replaced, {force_kept_count} force kept")
                    
                    if processed % 1000 == 0:
                        self.log(f"Milestone: {processed} files processed, {large_files_count} large files, {force_replaced_count} force replaced, {force_kept_count} force kept, {len(error_files)} errors")
                    
                except Exception as e:
                    self.log(f"{self.localizer.get('error_processing_file')}: {file_path} - {e}")
                    error_files.append(file_path)
            
            def final_update():
                self.progress_var.set(100)
                self.status_var.set(self.localizer.get('completed'))
            self.root.after(0, final_update)
            
            self.log(f"{self.localizer.get('dump_completed')}")
            self.log(f"{self.localizer.get('total_files')}: {total_files}")
            self.log(f"{self.localizer.get('large_files_replaced')}: {large_files_count}")
            if force_replaced_count > 0:
                self.log(f"{self.localizer.get('force_replaced_files')}: {force_replaced_count}")
            if force_kept_count > 0:
                self.log(f"{self.localizer.get('force_kept_files')}: {force_kept_count}")
            if error_files:
                self.log(f"Files with errors: {len(error_files)}")
            self.log(f"Output directory: {output_dir}")
            
            def show_success():
                messagebox.showinfo(self.localizer.get('success'), 
                                  self.localizer.get('dump_completed_successfully'))
            self.root.after(0, show_success)
            
        except Exception as e:
            error_msg = f"{self.localizer.get('dump_failed')}: {e}"
            self.log(error_msg)
            
            def update_error_status():
                self.status_var.set(self.localizer.get('failed'))
                messagebox.showerror(self.localizer.get('error'), error_msg)
            self.root.after(0, update_error_status)
        
        finally:
            def final_cleanup():
                self.is_processing = False
                self.start_button.config(state='normal')
            self.root.after(0, final_cleanup)
    
    def run(self):
        self.root.mainloop()


def main():
    app = PathDumper()
    app.run()


if __name__ == "__main__":
    main()
