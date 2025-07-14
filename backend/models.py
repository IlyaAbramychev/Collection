from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(64))
    show_status = db.Column(db.Boolean, default=True)
    bio = db.Column(db.Text)
    show_bio = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(256))  # путь к файлу аватара
    # Новые поля для научного профиля
    full_name = db.Column(db.String(128), nullable=True)
    show_full_name = db.Column(db.Boolean, default=True)
    degree = db.Column(db.String(64), nullable=True)
    show_degree = db.Column(db.Boolean, default=True)
    interests = db.Column(db.String(256), nullable=True)
    show_interests = db.Column(db.Boolean, default=True)
    organization = db.Column(db.String(128), nullable=True)
    show_organization = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(128), nullable=True)
    show_location = db.Column(db.Boolean, default=True)
    scholar_links = db.Column(db.String(512), nullable=True)  # ссылки через запятую или json
    show_scholar_links = db.Column(db.Boolean, default=True)
    website = db.Column(db.String(256), nullable=True)
    show_website = db.Column(db.Boolean, default=True)
    birthdate = db.Column(db.String(32), nullable=True)  # строкой для простоты
    show_birthdate = db.Column(db.Boolean, default=True)
    public_email = db.Column(db.String(120), nullable=True)
    show_public_email = db.Column(db.Boolean, default=True)
    telegram = db.Column(db.String(64), nullable=True)
    show_telegram = db.Column(db.Boolean, default=True)
    # Поля для онлайн статуса
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    image_path = db.Column(db.String(256), nullable=True)  # путь к картинке
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy=True))

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user = db.relationship('User', backref=db.backref('comment_likes', lazy=True))
    comment = db.relationship('Comment', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    post = db.relationship('Post', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_assoc')
    followed = db.relationship('User', foreign_keys=[followed_id], backref='followers_assoc')

# Методы для User:
# User.follow(user), User.unfollow(user), User.is_following(user)

setattr(User, 'follow', lambda self, user: (
    db.session.add(Follow(follower_id=self.id, followed_id=user.id)) if not self.is_following(user) and self.id != user.id else None
))
setattr(User, 'unfollow', lambda self, user: (
    db.session.delete(f) for f in Follow.query.filter_by(follower_id=self.id, followed_id=user.id).all()
))
setattr(User, 'is_following', lambda self, user: (
    Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None
))
setattr(User, 'followers', property(lambda self: User.query.join(Follow, Follow.follower_id == User.id).filter(Follow.followed_id == self.id)))
setattr(User, 'following', property(lambda self: User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == self.id)))