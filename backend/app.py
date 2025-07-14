from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Post, Comment, Like, Tag, CommentLike
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PIL import Image
import re
import time
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Для сессий и flash

# Настройка SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, User, Post, Comment, Like, Tag

db.init_app(app)
migrate = Migrate(app, db)

# Middleware для обновления онлайн статуса
@app.before_request
def update_online_status():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user.last_seen = datetime.utcnow()
            user.is_online = True
            db.session.commit()

# Функция для определения онлайн статуса (онлайн если активность была менее 5 минут назад)
def is_user_online(user):
    if not user or not user.last_seen:
        return False
    return (datetime.utcnow() - user.last_seen).total_seconds() < 300  # 5 минут

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
    # --- feed block ---
    posts = Post.query.order_by(Post.created_at.desc()).all()
    for post in posts:
        post.user = User.query.get(post.user_id)
        post.comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
        for comment in post.comments:
            comment.user = User.query.get(comment.user_id)
        post.likes_count = Like.query.filter_by(post_id=post.id).count()
        post.liked_by_current = False
        if user_id:
            post.liked_by_current = Like.query.filter_by(post_id=post.id, user_id=user_id).first() is not None
    
    # Получаем уникальных активных пользователей
    seen_users = set()
    active_users = []
    for post in posts:
        if post.user.id not in seen_users:
            seen_users.add(post.user.id)
            active_users.append(post.user)
    
    return render_template('index.html', 
                         recommended_articles=articles_with_likes[:2], 
                         latest_articles=articles_with_likes, 
                         posts=posts,
                         active_users=active_users)

@app.route('/articles')
def articles_page():
    return render_template('articles.html')

@app.route('/reg_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
            return render_template('reg_login.html')
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
        email_error = None
        username_error = None
        # Проверка совпадения паролей
        if password != password2:
            flash('Пароли не совпадают!', 'danger')
            print('DEBUG: Пароли не совпадают')
            return render_template('reg_login.html', reg_username=username, reg_email=email, show_register_tab=True)
        # Проверка уникальности username/email
        if User.query.filter_by(username=username).first():
            username_error = 'Пользователь с таким именем уже существует!'
        if User.query.filter_by(email=email).first():
            email_error = 'Пользователь с таким email уже существует!'
        if username_error or email_error:
            print('DEBUG: Ошибка регистрации:', username_error, email_error)
            return render_template('reg_login.html', username_error=username_error, email_error=email_error, reg_username=username, reg_email=email, show_register_tab=True)
        # Хеширование пароля
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash, status=status, bio=bio)
        db.session.add(user)
        db.session.commit()
        print('DEBUG: User created:', user.id, user.username)
        # Автоматический вход
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Регистрация успешна! Добро пожаловать.', 'success')
        print('SESSION AFTER REGISTER:', dict(session))
        return redirect(url_for('profile'))
    print('DEBUG: GET /register')
    return render_template('reg_login.html')

@app.route('/profile')
def profile():
    print('SESSION ON PROFILE:', dict(session))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    
    # Получаем подписчиков и подписки
    followers = list(user.followers)
    following = list(user.following)
    
    # Получаем посты пользователя
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(10).all()
    
    return render_template('profile.html', 
                         user=user, 
                         followers=followers, 
                         following=following,
                         user_posts=user_posts,
                         followers_count=len(followers),
                         following_count=len(following))

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

    # Флаги видимости (чекбоксы)
    user.show_status = 'show_status' in request.form
    user.show_bio = 'show_bio' in request.form
    user.show_full_name = 'show_full_name' in request.form
    user.show_degree = 'show_degree' in request.form
    user.show_interests = 'show_interests' in request.form
    user.show_organization = 'show_organization' in request.form
    user.show_location = 'show_location' in request.form
    user.show_scholar_links = 'show_scholar_links' in request.form
    user.show_website = 'show_website' in request.form
    user.show_birthdate = 'show_birthdate' in request.form
    user.show_public_email = 'show_public_email' in request.form
    user.show_telegram = 'show_telegram' in request.form

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
    return redirect(url_for('login'))

