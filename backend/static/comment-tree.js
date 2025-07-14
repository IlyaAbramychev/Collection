// comment-tree.js
// Динамическая загрузка и рендер дерева комментариев для каждого поста

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.wall-comments[data-post-id]').forEach(function (container) {
    const postId = container.getAttribute('data-post-id');
    loadComments(postId, container);
  });
});

function loadComments(postId, container) {
  fetch(`/wall/comments?post_id=${postId}`)
    .then(r => r.json())
    .then(tree => {
      container.innerHTML = '';
      renderCommentTree(tree, container, postId);
      addCommentForm(container, postId, null);
    });
}

function renderCommentTree(comments, parentElem, postId, level = 0) {
  const currentUserId = window.currentUserId;
  comments.forEach(comment => {
    const div = document.createElement('div');
    div.className = 'comment-item';
    div.style = `margin-bottom:10px;padding:10px 14px 10px 10px;background:#fafdff;border-radius:10px;box-shadow:0 1px 4px #3ec6b022;display:flex;flex-direction:column;gap:4px;margin-left:${level*28}px;position:relative;`;
    let menuHtml = '';
    if (currentUserId && String(comment.user_id) === String(currentUserId)) {
      menuHtml = `
        <button class="comment-menu-btn" style="background:none;border:none;font-size:1.2em;color:#888;cursor:pointer;padding:0 4px;">⋯</button>
        <div class="comment-menu-dropdown" style="display:none;position:absolute;right:10px;top:36px;background:#fff;border-radius:8px;box-shadow:0 2px 8px #3ec6b033;z-index:10;min-width:110px;flex-direction:column;">
          <button class="comment-menu-edit" data-comment-id="${comment.id}" style="background:none;border:none;padding:8px 14px;text-align:left;width:100%;color:#187a6e;display:flex;align-items:center;gap:8px;">Редактировать</button>
          <button class="comment-menu-delete" data-comment-id="${comment.id}" style="background:none;border:none;padding:8px 14px;text-align:left;width:100%;color:#e74c3c;display:flex;align-items:center;gap:8px;">Удалить</button>
        </div>
      `;
    }
    div.innerHTML = `
      <div class="comment-header" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <div style="width:28px;height:28px;border-radius:50%;background:#fff;overflow:hidden;display:flex;align-items:center;justify-content:center;">
          <img src="/static/${comment.user.avatar || 'img/profile_user_svg.svg'}" alt="Аватар" style="width:20px;height:20px;object-fit:cover;border-radius:50%;background:#fff;">
        </div>
        <span class="comment-username">${comment.user.username}</span>
        ${comment.user.degree ? `<span class="degree-badge degree-${comment.user.degree.toLowerCase().replace(/\s+/g,'-')}">${comment.user.degree}</span>` : ''}
        <span style="color:#aaa;font-size:0.92em;">${formatDate(comment.created_at)}</span>
        ${menuHtml}
        <button class="comment-like-btn" data-comment-id="${comment.id}" data-liked="${comment.liked_by_current}" style="background:none;border:none;color:#3ec6b0;font-size:1em;cursor:pointer;display:flex;align-items:center;gap:4px;margin-left:auto;">
          <img src="/static/img/heart_svg.svg" style="width:16px;height:16px;${comment.liked_by_current ? 'filter:invert(41%) sepia(94%) saturate(442%) hue-rotate(124deg) brightness(92%) contrast(92%);' : ''}">
          <span class="comment-like-count">${comment.likes_count}</span>
        </button>
        <button class="comment-reply-btn" data-comment-id="${comment.id}" style="background:none;border:none;color:#4db6e2;font-size:0.98em;cursor:pointer;">Ответить</button>
      </div>
      <div class="comment-body" style="margin-left:36px;margin-top:2px;word-break:break-word;">
        <span class="comment-content">${hashtagify(comment.content)}</span>
      </div>
    `;
    parentElem.appendChild(div);
    // Форма для ответа (по клику)
    div.querySelector('.comment-reply-btn').addEventListener('click', function () {
      let form = div.querySelector('.comment-reply-form');
      if (!form) {
        form = addCommentForm(div, postId, comment.id);
      }
      form.querySelector('input[name="content"]').focus();
    });
    // Лайк
    div.querySelector('.comment-like-btn').addEventListener('click', function () {
      toggleCommentLike(comment.id, div.querySelector('.comment-like-btn'));
    });
    // --- Меню три точки ---
    const menuBtn = div.querySelector('.comment-menu-btn');
    const menuDropdown = div.querySelector('.comment-menu-dropdown');
    if (menuBtn && menuDropdown) {
      menuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        menuDropdown.style.display = menuDropdown.style.display === 'flex' ? 'none' : 'flex';
        menuDropdown.style.flexDirection = 'column';
      });
      document.addEventListener('click', function(e) {
        if (!e.target.closest('.comment-menu-btn')) {
          menuDropdown.style.display = 'none';
        }
      });
      // Удаление комментария
      menuDropdown.querySelector('.comment-menu-delete').addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('Удалить комментарий?')) {
          const formData = new FormData();
          formData.append('comment_id', comment.id);
          fetch('/wall/comment/delete', {
            method: 'POST',
            body: formData
          })
            .then(r => r.json())
            .then(resp => {
              if (resp.success) {
                // Перезагрузить дерево комментариев
                const container = div.closest('.wall-comments');
                loadComments(postId, container);
              } else {
                alert('Ошибка: ' + (resp.error || 'Не удалось удалить комментарий.'));
              }
            });
        }
      });
      // --- Редактирование комментария ---
      menuDropdown.querySelector('.comment-menu-edit').addEventListener('click', function(e) {
        e.preventDefault();
        menuDropdown.style.display = 'none';
        const contentSpan = div.querySelector('.comment-content');
        if (!contentSpan) return;
        if (div.querySelector('.edit-comment-form')) return;
        const oldContent = contentSpan.textContent;
        const form = document.createElement('form');
        form.className = 'edit-comment-form';
        form.style = 'display:inline;margin-left:8px;';
        form.innerHTML = `<input type='text' name='content' value='${oldContent.replace(/'/g, "&#39;")}' style='font-size:1em;width:220px;border-radius:6px;padding:2px 8px;'> <button type='submit' style='padding:2px 12px;border-radius:8px;background:#3ec6b0;color:#fff;border:none;'>OK</button> <button type='button' class='edit-cancel-btn' style='padding:2px 10px;border-radius:8px;background:#eee;color:#444;border:none;'>Отмена</button>`;
        contentSpan.style.display = 'none';
        contentSpan.parentNode.insertBefore(form, contentSpan.nextSibling);
        form.querySelector('.edit-cancel-btn').onclick = function() {
          form.remove();
          contentSpan.style.display = '';
        };
        form.onsubmit = function(ev) {
          ev.preventDefault();
          const fd = new FormData();
          fd.append('comment_id', comment.id);
          fd.append('content', form.querySelector('input[name="content"]').value);
          fetch('/wall/comment/edit', {
            method: 'POST',
            body: fd
          })
            .then(r => r.json())
            .then(resp => {
              if (resp.success) {
                contentSpan.textContent = resp.content;
                form.remove();
                contentSpan.style.display = '';
              } else {
                alert('Ошибка: ' + (resp.error || 'Не удалось сохранить изменения.'));
              }
            });
        };
      });
    }
    // Рекурсивно рендерим ответы
    if (comment.replies && comment.replies.length > 0) {
      renderCommentTree(comment.replies, parentElem, postId, level + 1);
    }
  });
}

