from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Увеличено до 256
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
    # Новые поля для модерации и ролей
    role = db.Column(db.String(32), default='user')  # user, moderator, admin
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(256), nullable=True)
    ban_until = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#00e1d3')  # Цвет тега в hex
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#00e1d3')
    icon = db.Column(db.String(32), nullable=True)  # Иконка для категории
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    image_path = db.Column(db.String(256), nullable=True)  # путь к картинке
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    # Новые поля для расширенной функциональности
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    publish_at = db.Column(db.DateTime, nullable=True)  # Для отложенной публикации
    post_type = db.Column(db.String(32), default='text')  # text, poll, announcement
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    edit_count = db.Column(db.Integer, default=0)
    attachments = db.Column(db.Text, nullable=True)  # JSON список файлов
    preview_text = db.Column(db.String(500), nullable=True)  # Краткое описание
    
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    
    def get_attachments(self):
        """Получить список вложений"""
        if self.attachments:
            try:
                return json.loads(self.attachments)
            except:
                return []
        return []
    
    def add_attachment(self, filename, file_type, file_size):
        """Добавить вложение"""
        attachments = self.get_attachments()
        attachments.append({
            'filename': filename,
            'type': file_type,
            'size': file_size,
            'uploaded_at': datetime.utcnow().isoformat()
        })
        self.attachments = json.dumps(attachments)
    
    def is_liked_by(self, user):
        """Проверить, лайкнул ли пользователь этот пост"""
        if not user:
            return False
        return Like.query.filter_by(post_id=self.id, user_id=user.id).first() is not None

class Article(db.Model):
    """Полноценные статьи с расширенными возможностями"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Markdown содержимое
    summary = db.Column(db.Text, nullable=True)  # Краткое описание
    cover_image = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)  # Рекомендуемая статья
    reading_time = db.Column(db.Integer, default=0)  # Время чтения в минутах
    views_count = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('articles', lazy=True))
    category = db.relationship('Category', backref=db.backref('articles', lazy=True))
    tags = db.relationship('Tag', secondary=article_tags, backref=db.backref('articles', lazy='dynamic'))

class Poll(db.Model):
    """Опросы и голосования"""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    question = db.Column(db.String(256), nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON список вариантов
    multiple_choice = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    post = db.relationship('Post', backref=db.backref('poll', uselist=False))
    
    def get_options(self):
        """Получить варианты ответов"""
        try:
            return json.loads(self.options)
        except:
            return []
    
    def set_options(self, options_list):
        """Установить варианты ответов"""
        self.options = json.dumps(options_list)

class PollVote(db.Model):
    """Голоса в опросах"""
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    option_index = db.Column(db.Integer, nullable=False)  # Индекс выбранного варианта
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    poll = db.relationship('Poll', backref=db.backref('votes', lazy=True))
    user = db.relationship('User', backref=db.backref('poll_votes', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    article = db.relationship('Article', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy=True))

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user = db.relationship('User', backref=db.backref('comment_likes', lazy=True))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    post = db.relationship('Post', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))
    article = db.relationship('Article', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_assoc')
    followed = db.relationship('User', foreign_keys=[followed_id], backref='followers_assoc')

class TagSubscription(db.Model):
    """Модель подписок на теги"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('tag_subscriptions', lazy=True))
    tag = db.relationship('Tag', backref=db.backref('subscribers', lazy=True))

class ActivityFeed(db.Model):
    """Модель ленты активности"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(32), nullable=False)  # post, comment, like, follow
    object_type = db.Column(db.String(32), nullable=False)  # post, article, comment, user
    object_id = db.Column(db.Integer, nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # для follow
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='activities')
    target_user = db.relationship('User', foreign_keys=[target_user_id])

class Reaction(db.Model):
    """Модель расширенных реакций"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    reaction_type = db.Column(db.String(16), nullable=False)  # like, heart, fire, think
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('reactions', lazy=True))
    post = db.relationship('Post', backref=db.backref('reactions', lazy=True))
    article = db.relationship('Article', backref=db.backref('reactions', lazy=True))
    comment = db.relationship('Comment', backref=db.backref('reactions', lazy=True))

class Bookmark(db.Model):
    """Закладки пользователей"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))
    post = db.relationship('Post', backref=db.backref('bookmarks', lazy=True))
    article = db.relationship('Article', backref=db.backref('bookmarks', lazy=True))

class Badge(db.Model):
    """Бейджи и достижения"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(64), nullable=True)  # Иконка бейджа
    color = db.Column(db.String(7), default='#00e1d3')
    rarity = db.Column(db.String(16), default='common')  # common, rare, epic, legendary
    condition_type = db.Column(db.String(32), nullable=False)  # posts_count, likes_received, etc.
    condition_value = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserBadge(db.Model):
    """Связь пользователей с полученными бейджами"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('user_badges', lazy=True))
    badge = db.relationship('Badge', backref=db.backref('user_badges', lazy=True))

class Notification(db.Model):
    """Уведомления"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(32), nullable=False)  # follow, like, comment, mention
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Ссылки на связанные объекты
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    related_post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    related_article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy=True))
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    related_post = db.relationship('Post')
    related_article = db.relationship('Article')