@app.route('/wall', methods=['GET', 'POST'])
def wall():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        image = request.files.get('image')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        image_path = None
        if image and image.filename:
            # Сохраняем изображение в static/uploads/
            upload_dir = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filename = f'post_{user.id}_{int(time.time())}_{image.filename}'
            filepath = os.path.join(upload_dir, filename)
            image.save(filepath)
            image_path = f'uploads/{filename}'
        if content:
            post = Post(user_id=user.id, content=content)
            if image_path:
                post.image_path = image_path
            # Координаты
            try:
                if latitude:
                    post.latitude = float(latitude)
                if longitude:
                    post.longitude = float(longitude)
            except ValueError:
                pass
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
    
    # Получаем только посты текущего пользователя
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    
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
    
    return render_template('wall.html', user=user, posts=posts, is_global_wall=False, target_user=user)

@app.route('/wall/comment', methods=['POST'])
def wall_comment():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    post_id = request.form.get('post_id')
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id')
    if parent_id:
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            parent_id = None
    if post_id and content:
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        if parent_id:
            comment.parent_id = parent_id
        db.session.add(comment)
        db.session.commit()
        # Для AJAX: возвращаем данные нового комментария
        return jsonify({
            'id': comment.id,
            'post_id': comment.post_id,
            'user_id': comment.user_id,
            'content': comment.content,
            'parent_id': comment.parent_id,
            'created_at': comment.created_at.isoformat(),
            'user': {
                'id': comment.user.id,
                'username': comment.user.username,
                'full_name': comment.user.full_name,
                'avatar': comment.user.avatar,
                'degree': comment.user.degree
            },
            'likes_count': 0,
            'liked_by_current': False
        })
    return jsonify({'error': 'invalid_data'}), 400

@app.route('/wall/comment/like', methods=['POST'])
def wall_comment_like():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    comment_id = request.form.get('comment_id')
    if comment_id:
        try:
            comment_id = int(comment_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'invalid_comment_id'}), 400
    like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        like = CommentLike(user_id=user_id, comment_id=comment_id)
        db.session.add(like)
        db.session.commit()
        liked = True
    count = CommentLike.query.filter_by(comment_id=comment_id).count()
    return jsonify({'liked': liked, 'count': count})

@app.route('/wall/comment/edit', methods=['POST'])
def wall_comment_edit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    comment_id = request.form.get('comment_id')
    if not comment_id:
        return jsonify({'error': 'no_comment_id'}), 400
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'not_found'}), 404
    if comment.user_id != user_id:
        return jsonify({'error': 'forbidden'}), 403
    content = request.form.get('content', '').strip()
    if not content:
        return jsonify({'error': 'empty_content'}), 400
    comment.content = content
    db.session.commit()
    return jsonify({'success': True, 'content': comment.content})

@app.route('/wall/comment/delete', methods=['POST'])
def wall_comment_delete():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    comment_id = request.form.get('comment_id')
    if not comment_id:
        return jsonify({'error': 'no_comment_id'}), 400
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'not_found'}), 404
    if comment.user_id != user_id:
        return jsonify({'error': 'forbidden'}), 403
    # Удаляем все подкомментарии рекурсивно
    def delete_with_replies(c):
        for reply in c.replies:
            delete_with_replies(reply)
        db.session.delete(c)
    delete_with_replies(comment)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/wall/comments', methods=['GET'])
