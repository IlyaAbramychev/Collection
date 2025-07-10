// like-toggle.js

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.like-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const postId = btn.getAttribute('data-post-id');
      const icon = btn.querySelector('img');
      const countSpan = btn.querySelector('.like-count');
      fetch('/wall/like', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'post_id=' + encodeURIComponent(postId)
      })
      .then(r => r.json())
      .then(data => {
        if (data && typeof data.count !== 'undefined') {
          countSpan.textContent = data.count;
          btn.setAttribute('data-liked', data.liked ? 'true' : 'false');
          if (data.liked) {
            icon.style.filter = 'invert(41%) sepia(94%) saturate(442%) hue-rotate(124deg) brightness(92%) contrast(92%)';
          } else {
            icon.style.filter = '';
          }
        }
      });
    });
  });
}); 