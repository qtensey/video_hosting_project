from app import app, db
import os

# Перевірте поточну директорію
print("Текуща директорія:", os.getcwd())

# Переконайтесь, що база даних може бути створена
with app.app_context():
    try:
        db.create_all()
        print("База даних успішно створена.")
    except Exception as e:
        print(f"Помилка при створенні бази даних: {e}")
