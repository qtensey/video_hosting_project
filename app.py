from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Налаштування для відео
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Створюємо папку для відео, якщо її немає
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    videos = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith(tuple(ALLOWED_EXTENSIONS))]
    return render_template('main.html', videos=videos)

@app.route('/video/<filename>')
def video_detail(filename):
    return render_template('video_detail.html', video=filename)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    upload_folder = app.config['UPLOAD_FOLDER']

    if request.method == 'POST':
        file = request.files.get('video')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            flash('Відео успішно завантажено!')
            return redirect(url_for('profile'))
        flash('Невірний формат файлу або файл не обрано.')

    video_files = []
    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
            video_files.append({
                'filename': filename,
                'title': os.path.splitext(filename)[0],
                'description': 'Опис відсутній'
            })

    fake_user = {
        'username': 'DemoUser',
        'email': 'demo@example.com',
        'avatar': 'default.gif'
    }

    return render_template('profile.html', videos=video_files, user=fake_user)

@app.route('/delete_video/<filename>', methods=['POST'])
def delete_video(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Відео видалено.')
    else:
        flash('Файл не знайдено.')
    return redirect(url_for('profile'))

@app.route('/trending')
def trending():
    return render_template('trending.html')

@app.route('/subscriptions')
def subscriptions():
    return render_template('subscriptions.html')

@app.route('/library')
def library():
    return render_template('library.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/videohostplus')
def videohostplus():
    return render_template('videohostplus.html')

if __name__ == '__main__':
    app.run(debug=True)
