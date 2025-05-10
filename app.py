from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Необхідно для повідомлень flash

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Створити папку, якщо її немає
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    videos = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('main.html', videos=videos)


@app.route('/video/<filename>')
def video_detail(filename):
    return render_template('video_detail.html', video=filename)


@app.route('/trending')
def trending():
    return render_template('trending.html')  # Створіть відповідний шаблон

@app.route('/subscriptions')
def subscriptions():
    return render_template('subscriptions.html')  # Створіть відповідний шаблон

@app.route('/library')
def library():
    return render_template('library.html')  # Створіть відповідний шаблон

@app.route('/history')
def history():
    return render_template('history.html')  # Створіть відповідний шаблон


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Для тесту
    user = {'name': 'John Doe', 'email': 'john@example.com'}

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        # Збереження або обробка даних
        print(f"Оновлено: {username}, {email}")
    
    return render_template('profile.html', user=user)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('Файл не знайдено у запиті', 'error')
            return redirect(request.url)
        file = request.files['video']
        if file.filename == '':
            flash('Файл не обрано', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            flash('Файл успішно завантажено', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неприпустимий тип файлу', 'error')
            return redirect(request.url)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
