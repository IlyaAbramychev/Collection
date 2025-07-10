from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PIL import Image
import re

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Для сессий и flash

# Настройка SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, User, Post, Comment, Like, Tag

db.init_app(app)
migrate = Migrate(app, db)

# Пример данных для статей
articles = [
    {'id': 1, 'title': 'Статья 1', 'summary': 'Краткое описание статьи 1'},
    {'id': 2, 'title': 'Статья 2', 'summary': 'Краткое описание статьи 2'},
    {'id': 3, 'title': 'Статья 3', 'summary': 'Краткое описание статьи 3'},
]

@app.route('/')
def index():
    user_id = session.get('user_id')
    # Для каждой тестовой статьи ищем пост с таким id (если есть) и подставляем лайки
    articles_with_likes = []
    for art in articles:
        post = Post.query.filter_by(id=art['id']).first()
        if post:
            likes_count = Like.query.filter_by(post_id=post.id).count()
            liked_by_current = False
            if user_id:
                liked_by_current = Like.query.filter_by(post_id=post.id, user_id=user_id).first() is not None
            art = art.copy()
            art['likes_count'] = likes_count
            art['liked_by_current'] = liked_by_current
        else:
            art = art.copy()
            art['likes_count'] = 0
            art['liked_by_current'] = False
        articles_with_likes.append(art)
    return render_template('index.html', recommended_articles=articles_with_likes[:2], latest_articles=articles_with_likes)

@app.route('/articles')
def articles_page():
    return render_template('articles.html')

@app.route('/reg_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Проверка логина и пароля
        # ...
        return redirect(url_for('index'))
    return render_template('reg_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        status = request.form.get('status', '')
        bio = request.form.get('bio', '')

        # Проверка совпадения паролей
        if password != password2:
            flash('Пароли не совпадают!', 'danger')
            return render_template('reg_login.html', reg_error='Пароли не совпадают!')

        # Проверка уникальности username/email
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!', 'danger')
            return render_template('reg_login.html', reg_error='Пользователь с таким именем уже существует!')
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует!', 'danger')
            return render_template('reg_login.html', reg_error='Пользователь с таким email уже существует!')

        # Хеширование пароля
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash, status=status, bio=bio)
        db.session.add(user)
        db.session.commit()

        # Автоматический вход
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Регистрация успешна! Добро пожаловать.', 'success')
        return redirect(url_for('profile'))
    return render_template('reg_login.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('register'))
    username = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    status = request.form.get('status', '').strip()
    bio = request.form.get('bio', '').strip()
    # Новые поля
    user.full_name = request.form.get('full_name', '').strip()
    user.degree = request.form.get('degree', '').strip()
    user.interests = request.form.get('interests', '').strip()
    user.organization = request.form.get('organization', '').strip()
    user.location = request.form.get('location', '').strip()
    user.scholar_links = request.form.get('scholar_links', '').strip()
    user.website = request.form.get('website', '').strip()
    user.birthdate = request.form.get('birthdate', '').strip()
    user.public_email = request.form.get('public_email', '').strip()
    user.telegram = request.form.get('telegram', '').strip()
    # Проверка уникальности email, если изменился
    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует!', 'danger')
            return redirect(url_for('profile'))
        user.email = email
    # Проверка уникальности username, если изменился
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!', 'danger')
            return redirect(url_for('profile'))
        user.username = username
        session['username'] = username
    user.status = status
    user.bio = bio
    db.session.commit()
    flash('Профиль успешно обновлён!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/avatar', methods=['POST'])
def upload_avatar():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    file = request.files.get('avatar')
    if file and file.filename:
        filename = f'user_{user.id}_avatar.png'
        filepath = os.path.join(app.root_path, 'static', 'avatars', filename)
        # Создать папку avatars, если нет
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Обрезать и уменьшить изображение
        img = Image.open(file)
        img = img.convert('RGB')
        min_side = min(img.size)
        left = (img.width - min_side) // 2
        top = (img.height - min_side) // 2
        img = img.crop((left, top, left + min_side, top + min_side))
        img = img.resize((256, 256))
        img.save(filepath, format='PNG', optimize=True)
        user.avatar = f'avatars/{filename}'
        db.session.commit()
        flash('Аватар обновлён!', 'success')
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта.', 'success')
    return redirect(url_for('reg_login'))

@app.route('/wall', methods=['GET', 'POST'])
def wall():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            post = Post(user_id=user.id, content=content)
            # Парсим теги из текста
            tag_names = set(re.findall(r'#([\wа-яА-ЯёЁ\-]+)', content))
            tags = []
            for name in tag_names:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.session.add(tag)
                tags.append(tag)
            post.tags = tags
            db.session.add(post)
            db.session.commit()
            flash('Пост опубликован!', 'success')
        return redirect(url_for('wall'))
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # Жадная загрузка авторов и комментариев
    for post in posts:
        post.user = User.query.get(post.user_id)
        post.comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
        for comment in post.comments:
            comment.user = User.query.get(comment.user_id)
        post.likes_count = Like.query.filter_by(post_id=post.id).count()
        post.liked_by_current = False
        if user_id:
            post.liked_by_current = Like.query.filter_by(post_id=post.id, user_id=user_id).first() is not None
    return render_template('wall.html', user=user, posts=posts)

@app.route('/wall/comment', methods=['POST'])
def wall_comment():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    post_id = request.form.get('post_id')
    content = request.form.get('content', '').strip()
    if post_id and content:
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')
    return redirect(url_for('wall'))

@app.route('/wall/like', methods=['POST'])
def wall_like():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    post_id = request.form.get('post_id')
    if not post_id:
        return jsonify({'error': 'no_post_id'}), 400
    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        like = Like(user_id=user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        liked = True
    count = Like.query.filter_by(post_id=post_id).count()
    return jsonify({'liked': liked, 'count': count})

@app.route('/wall/delete', methods=['POST'])
def wall_delete():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    post_id = request.form.get('post_id')
    if not post_id:
        return jsonify({'error': 'no_post_id'}), 400
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'not_found'}), 404
    if post.user_id != user_id:
        return jsonify({'error': 'forbidden'}), 403
    # Удаляем комментарии и лайки, связанные с постом
    Comment.query.filter_by(post_id=post.id).delete()
    Like.query.filter_by(post_id=post.id).delete()
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return dict(current_user=user)
    return dict(current_user=None)

@app.template_filter('hashtagify')
def hashtagify(text):
    def repl(match):
        tag = match.group(1)
        return f'<a href="/wall?q=%23{tag}" class="hashtag">#{tag}</a>'
    return re.sub(r'#([\wа-яА-ЯёЁ\-]+)', repl, text)

if __name__ == '__main__':
    app.run(debug=True)