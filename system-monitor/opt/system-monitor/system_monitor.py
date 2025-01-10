import tkinter as tk
import psutil
import sqlite3
from datetime import datetime
import os


class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.geometry("400x350")

        # Установка начального интервала обновления (1 секунда)
        self.update_interval = 1000  # в миллисекундах
        self.is_recording = False  # Флаг для отслеживания состояния записи
        self.start_time = None  # Время начала записи

        # Указываем путь к файлу базы данных в домашней директории
        home_dir = os.path.expanduser("~")
        self.db_path = os.path.join(home_dir, "system_monitor.db")

        # Подключение к базе данных
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

        # Создание и размещение виджетов
        self.cpu_label = tk.Label(root, text="Загруженность ЦП: N/A", font=("Arial", 12))
        self.cpu_label.pack(pady=10)

        self.ram_label = tk.Label(root, text="Загруженность ОЗУ: N/A", font=("Arial", 12))
        self.ram_label.pack(pady=10)

        self.disk_label = tk.Label(root, text="Загруженность ПЗУ: N/A", font=("Arial", 12))
        self.disk_label.pack(pady=10)

        # Поле ввода для интервала обновления
        self.interval_frame = tk.Frame(root)
        self.interval_frame.pack(pady=10)

        self.interval_label = tk.Label(self.interval_frame, text="Интервал обновления (ms):", font=("Arial", 10))
        self.interval_label.pack(side=tk.LEFT)

        self.interval_entry = tk.Entry(self.interval_frame, width=10)
        self.interval_entry.insert(0, str(self.update_interval))
        self.interval_entry.pack(side=tk.LEFT, padx=5)

        self.apply_button = tk.Button(self.interval_frame, text="Применить", command=self.apply_interval)
        self.apply_button.pack(side=tk.LEFT)

        # Кнопка "Начать запись" / "Остановить"
        self.record_button = tk.Button(root, text="Начать запись", command=self.toggle_recording)
        self.record_button.pack(pady=10)

        # Таймер
        self.timer_label = tk.Label(root, text="00:00", font=("Arial", 14))
        self.timer_label.pack(pady=10)

        # Подключение к базе данных SQLite
        self.conn = sqlite3.connect('../../system_monitor.db')
        self.create_table()

        # Запуск обновления информации
        self.update_system_info()

    def create_table(self):
        """Создание таблицы в базе данных, если она не существует."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL
            )
        ''')
        self.conn.commit()

    def insert_metrics(self, cpu_usage, ram_usage, disk_usage):
        """Вставка данных в базу данных."""
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO system_metrics (timestamp, cpu_usage, ram_usage, disk_usage)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, cpu_usage, ram_usage, disk_usage))
        self.conn.commit()

    def update_system_info(self):
        # Получение информации о загруженности ЦП
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_label.config(text=f"Загруженность ЦП: {cpu_percent}%")

        # Получение информации о загруженности ОЗУ
        ram_info = psutil.virtual_memory()
        ram_percent = ram_info.percent
        self.ram_label.config(text=f"Загруженность ОЗУ: {ram_percent}%")

        # Получение информации о загруженности ПЗУ (диска)
        disk_info = psutil.disk_usage('/')
        disk_percent = disk_info.percent
        self.disk_label.config(text=f"Загруженность ПЗУ: {disk_percent}%")

        # Если запись активна, сохраняем данные в базу данных
        if self.is_recording:
            self.insert_metrics(cpu_percent, ram_percent, disk_percent)

        # Планирование следующего обновления
        self.root.after(self.update_interval, self.update_system_info)

    def apply_interval(self):
        # Применение нового интервала обновления
        try:
            new_interval = int(self.interval_entry.get())
            if new_interval < 1000:
                raise ValueError("Интервал должен быть не менее 1000 мс (1 секунды).")
            self.update_interval = new_interval
        except ValueError as e:
            print(f"Неверный интервал: {e}")

    def toggle_recording(self):
        """Переключение состояния записи."""
        if not self.is_recording:
            # Начало записи
            self.is_recording = True
            self.record_button.config(text="Остановить")
            self.start_time = datetime.now()
            self.update_timer()
        else:
            # Остановка записи
            self.is_recording = False
            self.record_button.config(text="Начать запись")
            self.timer_label.config(text="00:00")

    def update_timer(self):
        """Обновление таймера."""
        if self.is_recording:
            elapsed_time = datetime.now() - self.start_time
            elapsed_seconds = int(elapsed_time.total_seconds())
            minutes, seconds = divmod(elapsed_seconds, 60)
            self.timer_label.config(text=f"{minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def __del__(self):
        """Закрытие соединения с базой данных при завершении работы."""
        self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()
