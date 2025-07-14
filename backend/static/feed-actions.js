// Функция для переключения лайка
function toggleLike(postId) {
    fetch(`/api/like/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Ошибка: ' + data.error);
            return;
        }
        
        // Обновляем счетчик лайков
        const likesCountElement = document.getElementById(`likes-count-${postId}`);
        if (likesCountElement) {
            likesCountElement.textContent = data.likes_count;
        }
        
        // Можно добавить визуальную обратную связь (изменение цвета иконки)
        const likeButton = document.querySelector(`[onclick="toggleLike(${postId})"]`);
        if (likeButton) {
            const heartIcon = likeButton.querySelector('img');
            if (data.liked) {
                heartIcon.style.filter = 'invert(0.2) sepia(1) saturate(5) hue-rotate(340deg) brightness(1.2)';
            } else {
                heartIcon.style.filter = 'invert(0.2) sepia(1) saturate(5) hue-rotate(340deg) brightness(0.8)';
            }
        }
    })
    .catch(error => {
        console.error('Ошибка при лайке:', error);
        alert('Произошла ошибка при обработке лайка');
    });
}

// Функция для переключения отображения комментариев
function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-section-${postId}`);
    
    if (commentsSection) {
        // Если секция уже существует, переключаем видимость
        if (commentsSection.style.display === 'none') {
            commentsSection.style.display = 'block';
            loadComments(postId);
        } else {
            commentsSection.style.display = 'none';
        }
    } else {
        // Создаем секцию комментариев
        createCommentsSection(postId);
        loadComments(postId);
    }
}

// Функция для создания секции комментариев
function createCommentsSection(postId) {
    const postElement = document.querySelector(`[onclick="toggleComments(${postId})"]`).closest('.feed-post');
    
    const commentsSection = document.createElement('div');
    commentsSection.id = `comments-section-${postId}`;
    commentsSection.style.marginTop = '15px';
    commentsSection.style.borderTop = '1px solid rgba(62,198,176,0.08)';
    commentsSection.style.paddingTop = '15px';
    
    // Форма для добавления комментария
    const commentForm = document.createElement('div');
    commentForm.innerHTML = `
        <div style="display:flex;gap:10px;margin-bottom:15px;">
            <textarea id="comment-input-${postId}" placeholder="Написать комментарий..." 
                      style="flex:1;padding:10px;border:1px solid rgba(62,198,176,0.2);border-radius:8px;resize:vertical;min-height:60px;font-family:inherit;"></textarea>
            <button onclick="addComment(${postId})" 
                    style="padding:10px 20px;background:#3ec6b0;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;transition:background 0.2s;"
                    onmouseover="this.style.background='#2aa896'" onmouseout="this.style.background='#3ec6b0'">
                Отправить
            </button>
        </div>
    `;
    
    // Контейнер для комментариев
    const commentsContainer = document.createElement('div');
    commentsContainer.id = `comments-list-${postId}`;
    commentsContainer.style.maxHeight = '300px';
    commentsContainer.style.overflowY = 'auto';
    
    commentsSection.appendChild(commentForm);
    commentsSection.appendChild(commentsContainer);
    
    postElement.appendChild(commentsSection);
}

// Функция для загрузки комментариев
function loadComments(postId) {
    fetch(`/api/comments/${postId}`)
    .then(response => response.json())
    .then(data => {
        const commentsContainer = document.getElementById(`comments-list-${postId}`);
        if (!commentsContainer) return;
        
        commentsContainer.innerHTML = '';
        
        data.comments.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.style.cssText = 'margin-bottom:12px;padding:10px;background:rgba(62,198,176,0.04);border-radius:8px;';
            
            commentElement.innerHTML = `
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <img src="${comment.user.avatar || '/static/img/profile_user_svg.svg'}" 
                         alt="Аватар" style="width:24px;height:24px;border-radius:50%;object-fit:cover;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-weight:600;color:#187a6e;font-size:0.9em;">${comment.user.username}</span>
                        ${comment.user.degree ? `<span class="degree-badge degree-${comment.user.degree.toLowerCase().replace(' ', '-')}" style="font-size:0.7em;padding:2px 6px;border-radius:10px;font-weight:600;">${comment.user.degree}</span>` : ''}
                    </div>
                    <span style="font-size:0.8em;color:#999;margin-left:auto;">${comment.created_at}</span>
                </div>
                <div style="font-size:0.9em;color:#333;line-height:1.4;">${comment.content}</div>
            `;
            
            commentsContainer.appendChild(commentElement);
        });
    })
    .catch(error => {
        console.error('Ошибка при загрузке комментариев:', error);
    });
}

// Функция для добавления комментария
function addComment(postId) {
    const commentInput = document.getElementById(`comment-input-${postId}`);
    const content = commentInput.value.trim();
    
    if (!content) {
        alert('Комментарий не может быть пустым');
        return;
    }
    
    fetch(`/api/comment/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Ошибка: ' + data.error);
            return;
        }
        
        // Очищаем поле ввода
        commentInput.value = '';
        
        // Обновляем счетчик комментариев
        const commentsCountElement = document.getElementById(`comments-count-${postId}`);
        if (commentsCountElement) {
            commentsCountElement.textContent = data.comments_count;
        }
        
        // Перезагружаем комментарии
        loadComments(postId);
    })
    .catch(error => {
        console.error('Ошибка при добавлении комментария:', error);
        alert('Произошла ошибка при добавлении комментария');
    });
}

// Функция для открытия модального окна с изображением
function openImageModal(imageSrc) {
    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = imageSrc;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;
    
    modal.appendChild(img);
    document.body.appendChild(modal);
    
    // Закрытие по клику
    modal.onclick = function() {
        document.body.removeChild(modal);
    };
    
    // Закрытие по ESC
    const closeOnEsc = function(e) {
        if (e.key === 'Escape') {
            document.body.removeChild(modal);
            document.removeEventListener('keydown', closeOnEsc);
        }
    };
    document.addEventListener('keydown', closeOnEsc);
} 