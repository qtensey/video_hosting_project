from flask import Flask, render_template, request, redirect, url_for, flash, session
import os, json
from werkzeug.utils import secure_filename
from models import db, User
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Необхідно для повідомлень flash

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.getcwd(), 'users.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

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
@login_required
def profile():
    if request.method == 'POST':
        file = request.files.get('video')
        if file and file.filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
    videos = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('profile.html', videos=videos, user=current_user)


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
            return redirect(url_for('main'))
        else:
            flash('Неприпустимий тип файлу', 'error')
            return redirect(request.url)
    return render_template('upload.html')


@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
 
    file = request.files['avatar']

    if file:
        filename = secure_filename(file.filename)
        avatar_path = os.path.join('static', 'avatars', filename)
        file.save(avatar_path)

        # Видалення старої аватарки, якщо не за замовчуванням
        old_avatar = current_user.avatar
        if old_avatar != 'default.jpg':
            old_path = os.path.join('static', 'avatars', old_avatar)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Оновлення в базі
        current_user.avatar = filename
        db.session.commit()
    return redirect(url_for('profile'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Зберігаємо поля у сесії, якщо буде помилка
        session['username'] = username
        session['email'] = email

        if password != confirm_password:
            flash("Паролі не співпадають.")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Користувач з таким email вже існує.')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Очистимо збережені дані
        session.pop('username', None)
        session.pop('email', None)

        flash('Реєстрація успішна. Увійдіть до акаунту.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_video(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
            flash('Відео успішно видалено', 'success')
        else:
            flash('Файл не знайдено', 'error')
    except Exception as e:
        flash(f'Помилка при видаленні: {str(e)}', 'error')
    return redirect(url_for('profile'))  # або 'main', залежно куди треба повернути


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['email'] = email  # Зберігаємо email на випадок помилки

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Невірний email або пароль.')
            return redirect(url_for('login'))

        login_user(user)
        session.pop('email', None)  # Очищаємо email після успішного входу
        return redirect(url_for('profile'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з акаунта.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
