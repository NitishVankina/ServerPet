#!/usr/bin/env python3
"""
System Monitor Pet - Premium Edition with Advanced Features
Works on Linux and Windows
Requires: pip install psutil customtkinter pillow matplotlib numpy
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import psutil
import threading
import time
from datetime import datetime, timedelta
import math
import random
import platform
from collections import deque

class AdvancedSystemPetGUI:
    def __init__(self):
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        # Class-level constants for colors and emojis
        self.MOOD_COLORS = {
            'happy': '#4CAF50',
            'content': '#2196F3',
            'worried': '#FF9800',
            'critical': '#F44336'
        }
        self.MOOD_EMOJIS = {
            'happy': '😊',
            'content': '😌',
            'worried': '😰',
            'critical': '😵'
        }
        
        # Create main window with modern style
        self.root = ctk.CTk()
        self.root.title("System Pet Monitor - Premium Edition")
        self.root.geometry("900x850")
        self.root.resizable(True, True)
        
        # Pet state and preferences
        self.pet_name = "Byte"
        self.pet_type = "cat"  # cat, dog, robot
        self.mood = "happy"
        self.animation_frame = 0
        self.blink_counter = 0
        self.is_blinking = False
        self.enable_sound = True
        self.alert_shown = False
        
        # Data history for graphs (last 60 data points)
        self.cpu_history = deque(maxlen=60)
        self.ram_history = deque(maxlen=60)
        self.disk_history = deque(maxlen=60)
        self.net_history = deque(maxlen=60)
        
        # Network tracking
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()
        
        # Temperature support
        self.temp_available = self.check_temp_support()
        
        # Statistics
        self.stats = {
            'happy_time': 0,
            'worried_time': 0,
            'critical_time': 0,
            'total_time': 0,
            'max_cpu': 0,
            'max_ram': 0,
            'max_disk': 0
        }
        
        # Create UI
        self.create_ui()
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
        
        # Start animation
        self.animate_pet()
        
        # Update graph
        self.update_graph()
        
    def check_temp_support(self):
        """Check if temperature sensors are available"""
        try:
            temps = psutil.sensors_temperatures()
            return len(temps) > 0
        except:
            return False
    
    def create_ui(self):
        """Create the enhanced user interface"""
        
        # Create notebook (tabs)
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Add tabs
        self.notebook.add("Dashboard")
        self.notebook.add("Details")
        self.notebook.add("History")
        self.notebook.add("Settings")
        
        # Create each tab
        self.create_dashboard_tab()
        self.create_details_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
    def create_dashboard_tab(self):
        """Create main dashboard"""
        tab = self.notebook.tab("Dashboard")
        
        # Top section with pet and status
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Pet display
        pet_container = ctk.CTkFrame(top_frame, corner_radius=15)
        pet_container.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Pet name label
        name_label = ctk.CTkLabel(
            pet_container,
            text=f"🐱 Meet {self.pet_name}!",
            font=("Arial", 22, "bold")
        )
        name_label.pack(pady=(15, 5))
        
        # Pet canvas
        self.pet_canvas = tk.Canvas(
            pet_container,
            width=280,
            height=280,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.pet_canvas.pack(pady=10)
        
        # Mood indicator
        self.mood_label = ctk.CTkLabel(
            pet_container,
            text="Mood: Happy 😊",
            font=("Arial", 16, "bold"),
            text_color="#4CAF50"
        )
        self.mood_label.pack(pady=5)
        
        # Pet message with bubble effect
        self.pet_message = ctk.CTkLabel(
            pet_container,
            text="Everything is running perfectly!",
            font=("Arial", 13),
            wraplength=250,
            justify="center"
        )
        self.pet_message.pack(pady=(5, 15))
        
        # Right side - Quick stats
        stats_container = ctk.CTkFrame(top_frame, corner_radius=15)
        stats_container.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        stats_title = ctk.CTkLabel(
            stats_container,
            text="⚡ System Status",
            font=("Arial", 20, "bold")
        )
        stats_title.pack(pady=(15, 10))
        
        # CPU Section
        self.create_stat_section(stats_container, "CPU", "cpu")
        
        # RAM Section
        self.create_stat_section(stats_container, "RAM", "ram")
        
        # Disk Section
        self.create_stat_section(stats_container, "disk", "disk")
        
        # Network Section
        self.create_stat_section(stats_container, "Network", "net")
        
        # Bottom info bar
        info_bar = ctk.CTkFrame(tab, height=50, corner_radius=10)
        info_bar.pack(fill="x", padx=10, pady=(5, 10))
        info_bar.pack_propagate(False)
        
        self.info_label = ctk.CTkLabel(
            info_bar,
            text="Initializing...",
            font=("Arial", 12)
        )
        self.info_label.pack(expand=True)
        
    def create_stat_section(self, parent, name, key):
        """Create a stat display section"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=8)
        
        # Icon and label
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x")
        
        icons = {"CPU": "💻", "RAM": "🧠", "disk": "💾", "Network": "🌐"}
        label = ctk.CTkLabel(
            label_frame,
            text=f"{icons.get(name, '📊')} {name}",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        label.pack(side="left")
        
        # Value label
        value_label = ctk.CTkLabel(
            label_frame,
            text="0%",
            font=("Arial", 13),
            anchor="e"
        )
        value_label.pack(side="right")
        
        # Progress bar
        bar = ctk.CTkProgressBar(frame, width=300, height=15)
        bar.pack(fill="x", pady=(3, 0))
        bar.set(0)
        
        # Store references
        setattr(self, f"{key}_bar_dash", bar)
        setattr(self, f"{key}_label_dash", value_label)
    
    def create_details_tab(self):
        """Create detailed system information tab"""
        tab = self.notebook.tab("Details")
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # System Information
        sys_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        sys_frame.pack(fill="x", pady=(0, 10))
        
        sys_title = ctk.CTkLabel(sys_frame, text="💻 System Information", font=("Arial", 18, "bold"))
        sys_title.pack(pady=10, anchor="w", padx=15)
        
        # Get system info
        self.sys_info_text = ctk.CTkTextbox(sys_frame, height=200, font=("Courier", 11))
        self.sys_info_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # CPU Details
        cpu_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        cpu_frame.pack(fill="x", pady=(0, 10))
        
        cpu_title = ctk.CTkLabel(cpu_frame, text="🔥 CPU Details", font=("Arial", 18, "bold"))
        cpu_title.pack(pady=10, anchor="w", padx=15)
        
        self.cpu_details_text = ctk.CTkTextbox(cpu_frame, height=150, font=("Courier", 11))
        self.cpu_details_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Memory Details
        mem_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        mem_frame.pack(fill="x", pady=(0, 10))
        
        mem_title = ctk.CTkLabel(mem_frame, text="🧠 Memory Details", font=("Arial", 18, "bold"))
        mem_title.pack(pady=10, anchor="w", padx=15)
        
        self.mem_details_text = ctk.CTkTextbox(mem_frame, height=150, font=("Courier", 11))
        self.mem_details_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Disk Details
        disk_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        disk_frame.pack(fill="x", pady=(0, 10))
        
        disk_title = ctk.CTkLabel(disk_frame, text="💾 Disk Details", font=("Arial", 18, "bold"))
        disk_title.pack(pady=10, anchor="w", padx=15)
        
        self.disk_details_text = ctk.CTkTextbox(disk_frame, height=150, font=("Courier", 11))
        self.disk_details_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Network Details
        net_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        net_frame.pack(fill="x", pady=(0, 10))
        
        net_title = ctk.CTkLabel(net_frame, text="🌐 Network Details", font=("Arial", 18, "bold"))
        net_title.pack(pady=10, anchor="w", padx=15)
        
        self.net_details_text = ctk.CTkTextbox(net_frame, height=150, font=("Courier", 11))
        self.net_details_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Process List
        proc_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        proc_frame.pack(fill="x", pady=(0, 10))
        
        proc_title = ctk.CTkLabel(proc_frame, text="⚙️ Top Processes", font=("Arial", 18, "bold"))
        proc_title.pack(pady=10, anchor="w", padx=15)
        
        self.proc_details_text = ctk.CTkTextbox(proc_frame, height=200, font=("Courier", 11))
        self.proc_details_text.pack(fill="x", padx=15, pady=(0, 15))
    
    def create_history_tab(self):
        """Create history/graph tab"""
        tab = self.notebook.tab("History")
        
        title = ctk.CTkLabel(tab, text="📊 Performance History", font=("Arial", 20, "bold"))
        title.pack(pady=15)
        
        # Graph canvas
        self.graph_canvas = tk.Canvas(tab, bg="#1a1a1a", highlightthickness=0)
        self.graph_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Stats summary
        stats_frame = ctk.CTkFrame(tab, corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        stats_title = ctk.CTkLabel(stats_frame, text="📈 Session Statistics", font=("Arial", 16, "bold"))
        stats_title.pack(pady=10)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="No data yet...",
            font=("Courier", 11),
            justify="left"
        )
        self.stats_label.pack(pady=(0, 15), padx=20)
    
    def create_settings_tab(self):
        """Create settings tab"""
        tab = self.notebook.tab("Settings")
        
        title = ctk.CTkLabel(tab, text="⚙️ Settings & Preferences", font=("Arial", 20, "bold"))
        title.pack(pady=15)
        
        # Pet Settings
        pet_frame = ctk.CTkFrame(tab, corner_radius=10)
        pet_frame.pack(fill="x", padx=15, pady=10)
        
        pet_label = ctk.CTkLabel(pet_frame, text="🐱 Pet Settings", font=("Arial", 16, "bold"))
        pet_label.pack(pady=10, anchor="w", padx=15)
        
        # Pet name
        name_frame = ctk.CTkFrame(pet_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(name_frame, text="Pet Name:", font=("Arial", 13)).pack(side="left", padx=(0, 10))
        
        self.name_entry = ctk.CTkEntry(name_frame, width=200)
        self.name_entry.pack(side="left")
        self.name_entry.insert(0, self.pet_name)
        
        name_btn = ctk.CTkButton(name_frame, text="Update", width=80, command=self.update_pet_name)
        name_btn.pack(side="left", padx=10)
        
        # Pet type selector
        type_frame = ctk.CTkFrame(pet_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(type_frame, text="Pet Type:", font=("Arial", 13)).pack(side="left", padx=(0, 10))
        
        self.pet_type_var = ctk.StringVar(value=self.pet_type)
        pet_type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=["cat", "dog", "robot"],
            variable=self.pet_type_var,
            command=self.change_pet_type,
            width=200
        )
        pet_type_menu.pack(side="left", pady=10)
        
        # Alert Settings
        alert_frame = ctk.CTkFrame(tab, corner_radius=10)
        alert_frame.pack(fill="x", padx=15, pady=10)
        
        alert_label = ctk.CTkLabel(alert_frame, text="🔔 Alert Settings", font=("Arial", 16, "bold"))
        alert_label.pack(pady=10, anchor="w", padx=15)
        
        self.alert_enabled = ctk.CTkCheckBox(
            alert_frame,
            text="Enable desktop notifications for critical alerts",
            font=("Arial", 12)
        )
        self.alert_enabled.pack(padx=15, pady=5, anchor="w")
        self.alert_enabled.select()
        
        # Thresholds
        thresh_frame = ctk.CTkFrame(tab, corner_radius=10)
        thresh_frame.pack(fill="x", padx=15, pady=10)
        
        thresh_label = ctk.CTkLabel(thresh_frame, text="⚠️ Alert Thresholds", font=("Arial", 16, "bold"))
        thresh_label.pack(pady=10, anchor="w", padx=15)
        
        # CPU threshold
        cpu_thresh = ctk.CTkFrame(thresh_frame, fg_color="transparent")
        cpu_thresh.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(cpu_thresh, text="CPU Critical:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.cpu_thresh_slider = ctk.CTkSlider(cpu_thresh, from_=50, to=100, number_of_steps=50, width=200)
        self.cpu_thresh_slider.pack(side="left")
        self.cpu_thresh_slider.set(90)
        self.cpu_thresh_label = ctk.CTkLabel(cpu_thresh, text="90%", font=("Arial", 12))
        self.cpu_thresh_label.pack(side="left", padx=10)
        self.cpu_thresh_slider.configure(command=lambda v: self.cpu_thresh_label.configure(text=f"{int(v)}%"))
        
        # About section
        about_frame = ctk.CTkFrame(tab, corner_radius=10)
        about_frame.pack(fill="x", padx=15, pady=10)
        
        about_label = ctk.CTkLabel(about_frame, text="ℹ️ About", font=("Arial", 16, "bold"))
        about_label.pack(pady=10, anchor="w", padx=15)
        
        about_text = f"""System Pet Monitor - Premium Edition
Version 2.0
        
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}
        
A cute companion that watches over your system!
        """
        
        about_display = ctk.CTkLabel(
            about_frame,
            text=about_text,
            font=("Arial", 11),
            justify="left"
        )
        about_display.pack(pady=(0, 15), padx=20, anchor="w")
    
    def update_pet_name(self):
        """Update pet name"""
        new_name = self.name_entry.get().strip()
        if new_name:
            self.pet_name = new_name
            messagebox.showinfo("Success", f"Pet name updated to {self.pet_name}!")
    
    def change_pet_type(self, choice):
        """Change pet type"""
        self.pet_type = choice
    
    def draw_pet(self, mood, is_blinking=False):
        """Draw the pet based on type and mood"""
        canvas = self.pet_canvas
        canvas.delete("all")
        
        if self.pet_type == "cat":
            self.draw_cat(canvas, mood, is_blinking)
        elif self.pet_type == "dog":
            self.draw_dog(canvas, mood, is_blinking)
        else:
            self.draw_robot(canvas, mood, is_blinking)
    
    def draw_cat(self, canvas, mood, is_blinking):
        """Draw cat pet"""
        colors = {
            'happy': {'body': '#FFB6C1', 'accent': '#FF69B4', 'dark': '#FF1493'},
            'content': {'body': '#87CEEB', 'accent': '#4682B4', 'dark': '#1E90FF'},
            'worried': {'body': '#FFD700', 'accent': '#FFA500', 'dark': '#FF8C00'},
            'critical': {'body': '#FF6B6B', 'accent': '#DC143C', 'dark': '#8B0000'}
        }
        
        color = colors.get(mood, colors['content'])
        
        # Body
        canvas.create_oval(90, 100, 190, 200, fill=color['body'], outline=color['accent'], width=4)
        
        # Ears
        if mood in ['worried', 'critical']:
            canvas.create_polygon(100, 110, 90, 80, 120, 100, fill=color['body'], outline=color['accent'], width=3)
            canvas.create_polygon(180, 110, 190, 80, 160, 100, fill=color['body'], outline=color['accent'], width=3)
        else:
            canvas.create_polygon(100, 100, 90, 60, 120, 90, fill=color['body'], outline=color['accent'], width=3)
            canvas.create_polygon(180, 100, 190, 60, 160, 90, fill=color['body'], outline=color['accent'], width=3)
        
        # Eyes
        if is_blinking:
            canvas.create_line(115, 140, 130, 140, fill='black', width=4)
            canvas.create_line(150, 140, 165, 140, fill='black', width=4)
        else:
            if mood == 'critical':
                # X eyes
                canvas.create_line(115, 135, 130, 150, fill='black', width=4)
                canvas.create_line(130, 135, 115, 150, fill='black', width=4)
                canvas.create_line(150, 135, 165, 150, fill='black', width=4)
                canvas.create_line(165, 135, 150, 150, fill='black', width=4)
            elif mood == 'worried':
                canvas.create_oval(115, 135, 135, 155, fill='black')
                canvas.create_oval(145, 135, 165, 155, fill='black')
            else:
                canvas.create_oval(115, 135, 135, 155, fill='black')
                canvas.create_oval(120, 138, 127, 145, fill='white')
                canvas.create_oval(145, 135, 165, 155, fill='black')
                canvas.create_oval(150, 138, 157, 145, fill='white')
        
        # Nose
        canvas.create_polygon(140, 155, 135, 160, 145, 160, fill=color['dark'])
        
        # Mouth
        if mood == 'happy':
            canvas.create_arc(110, 150, 170, 190, start=0, extent=-180, style=tk.ARC, width=3)
        elif mood == 'content':
            canvas.create_arc(120, 160, 160, 180, start=0, extent=-180, style=tk.ARC, width=3)
        elif mood == 'worried':
            canvas.create_arc(120, 170, 160, 190, start=0, extent=180, style=tk.ARC, width=3)
        else:
            canvas.create_oval(135, 165, 145, 180, fill='black')
        
        # Whiskers
        canvas.create_line(80, 145, 110, 150, fill=color['dark'], width=2)
        canvas.create_line(80, 155, 110, 155, fill=color['dark'], width=2)
        canvas.create_line(80, 165, 110, 160, fill=color['dark'], width=2)
        canvas.create_line(200, 145, 170, 150, fill=color['dark'], width=2)
        canvas.create_line(200, 155, 170, 155, fill=color['dark'], width=2)
        canvas.create_line(200, 165, 170, 160, fill=color['dark'], width=2)
        
        # Paws
        canvas.create_oval(105, 190, 125, 210, fill=color['body'], outline=color['accent'], width=3)
        canvas.create_oval(155, 190, 175, 210, fill=color['body'], outline=color['accent'], width=3)
        
        # Tail (animated)
        tail_swing = math.sin(self.animation_frame * 0.15) * 15
        canvas.create_arc(170, 150, 230, 210, start=180+tail_swing, extent=90, style=tk.ARC, 
                         outline=color['accent'], width=5)
        
        # Floating animation
        offset = math.sin(self.animation_frame * 0.08) * 4
        canvas.move("all", 0, offset)
        
        # Sweat drops for worried/critical
        if mood in ['worried', 'critical']:
            num_drops = 2 if mood == 'worried' else 4
            for i in range(num_drops):
                x = 185 + i * 12
                y = 110 + (i % 2) * 20
                canvas.create_oval(x, y, x+6, y+10, fill='#87CEEB', outline='#4682B4', width=2)
    
    def draw_dog(self, canvas, mood, is_blinking):
        """Draw dog pet"""
        colors = {
            'happy': {'body': '#D2691E', 'accent': '#8B4513', 'light': '#F4A460'},
            'content': {'body': '#DEB887', 'accent': '#BC8F8F', 'light': '#FFE4B5'},
            'worried': {'body': '#DAA520', 'accent': '#B8860B', 'light': '#FFD700'},
            'critical': {'body': '#CD853F', 'accent': '#A0522D', 'light': '#F5DEB3'}
        }
        
        color = colors.get(mood, colors['content'])
        
        # Body
        canvas.create_oval(90, 100, 190, 200, fill=color['body'], outline=color['accent'], width=4)
        
        # Ears (floppy)
        canvas.create_oval(70, 110, 110, 170, fill=color['body'], outline=color['accent'], width=3)
        canvas.create_oval(170, 110, 210, 170, fill=color['body'], outline=color['accent'], width=3)
        
        # Snout
        canvas.create_oval(120, 160, 160, 190, fill=color['light'], outline=color['accent'], width=3)
        
        # Eyes
        if is_blinking:
            canvas.create_line(115, 135, 125, 135, fill='black', width=4)
            canvas.create_line(155, 135, 165, 135, fill='black', width=4)
        else:
            if mood == 'critical':
                canvas.create_line(110, 130, 125, 145, fill='black', width=4)
                canvas.create_line(125, 130, 110, 145, fill='black', width=4)
                canvas.create_line(155, 130, 170, 145, fill='black', width=4)
                canvas.create_line(170, 130, 155, 145, fill='black', width=4)
            else:
                canvas.create_oval(110, 130, 130, 150, fill='black')
                canvas.create_oval(115, 133, 122, 140, fill='white')
                canvas.create_oval(150, 130, 170, 150, fill='black')
                canvas.create_oval(155, 133, 162, 140, fill='white')
        
        # Nose
        canvas.create_oval(135, 170, 145, 180, fill='black')
        
        # Mouth
        if mood == 'happy':
            # Tongue out
            canvas.create_line(140, 180, 140, 195, fill='black', width=2)
            canvas.create_oval(130, 190, 150, 205, fill='#FF69B4', outline='#FF1493', width=2)
        
        # Tail (wagging if happy)
        if mood == 'happy':
            tail_wag = math.sin(self.animation_frame * 0.3) * 20
        else:
            tail_wag = -10
        
        canvas.create_arc(160, 150, 220, 210, start=180+tail_wag, extent=80, style=tk.ARC,
                         outline=color['accent'], width=6)
        
        # Floating animation
        offset = math.sin(self.animation_frame * 0.08) * 4
        canvas.move("all", 0, offset)
    
    def draw_robot(self, canvas, mood, is_blinking):
        """Draw robot pet"""
        colors = {
            'happy': {'body': '#4CAF50', 'accent': '#2E7D32', 'screen': '#00FF00'},
            'content': {'body': '#2196F3', 'accent': '#1565C0', 'screen': '#00BFFF'},
            'worried': {'body': '#FF9800', 'accent': '#E65100', 'screen': '#FFA500'},
            'critical': {'body': '#F44336', 'accent': '#C62828', 'screen': '#FF0000'}
        }
        
        color = colors.get(mood, colors['content'])
        
        # Body (rounded rectangle)
        canvas.create_rectangle(100, 120, 180, 200, fill=color['body'], outline=color['accent'], width=4)
        canvas.create_oval(95, 115, 105, 125, fill=color['body'], outline=color['accent'], width=4)
        canvas.create_oval(175, 115, 185, 125, fill=color['body'], outline=color['accent'], width=4)
        
        # Head
        canvas.create_rectangle(110, 80, 170, 130, fill=color['body'], outline=color['accent'], width=4)
        
        # Antenna
        canvas.create_line(140, 80, 140, 60, fill=color['accent'], width=3)
        canvas.create_oval(135, 55, 145, 65, fill=color['screen'], outline=color['accent'], width=2)
        
        # Blinking antenna light
        if self.animation_frame % 20 < 10:
            canvas.create_oval(137, 57, 143, 63, fill='white')
        
        # Screen/Face
        screen_color = color['screen'] if not is_blinking else color['body']
        canvas.create_rectangle(115, 90, 165, 120, fill='#1a1a1a', outline=color['accent'], width=3)
        
        # Eyes on screen
        if is_blinking:
            canvas.create_line(125, 100, 135, 100, fill=screen_color, width=3)
            canvas.create_line(145, 100, 155, 100, fill=screen_color, width=3)
        else:
            if mood == 'critical':
                canvas.create_line(125, 95, 135, 110, fill=screen_color, width=3)
                canvas.create_line(135, 95, 125, 110, fill=screen_color, width=3)
                canvas.create_line(145, 95, 155, 110, fill=screen_color, width=3)
                canvas.create_line(155, 95, 145, 110, fill=screen_color, width=3)
            else:
                canvas.create_rectangle(125, 95, 135, 110, fill=screen_color)
                canvas.create_rectangle(145, 95, 155, 110, fill=screen_color)
        
        # Mouth on screen
        if mood == 'happy':
            canvas.create_arc(125, 105, 155, 125, start=0, extent=-180, 
                            style=tk.ARC, outline=screen_color, width=3)
        elif mood == 'worried':
            canvas.create_arc(125, 115, 155, 135, start=0, extent=180,
                            style=tk.ARC, outline=screen_color, width=3)
        
        # Arms
        canvas.create_rectangle(85, 135, 100, 165, fill=color['body'], outline=color['accent'], width=3)
        canvas.create_rectangle(180, 135, 195, 165, fill=color['body'], outline=color['accent'], width=3)
        
        # Legs
        canvas.create_rectangle(110, 200, 130, 230, fill=color['body'], outline=color['accent'], width=3)
        canvas.create_rectangle(150, 200, 170, 230, fill=color['body'], outline=color['accent'], width=3)
        
        # Panel details
        for i in range(3):
            y = 140 + i * 15
            canvas.create_line(110, y, 170, y, fill=color['accent'], width=1)
        
        # Floating animation
        offset = math.sin(self.animation_frame * 0.08) * 4
        canvas.move("all", 0, offset)
    
    def animate_pet(self):
        """Animate the pet"""
        self.animation_frame += 1
        
        # Blinking logic
        self.blink_counter += 1
        if self.blink_counter > 100:
            self.is_blinking = True
            self.blink_counter = 0
        elif self.blink_counter > 5:
            self.is_blinking = False
        
        self.draw_pet(self.mood, self.is_blinking)
        self.root.after(30, self.animate_pet)
    
    def update_graph(self):
        """Update the performance history graph"""
        canvas = self.graph_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width < 100 or height < 100:
            self.root.after(100, self.update_graph)
            return
        
        # Draw graph background
        canvas.create_rectangle(0, 0, width, height, fill='#1a1a1a', outline='')
        
        # Graph area
        margin = 40
        graph_width = width - 2 * margin
        graph_height = height - 2 * margin
        
        # Draw grid
        for i in range(0, 101, 25):
            y = margin + graph_height - (i / 100 * graph_height)
            canvas.create_line(margin, y, width - margin, y, fill='#333333', dash=(2, 4))
            canvas.create_text(margin - 10, y, text=f"{i}%", fill='#666666', anchor='e', font=("Arial", 8))
        
        # Draw data if available
        if len(self.cpu_history) > 1:
            self.draw_line_graph(canvas, self.cpu_history, '#FF6B6B', margin, graph_width, graph_height)
            self.draw_line_graph(canvas, self.ram_history, '#4CAF50', margin, graph_width, graph_height)
            self.draw_line_graph(canvas, self.disk_history, '#2196F3', margin, graph_width, graph_height)
        
        # Legend
        legend_x = width - margin - 100
        legend_y = margin + 10
        
        canvas.create_rectangle(legend_x - 5, legend_y - 5, legend_x + 95, legend_y + 65, 
                              fill='#2a2a2a', outline='#444444')
        
        canvas.create_line(legend_x, legend_y + 5, legend_x + 20, legend_y + 5, fill='#FF6B6B', width=2)
        canvas.create_text(legend_x + 25, legend_y + 5, text='CPU', fill='white', anchor='w', font=("Arial", 9))
        
        canvas.create_line(legend_x, legend_y + 25, legend_x + 20, legend_y + 25, fill='#4CAF50', width=2)
        canvas.create_text(legend_x + 25, legend_y + 25, text='RAM', fill='white', anchor='w', font=("Arial", 9))
        
        canvas.create_line(legend_x, legend_y + 45, legend_x + 20, legend_y + 45, fill='#2196F3', width=2)
        canvas.create_text(legend_x + 25, legend_y + 45, text='Disk', fill='white', anchor='w', font=("Arial", 9))
        
        self.root.after(2000, self.update_graph)
    
    def draw_line_graph(self, canvas, data, color, margin, graph_width, graph_height):
        """Draw a line graph on canvas"""
        if len(data) < 2:
            return
        
        points = []
        data_len = len(data)
        
        for i, value in enumerate(data):
            x = margin + (i / (data_len - 1)) * graph_width
            y = margin + graph_height - (value / 100 * graph_height)
            points.extend([x, y])
        
        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=2, smooth=True)
    
    def determine_mood(self, cpu, ram, disk):
        """Determine pet's mood"""
        threshold = self.cpu_thresh_slider.get()
        
        if cpu > threshold or ram > threshold or disk > threshold:
            return 'critical'
        elif cpu > 75 or ram > 75 or disk > 75:
            return 'worried'
        elif cpu < 30 and ram < 50 and disk < 70:
            return 'happy'
        else:
            return 'content'
    
    def get_mood_emoji(self, mood):
        """Get emoji for mood"""
        return self.MOOD_EMOJIS.get(mood, '🙂')
    
    def get_mood_color(self, mood):
        """Get color for mood"""
        return self.MOOD_COLORS.get(mood, '#2196F3')
    
    def get_message(self, mood, cpu, ram, disk):
        """Get message based on mood"""
        messages = {
            'happy': [
                "Everything is perfect! I'm so happy! ✨",
                "All systems running beautifully! 🌟",
                "I love it when things are this smooth! 💖",
                "This is wonderful! Keep it up! 🎉",
                "Feeling great! Everything's optimal! 🚀"
            ],
            'content': [
                "Everything looks good! Cruising along~",
                "All systems nominal! Doing great! ✓",
                "Nice and steady! No worries here!",
                "Running smoothly! All is well!",
                "Everything's under control! 👍"
            ],
            'worried': [
                "Umm... I'm getting a bit worried here... 😰",
                "Things are getting heavy... Please check! ⚠️",
                "I'm feeling the pressure... 💦",
                "This is making me nervous... 😟",
                "Resources are running high... help!"
            ],
            'critical': [
                "🚨 HELP! I CAN'T BREATHE! 🚨",
                "CRITICAL! Everything is too much! 😵",
                "I'M DYING! Please help me! 💀",
                "EMERGENCY! I need help NOW! ⚠️",
                "SYSTEM OVERLOAD! Do something! 🔥"
            ]
        }
        
        return random.choice(messages[mood])
    
    def format_bytes(self, bytes):
        """Format bytes to human readable"""
    def format_bytes(self, bytes_val: float) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    def update_system_info(self):
        """Update system information in details tab"""
        try:
            # System Info
            uname = platform.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            sys_info = f"""System: {uname.system} {uname.release}
Machine: {uname.machine}
Processor: {uname.processor}
Hostname: {uname.node}
Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {self.format_uptime(uptime)}
Python: {platform.python_version()}
"""
            self.sys_info_text.delete("1.0", "end")
            self.sys_info_text.insert("1.0", sys_info)
            
            # CPU Details
            cpu_freq = psutil.cpu_freq()
            cpu_info = f"""Physical Cores: {psutil.cpu_count(logical=False)}
Logical Cores: {psutil.cpu_count(logical=True)}
Max Frequency: {cpu_freq.max:.2f} MHz
Min Frequency: {cpu_freq.min:.2f} MHz
Current Frequency: {cpu_freq.current:.2f} MHz

Per-Core Usage:
"""
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
                cpu_info += f"Core {i}: {percentage}%\n"
            
            self.cpu_details_text.delete("1.0", "end")
            self.cpu_details_text.insert("1.0", cpu_info)
            
            # Memory Details
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            mem_info = f"""Total: {self.format_bytes(mem.total)}
Available: {self.format_bytes(mem.available)}
Used: {self.format_bytes(mem.used)}
Free: {self.format_bytes(mem.free)}
Percent: {mem.percent}%

Swap Memory:
Total: {self.format_bytes(swap.total)}
Used: {self.format_bytes(swap.used)}
Free: {self.format_bytes(swap.free)}
Percent: {swap.percent}%
"""
            self.mem_details_text.delete("1.0", "end")
            self.mem_details_text.insert("1.0", mem_info)
            
            # Disk Details
            disk_info = "Partitions:\n"
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info += f"\nDevice: {partition.device}\n"
                    disk_info += f"Mountpoint: {partition.mountpoint}\n"
                    disk_info += f"File System: {partition.fstype}\n"
                    disk_info += f"Total: {self.format_bytes(usage.total)}\n"
                    disk_info += f"Used: {self.format_bytes(usage.used)}\n"
                    disk_info += f"Free: {self.format_bytes(usage.free)}\n"
                    disk_info += f"Percent: {usage.percent}%\n"
                except:
                    pass
            
            self.disk_details_text.delete("1.0", "end")
            self.disk_details_text.insert("1.0", disk_info)
            
            # Network Details
            net_io = psutil.net_io_counters()
            net_info = f"""Bytes Sent: {self.format_bytes(net_io.bytes_sent)}
Bytes Received: {self.format_bytes(net_io.bytes_recv)}
Packets Sent: {net_io.packets_sent}
Packets Received: {net_io.packets_recv}
Errors In: {net_io.errin}
Errors Out: {net_io.errout}
Drops In: {net_io.dropin}
Drops Out: {net_io.dropout}

Network Interfaces:
"""
            for iface, addrs in psutil.net_if_addrs().items():
                net_info += f"\n{iface}:\n"
                for addr in addrs:
                    net_info += f"  {addr.family.name}: {addr.address}\n"
            
            self.net_details_text.delete("1.0", "end")
            self.net_details_text.insert("1.0", net_info)
            
            # Top Processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except:
                    pass
            
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            proc_info = f"{'PID':<8} {'NAME':<30} {'CPU%':<8} {'MEM%':<8}\n"
            proc_info += "=" * 60 + "\n"
            
            for proc in processes[:15]:
                proc_info += f"{proc['pid']:<8} {proc['name'][:29]:<30} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f}\n"
            
            self.proc_details_text.delete("1.0", "end")
            self.proc_details_text.insert("1.0", proc_info)
            
        except Exception as e:
            print(f"Error updating details: {e}")
    
    def format_uptime(self, uptime):
        """Format uptime timedelta"""
    def format_uptime(self, uptime: timedelta) -> str:
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes = remainder // 60
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_bars_color(self, bar, value):
        """Update progress bar color"""
    def update_bars_color(self, bar: ctk.CTkProgressBar, value: float) -> None:
        if value > 90:
            bar.configure(progress_color="#DC143C")
        elif value > 75:
            bar.configure(progress_color="#FFA500")
        else:
            bar.configure(progress_color="#4CAF50")
    
    def monitor_system(self):
        """Monitor system resources"""
    def monitor_system(self) -> None:
        start_time = time.time()
        poll_interval = 2
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                net_io = psutil.net_io_counters()
                current_time = time.time()
                time_delta = current_time - self.last_net_time
                bytes_sent = net_io.bytes_sent - self.last_net_io.bytes_sent
                bytes_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
                net_speed = (bytes_sent + bytes_recv) / time_delta / 1024  # KB/s
                self.last_net_io = net_io
                self.last_net_time = current_time
                self.cpu_history.append(cpu)
                self.ram_history.append(ram)
                self.disk_history.append(disk)
                self.net_history.append(min(net_speed / 1024 * 10, 100))
                self.stats['max_cpu'] = max(self.stats['max_cpu'], cpu)
                self.stats['max_ram'] = max(self.stats['max_ram'], ram)
                self.stats['max_disk'] = max(self.stats['max_disk'], disk)
                self.stats['total_time'] = time.time() - start_time
                new_mood = self.determine_mood(cpu, ram, disk)
                if new_mood == 'happy':
                    self.stats['happy_time'] += poll_interval
                elif new_mood == 'worried':
                    self.stats['worried_time'] += poll_interval
                elif new_mood == 'critical':
                    self.stats['critical_time'] += poll_interval
                self.root.after(0, self.update_ui, cpu, ram, disk, net_speed, new_mood)
                if new_mood == 'critical' and not self.alert_shown and self.alert_enabled.get():
                    self.root.after(0, self.show_alert, cpu, ram, disk)
                    self.alert_shown = True
                elif new_mood != 'critical':
                    self.alert_shown = False
                time.sleep(poll_interval)
            except Exception as e:
                import traceback
                print(f"Error in monitor: {e}\n{traceback.format_exc()}")
    
    def show_alert(self, cpu, ram, disk):
        """Show critical alert"""
        issues = []
        if cpu > 90:
            issues.append(f"CPU: {cpu:.1f}%")
        if ram > 90:
            issues.append(f"RAM: {ram:.1f}%")
        if disk > 90:
            issues.append(f"Disk: {disk:.1f}%")
        
        messagebox.showwarning(
            "Critical System Alert",
            f"⚠️ {self.pet_name} is in distress!\n\nHigh resource usage detected:\n" + "\n".join(issues)
        )
    
    def update_ui(self, cpu, ram, disk, net_speed, new_mood):
        """Update the UI"""
    def update_ui(self, cpu: float, ram: float, disk: float, net_speed: float, new_mood: str) -> None:
        try:
            # Update dashboard bars and colors
            for key, value in zip(['cpu', 'ram', 'disk', 'net'], [cpu, ram, disk, net_speed]):
                bar = getattr(self, f"{key}_bar_dash", None)
                label = getattr(self, f"{key}_label_dash", None)
                if bar:
                    if key == 'net':
                        bar.set(min(net_speed / 1024, 1))
                    else:
                        bar.set(value / 100)
                    if key != 'net':
                        self.update_bars_color(bar, value)
                if label:
                    if key == 'net':
                        label.configure(text=f"{net_speed:.1f} KB/s")
                    else:
                        label.configure(text=f"{value:.1f}%")
            # Update mood
            if new_mood != self.mood:
                self.mood = new_mood
                mood_text = f"Mood: {new_mood.capitalize()} {self.get_mood_emoji(new_mood)}"
                self.mood_label.configure(text=mood_text, text_color=self.get_mood_color(new_mood))
                self.pet_message.configure(text=self.get_message(new_mood, cpu, ram, disk))
            # Update info bar
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            process_count = len(psutil.pids())
            info_text = f"⏰ Uptime: {self.format_uptime(uptime)} | "
            info_text += f"📊 Processes: {process_count} | "
            info_text += f"🌐 Network: {net_speed:.1f} KB/s"
            if self.temp_available:
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries:
                                temp = entries[0].current
                                info_text += f" | 🌡️ Temp: {temp:.1f}°C"
                                break
                except Exception:
                    pass
            self.info_label.configure(text=info_text)
            # Update details tab and statistics
            self.update_system_info()
            self.update_statistics_display()
        except Exception as e:
            import traceback
            print(f"Error updating UI: {e}\n{traceback.format_exc()}")
    
    def update_statistics_display(self):
        """Update the statistics display"""
        total_time = self.stats['total_time']
        
        if total_time > 0:
            happy_percent = (self.stats['happy_time'] / total_time) * 100
            worried_percent = (self.stats['worried_time'] / total_time) * 100
            critical_percent = (self.stats['critical_time'] / total_time) * 100
            
            stats_text = f"""Session Duration: {self.format_uptime(timedelta(seconds=int(total_time)))}

Mood Distribution:
  😊 Happy: {happy_percent:.1f}% ({self.format_uptime(timedelta(seconds=int(self.stats['happy_time'])))})
  😰 Worried: {worried_percent:.1f}% ({self.format_uptime(timedelta(seconds=int(self.stats['worried_time'])))})
  😵 Critical: {critical_percent:.1f}% ({self.format_uptime(timedelta(seconds=int(self.stats['critical_time'])))})

Peak Usage:
  CPU: {self.stats['max_cpu']:.1f}%
  RAM: {self.stats['max_ram']:.1f}%
  Disk: {self.stats['max_disk']:.1f}%

Current Average:
  CPU: {sum(self.cpu_history)/len(self.cpu_history):.1f}%
  RAM: {sum(self.ram_history)/len(self.ram_history):.1f}%
  Disk: {sum(self.disk_history)/len(self.disk_history):.1f}%
"""
            self.stats_label.configure(text=stats_text)
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        time.sleep(0.5)
        self.root.destroy()

if __name__ == "__main__":
    app = AdvancedSystemPetGUI()
    app.run()
