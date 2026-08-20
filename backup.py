"""
Скрипт для создания резервной копии базы данных.

Запуск: python backup.py
"""

import os
import subprocess
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
filename = f'backups/backup_{timestamp}.sql'

command = [
    'pg_dump',
    '-U', DB_USER,
    '-d', DB_NAME,
    '-f', filename
]

subprocess.run(command, check=True)
print(f'Резервная копия создана: {filename}')