function addCommentForm(parentElem, postId, parentId) {
  let form = document.createElement('form');
  form.className = 'comment-reply-form';
  form.style = 'margin-top:6px;display:flex;gap:8px;';
  form.innerHTML = `
    <input type="hidden" name="post_id" value="${postId}">
    ${parentId ? `<input type="hidden" name="parent_id" value="${parentId}">` : ''}
    <input type="text" name="content" placeholder="Комментарий..." required style="flex:1;border-radius:8px;padding:6px 10px;">
    <button type="submit" class="button" style="padding:6px 16px;">→</button>
  `;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const data = new FormData(form);
    fetch('/wall/comment', {
      method: 'POST',
      body: data
    })
      .then(r => r.json())
      .then(resp => {
        if (resp.id) {
          // Перезагрузить дерево комментариев
          const container = parentElem.closest('.wall-comments');
          loadComments(postId, container);
        }
      });
  });
  parentElem.appendChild(form);
  return form;
}

function toggleCommentLike(commentId, btn) {
  const formData = new FormData();
  formData.append('comment_id', commentId);
  fetch('/wall/comment/like', {
    method: 'POST',
    body: formData
  })
    .then(r => r.json())
    .then(resp => {
      if ('liked' in resp && 'count' in resp) {
        btn.setAttribute('data-liked', resp.liked);
        btn.querySelector('.comment-like-count').textContent = resp.count;
        btn.querySelector('img').style.filter = resp.liked ? 'invert(41%) sepia(94%) saturate(442%) hue-rotate(124deg) brightness(92%) contrast(92%)' : '';
      }
    });
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function hashtagify(text) {
  return text.replace(/#([\wа-яА-ЯёЁ\-]+)/gi, function(match, tag) {
    return `<a href="/wall?q=%23${tag}" class="hashtag">#${tag}</a>`;
  });
} 