class Report(db.Model):
    """Жалобы на контент"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Кто пожаловался
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reason = db.Column(db.String(32), nullable=False)  # spam, inappropriate, harassment
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(16), default='pending')  # pending, reviewed, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('reports_made', lazy=True))
    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref=db.backref('reports_received', lazy=True))
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    post = db.relationship('Post')
    article = db.relationship('Article')
    comment = db.relationship('Comment')

class UserExternalLink(db.Model):
    """Модель для хранения внешних ссылок пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    link_type = db.Column(db.String(32), nullable=False)  # github, linkedin, twitter, etc.
    url = db.Column(db.String(512), nullable=False)
    title = db.Column(db.String(128), nullable=True)  # Пользовательское название
    is_public = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)  # Порядок отображения
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('external_links', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<UserExternalLink {self.link_type}: {self.url}>'

class UserProfileView(db.Model):
    """Модель для отслеживания просмотров профиля"""
    id = db.Column(db.Integer, primary_key=True)
    profile_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    viewer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None для анонимных
    viewer_ip = db.Column(db.String(45), nullable=True)  # IP для анонимных просмотров
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    profile_user = db.relationship('User', foreign_keys=[profile_user_id], backref=db.backref('profile_views', lazy=True))
    viewer_user = db.relationship('User', foreign_keys=[viewer_user_id])
    
    def __repr__(self):
        return f'<UserProfileView {self.profile_user_id} by {self.viewer_user_id or self.viewer_ip}>'

class UserSkill(db.Model):
    """Модель для навыков пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_name = db.Column(db.String(64), nullable=False)
    skill_level = db.Column(db.String(32), nullable=True)  # beginner, intermediate, advanced, expert
    is_public = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('skills', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<UserSkill {self.skill_name} ({self.skill_level})>'

class UserProject(db.Model):
    """Модель для проектов пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_url = db.Column(db.String(512), nullable=True)
    github_url = db.Column(db.String(512), nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    technologies = db.Column(db.String(512), nullable=True)  # JSON строка с технологиями
    start_date = db.Column(db.String(32), nullable=True)
    end_date = db.Column(db.String(32), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('projects', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<UserProject {self.title}>'

# Методы для User (существующие)
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

# Новые методы для User
def get_badges(self):
    """Получить все бейджи пользователя"""
    return Badge.query.join(UserBadge).filter(UserBadge.user_id == self.id).all()

def has_badge(self, badge_name):
    """Проверить, есть ли у пользователя определенный бейдж"""
    return UserBadge.query.join(Badge).filter(
        UserBadge.user_id == self.id,
        Badge.name == badge_name
    ).first() is not None

def award_badge(self, badge_name):
    """Выдать бейдж пользователю"""
    badge = Badge.query.filter_by(name=badge_name).first()
    if badge and not self.has_badge(badge_name):
        user_badge = UserBadge(user_id=self.id, badge_id=badge.id)
        db.session.add(user_badge)
        return True
    return False

def get_unread_notifications_count(self):
    """Получить количество непрочитанных уведомлений"""
    return Notification.query.filter_by(user_id=self.id, is_read=False).count()

setattr(User, 'get_badges', get_badges)
setattr(User, 'has_badge', has_badge)
setattr(User, 'award_badge', award_badge)
setattr(User, 'get_unread_notifications_count', get_unread_notifications_count)

# Методы для работы с подписками на теги
def subscribe_to_tag(self, tag):
    """Подписаться на тег"""
    if not self.is_subscribed_to_tag(tag):
        subscription = TagSubscription(user_id=self.id, tag_id=tag.id)
        db.session.add(subscription)
        return True
    return False

def unsubscribe_from_tag(self, tag):
    """Отписаться от тега"""
    subscription = TagSubscription.query.filter_by(user_id=self.id, tag_id=tag.id).first()
    if subscription:
        db.session.delete(subscription)
        return True
    return False

def is_subscribed_to_tag(self, tag):
    """Проверить подписку на тег"""
    return TagSubscription.query.filter_by(user_id=self.id, tag_id=tag.id).first() is not None

def get_subscribed_tags(self):
    """Получить все теги на которые подписан пользователь"""
    return Tag.query.join(TagSubscription).filter(TagSubscription.user_id == self.id).all()

def get_personalized_feed(self, limit=20, offset=0):
    """Получить персонализированную ленту активности"""
    # Получаем ID пользователей на которых подписан
    following_ids = [user.id for user in self.following]
    
    # Получаем ID тегов на которые подписан
    subscribed_tag_ids = [tag.id for tag in self.get_subscribed_tags()]
    
    # Базовый запрос для постов
    posts_query = Post.query.filter(
        Post.is_published == True,
        Post.is_deleted == False
    )
    
    # Фильтруем по подпискам на авторов или теги
    if following_ids or subscribed_tag_ids:
        from sqlalchemy import or_
        filters = []
        
        if following_ids:
            filters.append(Post.user_id.in_(following_ids))
        
        if subscribed_tag_ids:
            filters.append(Post.tags.any(Tag.id.in_(subscribed_tag_ids)))
        
        posts_query = posts_query.filter(or_(*filters))
    
    return posts_query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()

def add_activity(self, activity_type, object_type, object_id, target_user_id=None):
    """Добавить активность в ленту"""
    activity = ActivityFeed(
        user_id=self.id,
        activity_type=activity_type,
        object_type=object_type,
        object_id=object_id,
        target_user_id=target_user_id
    )
    db.session.add(activity)
    return activity

setattr(User, 'subscribe_to_tag', subscribe_to_tag)
setattr(User, 'unsubscribe_from_tag', unsubscribe_from_tag)
setattr(User, 'is_subscribed_to_tag', is_subscribed_to_tag)
setattr(User, 'get_subscribed_tags', get_subscribed_tags)
setattr(User, 'get_personalized_feed', get_personalized_feed)
setattr(User, 'add_activity', add_activity)

# Добавляем методы для работы с внешними ссылками
def get_external_links_by_type(self):
    """Получить внешние ссылки, сгруппированные по типу"""
    links = {}
    for link in self.external_links:
        if link.is_public:
            if link.link_type not in links:
                links[link.link_type] = []
            links[link.link_type].append(link)
    return links

def get_profile_views_count(self):
    """Получить количество просмотров профиля"""
    return len(self.profile_views)

def get_recent_profile_views(self, limit=10):
    """Получить последние просмотры профиля"""
    return UserProfileView.query.filter_by(profile_user_id=self.id)\
        .order_by(UserProfileView.viewed_at.desc())\
        .limit(limit).all()

def get_public_skills(self):
    """Получить публичные навыки"""
    return UserSkill.query.filter_by(user_id=self.id, is_public=True)\
        .order_by(UserSkill.order_index, UserSkill.skill_name).all()

def get_featured_projects(self):
    """Получить избранные проекты"""
    return UserProject.query.filter_by(user_id=self.id, is_public=True, is_featured=True)\
        .order_by(UserProject.order_index, UserProject.created_at.desc()).all()

def get_all_projects(self):
    """Получить все публичные проекты"""
    return UserProject.query.filter_by(user_id=self.id, is_public=True)\
        .order_by(UserProject.order_index, UserProject.created_at.desc()).all()

def add_profile_view(self, viewer_user=None, viewer_ip=None):
    """Добавить просмотр профиля"""
    # Проверяем, не просматривает ли пользователь свой собственный профиль
    if viewer_user and viewer_user.id == self.id:
        return
    
    # Проверяем, не было ли недавнего просмотра от этого пользователя/IP
    recent_view = None
    if viewer_user:
        recent_view = UserProfileView.query.filter_by(
            profile_user_id=self.id,
            viewer_user_id=viewer_user.id
        ).filter(UserProfileView.viewed_at > datetime.utcnow() - timedelta(hours=1)).first()
    elif viewer_ip:
        recent_view = UserProfileView.query.filter_by(
            profile_user_id=self.id,
            viewer_ip=viewer_ip
        ).filter(UserProfileView.viewed_at > datetime.utcnow() - timedelta(hours=1)).first()
    
    if not recent_view:
        view = UserProfileView(
            profile_user_id=self.id,
            viewer_user_id=viewer_user.id if viewer_user else None,
            viewer_ip=viewer_ip
        )
        db.session.add(view)
        db.session.commit()

setattr(User, 'get_external_links_by_type', get_external_links_by_type)
setattr(User, 'get_profile_views_count', get_profile_views_count)
setattr(User, 'get_recent_profile_views', get_recent_profile_views)
setattr(User, 'get_public_skills', get_public_skills)
setattr(User, 'get_featured_projects', get_featured_projects)
setattr(User, 'get_all_projects', get_all_projects)
setattr(User, 'add_profile_view', add_profile_view)