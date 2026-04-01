import os
import sys
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

print("=== Проверка переменных окружения ===")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")

# Пытаемся подключиться к PostgreSQL
try:
    import psycopg2

    print("\n=== Попытка подключения к PostgreSQL ===")
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print("✅ Подключение успешно!")

    # Проверяем версию
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL версия: {version[0]}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")