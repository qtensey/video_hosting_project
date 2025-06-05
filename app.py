from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import os, json
from werkzeug.utils import secure_filename
from models import db, User, Video
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Необхідно для повідомлень flash

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.getcwd(), 'users.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

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
    videos = Video.query.order_by(Video.id.desc()).all()  # або будь-яке сортування
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
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Збереження у базу даних (потрібно імпортувати Video і db)
            new_video = Video(
                filename=filename,
                title=request.form.get('title', filename),
                description=request.form.get('description', ''),
                user_id=current_user.id
            )
            db.session.add(new_video)
            db.session.commit()

    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', videos=videos, user=current_user)



@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['video']
    title = request.form['title']
    description = request.form['description']

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        new_video = Video(
            filename=filename,
            title=title,
            description=description,
            user_id=current_user.id
        )
        db.session.add(new_video)
        db.session.commit()
        flash('Відео успішно завантажено!')
        return redirect(url_for('profile'))

    flash('Помилка завантаження файлу.')
    return redirect(url_for('profile'))


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


@app.route('/delete_video/<int:video_id>', methods=['POST'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        abort(403)  # Заборонити видалення чужих відео

    # Видаляємо файл з диску
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], video.filename))
    except OSError:
        pass

    # Видаляємо з бази
    db.session.delete(video)
    db.session.commit()
    flash('Відео успішно видалено!')
    return redirect(url_for('profile'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Зберігаємо тільки якщо є помилка
        session['reg_username'] = username
        session['reg_email'] = email

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

        # Очистимо сесію після успішної реєстрації
        session.pop('reg_username', None)
        session.pop('reg_email', None)

        flash('Реєстрація успішна. Увійдіть до акаунту.')
        return redirect(url_for('login'))

    return render_template('register.html',
                           username=session.pop('reg_username', ''),
                           email=session.pop('reg_email', ''))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            session['login_email'] = email  # Зберігаємо тимчасово
            flash('Невірний email або пароль.')
            return redirect(url_for('login'))

        login_user(user)
        session.pop('login_email', None)  # Очищаємо після входу
        return redirect(url_for('profile'))

    return render_template('login.html',
                           email=session.pop('login_email', ''))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з акаунта.', 'success')
    return redirect(url_for('login'))


@app.route('/videohostplus')
def videohostplus():
    return render_template('videohostplus.html')



if __name__ == '__main__':
    app.run(debug=True)