def wall_get_comments():
    user_id = session.get('user_id')
    post_id = request.args.get('post_id')
    if not post_id:
        return jsonify({'error': 'no_post_id'}), 400
    try:
        post_id = int(post_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid_post_id'}), 400
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    # Собираем дерево комментариев
    comment_dict = {c.id: c for c in comments}
    tree = []
    for comment in comments:
        # Подсчёт лайков и статус для текущего пользователя
        likes_count = CommentLike.query.filter_by(comment_id=comment.id).count()
        liked_by_current = False
        if user_id:
            liked_by_current = CommentLike.query.filter_by(comment_id=comment.id, user_id=user_id).first() is not None
        comment._json = {
            'id': comment.id,
            'post_id': comment.post_id,
            'user_id': comment.user_id,
            'content': comment.content,
            'parent_id': comment.parent_id,
            'created_at': comment.created_at.isoformat(),
            'user': {
                'id': comment.user.id,
                'username': comment.user.username,
                'full_name': comment.user.full_name,
                'avatar': comment.user.avatar,
                'degree': comment.user.degree
            },
            'likes_count': likes_count,
            'liked_by_current': liked_by_current,
            'replies': []
        }
    # Формируем дерево
    for comment in comments:
        if comment.parent_id and comment.parent_id in comment_dict:
            comment_dict[comment.parent_id]._json['replies'].append(comment._json)
        else:
            tree.append(comment._json)
    return jsonify(tree)

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

@app.route('/wall/edit', methods=['POST'])
def wall_edit():
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
    # Обновление текста
    content = request.form.get('content', '').strip()
    if content:
        post.content = content
    # Обработка картинки
    image = request.files.get('image')
    remove_image = request.form.get('remove_image') == '1'
    if remove_image and post.image_path:
        # Удалить старую картинку
        try:
            os.remove(os.path.join(app.root_path, 'static', post.image_path))
        except Exception:
            pass
        post.image_path = None
    if image and image.filename:
        # Заменить картинку
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = f'post_{user_id}_{int(time.time())}_{image.filename}'
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)
        post.image_path = f'uploads/{filename}'
    db.session.commit()
    return jsonify({'success': True, 'content': post.content, 'image_path': post.image_path})

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

@app.route('/feed')
def global_feed():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    
    # Поиск по тегам
    search_query = request.args.get('q', '').strip()
    if search_query.startswith('#'):
        tag_name = search_query[1:]  # Убираем #
        posts = Post.query.join(Post.tags).filter(Tag.name == tag_name).order_by(Post.created_at.desc()).all()
    else:
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
    
    return render_template('wall.html', user=user, posts=posts, is_global_wall=True, search_query=search_query)

@app.route('/user/<username>')
def user_wall(username):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('register'))
    
    current_user = User.query.get(current_user_id)
    target_user = User.query.filter_by(username=username).first()
    
    if not target_user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('wall'))
    
    # Получаем посты только этого пользователя
    posts = Post.query.filter_by(user_id=target_user.id).order_by(Post.created_at.desc()).all()
    
    # Жадная загрузка авторов и комментариев
    for post in posts:
        post.user = User.query.get(post.user_id)
        post.comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
        for comment in post.comments:
            comment.user = User.query.get(comment.user_id)
        post.likes_count = Like.query.filter_by(post_id=post.id).count()
        post.liked_by_current = False
        if current_user_id:
            post.liked_by_current = Like.query.filter_by(post_id=post.id, user_id=current_user_id).first() is not None
    
    # Получаем подписчиков и подписки целевого пользователя
    followers = list(target_user.followers)
    following = list(target_user.following)
    
    # Проверяем, подписан ли текущий пользователь на целевого
    is_following = False
    if current_user_id:
        from models import Follow
        is_following = Follow.query.filter_by(
            follower_id=current_user_id,
            followed_id=target_user.id
        ).first() is not None
    
    return render_template('wall.html', 
                         user=current_user, 
                         posts=posts, 
                         target_user=target_user, 
                         is_global_wall=False,
                         followers=followers,
                         following=following,
                         followers_count=len(followers),
                         following_count=len(following),
                         is_following=is_following)

@app.route('/follow/<username>', methods=['POST'])
def follow_user(username):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    
    current_user = User.query.get(current_user_id)
    target_user = User.query.filter_by(username=username).first()
    
    if not target_user:
        return jsonify({'error': 'user_not_found'}), 404
    
    if current_user.id == target_user.id:
        return jsonify({'error': 'cannot_follow_self'}), 400
    
    if current_user.is_following(target_user):
        return jsonify({'error': 'already_following'}), 400
    
    try:
        current_user.follow(target_user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Вы подписались на {target_user.username}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database_error'}), 500

@app.route('/unfollow/<username>', methods=['POST'])
def unfollow_user(username):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    
    current_user = User.query.get(current_user_id)
    target_user = User.query.filter_by(username=username).first()
    
    if not target_user:
        return jsonify({'error': 'user_not_found'}), 404
    
    if not current_user.is_following(target_user):
        return jsonify({'error': 'not_following'}), 400
    
    try:
        current_user.unfollow(target_user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Вы отписались от {target_user.username}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'database_error'}), 500

