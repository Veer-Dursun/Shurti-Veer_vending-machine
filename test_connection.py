import psycopg2
from decouple import config

try:
    conn = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        sslmode='require'
    )
    print("✅ SUCCESS! Connected to DigitalOcean database!")
    conn.close()
except Exception as e:
    print(f"❌ FAILED: {e}")