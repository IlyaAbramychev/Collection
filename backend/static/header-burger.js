document.addEventListener('DOMContentLoaded', function() {
  const burger = document.getElementById('headerBurgerBtn');
  const dropdown = document.getElementById('headerDropdown');
  if (burger && dropdown) {
    burger.onclick = function(e) {
      e.stopPropagation();
      dropdown.classList.toggle('active');
    };
    document.body.onclick = function() {
      dropdown.classList.remove('active');
    };
  }
}); 