@app.route('/search/users')
def search_users():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'users': []})
    
    # Поиск по username, full_name, organization
    users = User.query.filter(
        db.or_(
            User.username.ilike(f'%{query}%'),
            User.full_name.ilike(f'%{query}%'),
            User.organization.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    current_user = User.query.get(current_user_id)
    results = []
    
    for user in users:
        if user.id != current_user.id:  # Исключаем текущего пользователя
            user_data = {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar,
                'is_following': current_user.is_following(user)
            }
            
            # Добавляем видимую информацию
            if user.show_full_name and user.full_name:
                user_data['full_name'] = user.full_name
            if user.show_degree and user.degree:
                user_data['degree'] = user.degree
            if user.show_organization and user.organization:
                user_data['organization'] = user.organization
            if user.show_location and user.location:
                user_data['location'] = user.location
            
            results.append(user_data)
    
    return jsonify({'users': results})

@app.route('/search')
def search_page():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('register'))
    return render_template('search_users.html')

@app.route('/user/mini_profile/<int:user_id>')
def mini_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    data = {
        'username': user.username,
        'avatar': user.avatar,
    }
    if user.show_full_name and user.full_name:
        data['full_name'] = user.full_name
    if user.show_degree and user.degree:
        data['degree'] = user.degree
    if user.show_bio and user.bio:
        data['bio'] = user.bio
    if user.show_status and user.status:
        data['status'] = user.status
    if user.show_organization and user.organization:
        data['organization'] = user.organization
    if user.show_location and user.location:
        data['location'] = user.location
    if user.show_interests and user.interests:
        data['interests'] = user.interests
    if user.show_scholar_links and user.scholar_links:
        data['scholar_links'] = user.scholar_links
    if user.show_website and user.website:
        data['website'] = user.website
    if user.show_public_email and user.public_email:
        data['public_email'] = user.public_email
    if user.show_telegram and user.telegram:
        data['telegram'] = user.telegram
    return jsonify(data)

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return dict(current_user=user, is_user_online=is_user_online)
    return dict(current_user=None, is_user_online=is_user_online)

@app.template_filter('hashtagify')
def hashtagify(text):
    def repl(match):
        tag = match.group(1)
        return f'<a href="/feed?q=%23{tag}" class="hashtag">#{tag}</a>'
    return re.sub(r'#([\wа-яА-ЯёЁ\-]+)', repl, text)

# API для лайков в общей ленте
@app.route('/api/like/<int:post_id>', methods=['POST'])
def api_like_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    post = Post.query.get_or_404(post_id)
    
    # Проверяем, есть ли уже лайк от этого пользователя
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    
    if existing_like:
        # Удаляем лайк
        db.session.delete(existing_like)
        liked = False
    else:
        # Добавляем лайк
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        liked = True
    
    db.session.commit()
    
    # Возвращаем обновленное количество лайков
    likes_count = Like.query.filter_by(post_id=post_id).count()
    return jsonify({'liked': liked, 'likes_count': likes_count})

# API для комментариев в общей ленте
@app.route('/api/comment/<int:post_id>', methods=['POST'])
def api_comment_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    post = Post.query.get_or_404(post_id)
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    # Создаем комментарий
    new_comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=content
    )
    db.session.add(new_comment)
    db.session.commit()
    
    # Возвращаем обновленное количество комментариев
    comments_count = Comment.query.filter_by(post_id=post_id).count()
    return jsonify({'success': True, 'comments_count': comments_count})

# API для получения комментариев поста
@app.route('/api/comments/<int:post_id>')
def api_get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
            'user': {
                'username': comment.user.username,
                'avatar': comment.user.avatar,
                'degree': comment.user.degree
            }
        })
    
    return jsonify({'comments': comments_data})

if __name__ == '__main__':
    app.run(debug=True)