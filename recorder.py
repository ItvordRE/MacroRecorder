import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pynput import mouse, keyboard
import json
import threading
import importlib.util
import os

# Система плагинов
def load_game_plugin(game_name):
    """Загружает плагин для игры"""
    # Пробуем разные варианты путей
    possible_paths = [
        f"plugins/{game_name}.py",
        f"plugins/{game_name.lower()}.py",
        f"{game_name}.py"
    ]
    
    for plugin_path in possible_paths:
        if os.path.exists(plugin_path):
            try:
                spec = importlib.util.spec_from_file_location(game_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            except Exception as e:
                print(f"Ошибка загрузки плагина {plugin_path}: {e}")
                return None
    return None

# Плагины (можно вынести в отдельные файлы)
class BasePlugin:
    """Базовый класс плагина"""
    def get_game_specific_keys(self):
        return {}
    
    def get_default_coords(self):
        return {}
    
    def get_macro_presets(self):
        return []
    
    def pre_process_event(self, event):
        """Предобработка события перед записью"""
        return event
    
    def post_process_event(self, event):
        """Постобработка события перед воспроизведением"""
        return event

class CS2Plugin(BasePlugin):
    def get_game_specific_keys(self):
        return {
            'shoot': 'left_click',
            'reload': 'r',
            'jump': 'space',
            'crouch': 'ctrl',
            'sprint': 'shift',
            'knife': '1',
            'pistol': '2',
            'primary': '3',
            'use': 'e',
            'inspect': 'f'
        }
    
    def get_default_coords(self):
        return {
            'buy_menu': (960, 540),
            'defuse_kit': (100, 100),
            'map_center': (960, 540),
            'radar': (1750, 150)
        }
    
    def get_macro_presets(self):
        return [
            {
                'name': 'Быстрая покупка AK47',
                'actions': [
                    {'type': 'key_press', 'key': 'b', 'time': 0.1},
                    {'type': 'click', 'x': 800, 'y': 400, 'button': 'left', 'time': 0.2},
                    {'type': 'click', 'x': 900, 'y': 300, 'button': 'left', 'time': 0.3}
                ]
            },
            {
                'name': 'Быстрое переключение оружия',
                'actions': [
                    {'type': 'key_press', 'key': '1', 'time': 0.1},
                    {'type': 'key_press', 'key': '2', 'time': 0.2},
                    {'type': 'key_press', 'key': '3', 'time': 0.3}
                ]
            }
        ]

class Dota2Plugin(BasePlugin):
    def get_game_specific_keys(self):
        return {
            'attack': 'a',
            'move': 's',
            'cast_q': 'q',
            'cast_w': 'w',
            'cast_e': 'e',
            'cast_r': 'r',
            'item_1': 'd',
            'item_2': 'f',
            'item_3': 'g',
            'item_4': 'z',
            'item_5': 'x',
            'item_6': 'c'
        }
    
    def get_macro_presets(self):
        return [
            {
                'name': 'Комбо Q-W-E',
                'actions': [
                    {'type': 'key_press', 'key': 'q', 'time': 0.1},
                    {'type': 'key_press', 'key': 'w', 'time': 0.3},
                    {'type': 'key_press', 'key': 'e', 'time': 0.5}
                ]
            },
            {
                'name': 'Использование всех предметов',
                'actions': [
                    {'type': 'key_press', 'key': 'd', 'time': 0.1},
                    {'type': 'key_press', 'key': 'f', 'time': 0.2},
                    {'type': 'key_press', 'key': 'g', 'time': 0.3}
                ]
            }
        ]

class OSUPlugin(BasePlugin):
    def get_game_specific_keys(self):
        return {
            'click_left': 'z',
            'click_right': 'x',
            'smoke': 'c',
            'skip': 'space'
        }
    
    def get_macro_presets(self):
        return [
            {
                'name': 'Быстрое кликание',
                'actions': [
                    {'type': 'key_press', 'key': 'z', 'time': 0.05},
                    {'type': 'key_press', 'key': 'x', 'time': 0.1},
                    {'type': 'key_press', 'key': 'z', 'time': 0.15},
                    {'type': 'key_press', 'key': 'x', 'time': 0.2}
                ]
            }
        ]

class BladeSoulPlugin(BasePlugin):
    def get_game_specific_keys(self):
        return {
            'attack_1': '1',
            'attack_2': '2',
            'attack_3': '3',
            'attack_4': '4',
            'dodge': 'f',
            'block': 'q',
            'special': 'r'
        }
    
    def get_macro_presets(self):
        return [
            {
                'name': 'Базовый комбо атаки',
                'actions': [
                    {'type': 'key_press', 'key': '1', 'time': 0.1},
                    {'type': 'key_press', 'key': '2', 'time': 0.3},
                    {'type': 'key_press', 'key': '3', 'time': 0.5},
                    {'type': 'key_press', 'key': '4', 'time': 0.7}
                ]
            }
        ]

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Recorder with Plugins")
        self.root.geometry("750x650")
        
        self.events = []
        self.recording = False
        self.playing = False
        self.stop_playback_flag = False
        self.loop_macro = False
        self.current_plugin = None
        
        # Регистрируем плагины
        self.plugins = {
            "Обычный режим": BasePlugin(),
            "CS2": CS2Plugin(),
            "Dota 2": Dota2Plugin(),
            "OSU!": OSUPlugin(),
            "Blade&Soul": BladeSoulPlugin()
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Macro Recorder with Plugins", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Game selection
        game_frame = ttk.LabelFrame(main_frame, text="Выбор игры", padding="10")
        game_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(game_frame, text="Игра:").grid(row=0, column=0, sticky=tk.W)
        
        self.game_var = tk.StringVar(value="Обычный режим")
        game_combo = ttk.Combobox(game_frame, textvariable=self.game_var, 
                                 values=list(self.plugins.keys()), state="readonly")
        game_combo.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        game_combo.bind('<<ComboboxSelected>>', self.on_game_selected)
        
        # Plugin info
        self.plugin_info_var = tk.StringVar(value="Режим: Обычный")
        ttk.Label(game_frame, textvariable=self.plugin_info_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        game_frame.columnconfigure(1, weight=1)
        
        # Preset macros
        preset_frame = ttk.LabelFrame(main_frame, text="Готовые макросы", padding="10")
        preset_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, state="readonly")
        self.preset_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.load_preset_btn = ttk.Button(preset_frame, text="Загрузить макрос", 
                                        command=self.load_preset, state=tk.DISABLED)
        self.load_preset_btn.grid(row=0, column=1)
        
        preset_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 20))
        
        self.record_btn = ttk.Button(button_frame, text="Начать запись", 
                                   command=self.toggle_recording)
        self.record_btn.grid(row=0, column=0, padx=5)
        
        self.play_btn = ttk.Button(button_frame, text="Воспроизвести", 
                                 command=self.play_recording, state=tk.DISABLED)
        self.play_btn.grid(row=0, column=1, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Стоп", 
                                 command=self.stop_playback, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Очистить", 
                                  command=self.clear_events)
        self.clear_btn.grid(row=0, column=3, padx=5)
        
        # Additional controls frame
        additional_frame = ttk.Frame(main_frame)
        additional_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        # Loop checkbox
        self.loop_var = tk.BooleanVar()
        self.loop_check = ttk.Checkbutton(additional_frame, text="Зациклить макрос", 
                                        variable=self.loop_var)
        self.loop_check.grid(row=0, column=0, padx=5)
        
        # Save macro button
        self.save_macro_btn = ttk.Button(additional_frame, text="Сохранить макрос", 
                                       command=self.save_macro, state=tk.DISABLED)
        self.save_macro_btn.grid(row=0, column=1, padx=5)
        
        # Load macro button
        self.load_macro_btn = ttk.Button(additional_frame, text="Загрузить макрос", 
                                       command=self.load_macro)
        self.load_macro_btn.grid(row=0, column=2, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Статус", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                     font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Events info
        info_frame = ttk.LabelFrame(main_frame, text="Информация о записи", padding="10")
        info_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.events_count_var = tk.StringVar(value="Записанных событий: 0")
        ttk.Label(info_frame, textvariable=self.events_count_var).grid(row=0, column=0, sticky=tk.W)
        
        self.duration_var = tk.StringVar(value="Длительность: 0.0 сек")
        ttk.Label(info_frame, textvariable=self.duration_var).grid(row=1, column=0, sticky=tk.W)
        
        # Events log
        log_frame = ttk.LabelFrame(main_frame, text="Лог событий", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=60)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        
        # Start mouse listener for continuous updates
        self.setup_listeners()
        
        # Load initial plugin
        self.on_game_selected()
        
    def setup_listeners(self):
        """Setup mouse listener for cursor position updates"""
        def on_move(x, y):
            if hasattr(self, 'last_move_time'):
                if time.time() - self.last_move_time > 0.1:
                    self.root.after(0, lambda: self.status_var.set(f"Курсор: X={x}, Y={y}"))
                    self.last_move_time = time.time()
            else:
                self.last_move_time = time.time()
        
        self.mouse_listener = mouse.Listener(on_move=on_move)
        self.mouse_listener.start()
        
    def on_game_selected(self, event=None):
        """Обработчик выбора игры"""
        game_name = self.game_var.get()
        
        # Пробуем загрузить внешний плагин
        if game_name != "Обычный режим":
            plugin_name = game_name.lower().replace(" ", "").replace("&", "").replace("!", "")
            external_plugin = load_game_plugin(plugin_name)
            if external_plugin:
                # Создаем экземпляр плагина на основе внешнего модуля
                class DynamicPlugin(BasePlugin):
                    def get_game_specific_keys(self):
                        return getattr(external_plugin, 'get_game_specific_keys', lambda: {})()
                    
                    def get_default_coords(self):
                        return getattr(external_plugin, 'get_default_coords', lambda: {})()
                    
                    def get_macro_presets(self):
                        return getattr(external_plugin, 'get_macro_presets', lambda: [])()
                
                self.current_plugin = DynamicPlugin()
                self.log_message(f"Загружен внешний плагин для {game_name}")
            else:
                # Используем встроенный плагин
                self.current_plugin = self.plugins.get(game_name, BasePlugin())
                self.log_message(f"Загружен встроенный плагин для {game_name}")
        else:
            self.current_plugin = self.plugins["Обычный режим"]
            self.log_message("Режим: Обычный")
        
        # Обновляем информацию о плагине
        if self.current_plugin:
            keys = self.current_plugin.get_game_specific_keys()
            presets = self.current_plugin.get_macro_presets()
            self.plugin_info_var.set(f"Режим: {game_name} | Клавиши: {len(keys)} | Макросы: {len(presets)}")
            
            # Обновляем список пресетов
            preset_names = [p['name'] for p in presets]
            self.preset_combo['values'] = preset_names
            if preset_names:
                self.preset_combo.set(preset_names[0])
                self.load_preset_btn.config(state=tk.NORMAL)
            else:
                self.preset_combo.set('')
                self.load_preset_btn.config(state=tk.DISABLED)
        
    def load_preset(self):
        """Загружает выбранный пресет-макрос"""
        if not self.current_plugin:
            return
            
        preset_name = self.preset_var.get()
        presets = self.current_plugin.get_macro_presets()
        
        preset = next((p for p in presets if p['name'] == preset_name), None)
        if preset:
            self.events = preset['actions']
            self.update_info()
            self.log_message(f"Загружен макрос: {preset_name}")
            self.log_message(f"Действий: {len(self.events)}")
        else:
            messagebox.showwarning("Предупреждение", "Макрос не найден")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_info(self):
        """Update events information"""
        count = len(self.events)
        self.events_count_var.set(f"Записанных событий: {count}")
        
        if count > 1:
            # Для пресетов используем относительное время
            if count > 0 and 'time' in self.events[0]:
                duration = max(event.get('time', 0) for event in self.events)
            else:
                duration = count * 0.5  # Примерная длительность
            self.duration_var.set(f"Длительность: {duration:.1f} сек")
        else:
            self.duration_var.set("Длительность: 0.0 сек")
            
        # Enable/disable play button
        if count > 0 and not self.recording:
            self.play_btn.config(state=tk.NORMAL)
            self.save_macro_btn.config(state=tk.NORMAL)
        else:
            self.play_btn.config(state=tk.DISABLED)
            if count == 0:
                self.save_macro_btn.config(state=tk.DISABLED)
    
    def toggle_recording(self):
        """Start or stop recording"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording events"""
        self.recording = True
        self.events.clear()
        self.record_btn.config(text="Остановить запись")
        self.play_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_macro_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Запись... Нажмите 'Esc' или 'q' для остановки")
        
        self.log_message("Начало записи")
        
        # Start listeners in separate threads
        self.mouse_listener_record = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        self.mouse_listener_record.start()
        self.keyboard_listener.start()
        
        # Update UI periodically
        self.update_ui_during_recording()
    
    def stop_recording(self):
        """Stop recording events"""
        self.recording = False
        self.record_btn.config(text="Начать запись")
        self.progress.stop()
        self.status_var.set("Запись остановлена")
        
        if hasattr(self, 'mouse_listener_record') and self.mouse_listener_record.is_alive():
            self.mouse_listener_record.stop()
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            
        self.save_events()
        self.update_info()
        self.log_message(f"Запись остановлена. Событий: {len(self.events)}")
    
    def update_ui_during_recording(self):
        """Update UI during recording"""
        if self.recording:
            count = len(self.events)
            self.status_var.set(f"Запись... Событий: {count}. Нажмите 'Esc' или 'q' для остановки")
            self.root.after(100, self.update_ui_during_recording)
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse clicks"""
        if pressed and self.recording:
            event = {
                'type': 'click',
                'x': x,
                'y': y,
                'button': button.name,
                'time': time.time()
            }
            
            # Обработка плагином
            if self.current_plugin:
                event = self.current_plugin.pre_process_event(event)
            
            self.events.append(event)
            self.log_message(f"Клик: ({x}, {y}) {button.name}")
            self.update_info()
    
    def on_press(self, key):
        """Handle keyboard presses"""
        try:
            if key.char == 'q':  # Stop recording with 'q'
                self.root.after(0, self.stop_recording)
                return False
        except AttributeError:
            if key == keyboard.Key.esc:  # Stop recording with Esc
                self.root.after(0, self.stop_recording)
                return False
        
        # Record key press
        if self.recording:
            try:
                key_char = key.char
            except AttributeError:
                key_char = str(key)
            
            event = {
                'type': 'key_press',
                'key': key_char,
                'time': time.time()
            }
            
            # Обработка плагином
            if self.current_plugin:
                event = self.current_plugin.pre_process_event(event)
            
            self.events.append(event)
            self.log_message(f"Клавиша: {key_char}")
            self.update_info()
    
    def save_events(self):
        """Save events to file"""
        try:
            with open('recording.json', 'w', encoding='utf-8') as f:
                json.dump(self.events, f, indent=2, ensure_ascii=False)
            self.log_message("События сохранены в recording.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def save_macro(self):
        """Save current macro to a file"""
        if not self.events:
            messagebox.showwarning("Предупреждение", "Нет событий для сохранения")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить макрос"
        )
        
        if filename:
            try:
                # Добавляем метаданные о макросе
                macro_data = {
                    'name': os.path.basename(filename),
                    'game': self.game_var.get(),
                    'created': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'events_count': len(self.events),
                    'actions': self.events
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(macro_data, f, indent=2, ensure_ascii=False)
                
                self.log_message(f"Макрос сохранен в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_macro(self):
        """Load macro from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить макрос"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    macro_data = json.load(f)
                
                # Проверяем формат файла
                if 'actions' in macro_data:
                    self.events = macro_data['actions']
                    self.update_info()
                    self.log_message(f"Загружен макрос из {filename}")
                    self.log_message(f"Действий: {len(self.events)}")
                    
                    # Если в файле есть информация о игре, пытаемся переключиться
                    if 'game' in macro_data:
                        game_name = macro_data['game']
                        if game_name in self.plugins:
                            self.game_var.set(game_name)
                            self.on_game_selected()
                else:
                    messagebox.showerror("Ошибка", "Неверный формат файла макроса")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def play_recording(self):
        """Play recorded events in separate thread"""
        if self.playing or len(self.events) == 0:
            return
            
        self.playing = True
        self.stop_playback_flag = False
        self.record_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set("Воспроизведение...")
        
        # Run playback in separate thread
        thread = threading.Thread(target=self._playback_thread)
        thread.daemon = True
        thread.start()
    
    def stop_playback(self):
        """Stop playback"""
        self.stop_playback_flag = True
        self.status_var.set("Остановка воспроизведения...")
    
    def _playback_thread(self):
        """Playback thread function"""
        try:
            mouse_ctrl = mouse.Controller()
            keyboard_ctrl = keyboard.Controller()
            
            # Запоминаем начальную позицию мыши для восстановления
            initial_pos = mouse_ctrl.position
            
            # Цикл воспроизведения
            loop_count = 0
            while not self.stop_playback_flag and (self.loop_var.get() or loop_count == 0):
                if loop_count > 0:
                    self.root.after(0, lambda: self.log_message(f"Повтор макроса (цикл {loop_count + 1})"))
                
                # Определяем начальное время
                if self.events and 'time' in self.events[0]:
                    # Для записанных событий
                    start_time = self.events[0]['time']
                else:
                    # Для пресетов
                    start_time = time.time()
                
                for i, event in enumerate(self.events):
                    # Проверяем флаг остановки
                    if self.stop_playback_flag:
                        break
                    
                    # Обработка плагином
                    if self.current_plugin:
                        event = self.current_plugin.post_process_event(event)
                    
                    # Calculate delay
                    if 'time' in event:
                        if i == 0:
                            delay = 0
                        else:
                            delay = event['time'] - start_time
                            if delay < 0:
                                delay = 0
                    else:
                        # Для пресетов без времени - фиксированная задержка
                        delay = 0.5
                    
                    if i > 0:
                        # Разбиваем задержку на небольшие интервалы для возможности прерывания
                        sleep_interval = 0.1
                        while delay > 0 and not self.stop_playback_flag:
                            if delay > sleep_interval:
                                time.sleep(sleep_interval)
                                delay -= sleep_interval
                            else:
                                time.sleep(delay)
                                break
                    
                    # Проверяем флаг остановки снова после задержки
                    if self.stop_playback_flag:
                        break
                    
                    # Execute event
                    if event['type'] == 'click':
                        self.root.after(0, lambda e=event: self.log_message(f"Воспроизведение: клик ({e['x']}, {e['y']})"))
                        mouse_ctrl.position = (event['x'], event['y'])
                        mouse_ctrl.click(mouse.Button[event['button']])
                    
                    elif event['type'] == 'key_press':
                        self.root.after(0, lambda e=event: self.log_message(f"Воспроизведение: клавиша {e['key']}"))
                        if 'Key.' in event['key']:
                            key_name = event['key'].replace('Key.', '')
                            key_obj = getattr(keyboard.Key, key_name, None)
                            if key_obj:
                                keyboard_ctrl.press(key_obj)
                                keyboard_ctrl.release(key_obj)
                        else:
                            keyboard_ctrl.type(event['key'])
                
                loop_count += 1
                
                # Если не зациклено, выходим из цикла
                if not self.loop_var.get():
                    break
            
            # Восстанавливаем позицию мыши
            if not self.stop_playback_flag:
                mouse_ctrl.position = initial_pos
            
            # Update UI after playback
            self.root.after(0, self._playback_finished)
            
        except Exception as e:
            self.root.after(0, lambda: self._playback_error(str(e)))
    
    def _playback_finished(self):
        """Called when playback finishes successfully"""
        self.playing = False
        self.record_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        
        if self.stop_playback_flag:
            self.status_var.set("Воспроизведение остановлено")
            self.log_message("Воспроизведение остановлено пользователем")
        else:
            self.status_var.set("Воспроизведение завершено")
            self.log_message("Воспроизведение завершено")
    
    def _playback_error(self, error_msg):
        """Called when playback encounters an error"""
        self.playing = False
        self.record_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Ошибка воспроизведения")
        messagebox.showerror("Ошибка", f"Ошибка при воспроизведении: {error_msg}")
        self.log_message(f"Ошибка воспроизведения: {error_msg}")
    
    def clear_events(self):
        """Clear all recorded events"""
        if self.recording or self.playing:
            messagebox.showwarning("Предупреждение", "Невозможно очистить во время записи или воспроизведения")
            return
            
        if messagebox.askyesno("Подтверждение", "Очистить все записанные события?"):
            self.events.clear()
            self.update_info()
            self.log_text.delete(1.0, tk.END)
            self.log_message("Все события очищены")
    
    def on_closing(self):
        """Handle application closing"""
        self.stop_playback_flag = True  # Останавливаем воспроизведение если активно
        
        if self.recording:
            self.stop_recording()
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RecorderApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()

if __name__ == "__main__":
    main()