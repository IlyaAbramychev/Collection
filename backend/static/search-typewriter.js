// Typewriter effect for search input placeholder
const phrases = [
  "🔬 квантовые вычисления",
  "⚛️ ядерные реакторы", 
  "🧠 нейронные сети",
  "🤖 машинное обучение",
  "📊 графовые базы данных",
  "🎯 искусственный интеллект",
  "💬 обработка естественного языка",
  "🔥 глубокое обучение",
  "🔐 квантовая криптография",
  "⛓️ блокчейн технологии",
  "🧬 генетические алгоритмы",
  "🤖 робототехника",
  "🌐 интернет вещей",
  "☁️ распределённые вычисления",
  "💾 облачные платформы",
  "🧪 биоинформатика",
  "👁️ компьютерное зрение",
  "📡 теория информации",
  "⚡ алгоритмы оптимизации",
  "🔋 сверхпроводники",
  "🔬 нанотехнологии",
  "✨ квантовая телепортация",
  "⚙️ системы управления",
  "📈 цифровая обработка сигналов",
  "🥽 виртуальная реальность",
  "🌟 дополненная реальность",
  "🖨️ 3D-печать",
  "🏭 автоматизация производства",
  "📊 большие данные",
  "📈 анализ данных",
  "📊 статистическое моделирование",
  "🕸️ теория графов",
  "🔒 криптографические протоколы",
  "⚡ квантовые алгоритмы",
  "🎮 обучение с подкреплением",
  "🔍 распознавание образов",
  "📝 компьютерная лингвистика",
  "💊 цифровая медицина",
  "🤖 интеллектуальные агенты",
  "🎯 системы поддержки принятия решений",
  "🛡️ информационная безопасность",
  "📋 автоматическое доказательство теорем",
  "⚡ гибридные вычисления",
  "👥 цифровые двойники",
  "🔗 технологии блокчейн",
  "📡 интеллектуальные датчики",
  "🌐 квантовые сети",
  "🤖 роботизированные системы",
  "👁️ машинное зрение",
  "🧠 глубокие нейронные сети"
];

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

const searchInput = document.querySelector('.header-search input');
if (searchInput) {
  searchInput.classList.add('typewriter-active');
  let phraseIndex = 0;
  let charIndex = 0;
  let typing = true;
  let currentPhrases = [...phrases];
  shuffle(currentPhrases);

  const minWidth = 120;
  const maxWidth = 400;
  function updateInputWidth(text) {
    if (!searchInput) return;
    // Создаём временный span для измерения ширины текста
    const span = document.createElement('span');
    span.style.visibility = 'hidden';
    span.style.position = 'fixed';
    span.style.whiteSpace = 'pre';
    span.style.font = window.getComputedStyle(searchInput).font;
    span.textContent = text;
    document.body.appendChild(span);
    let width = span.offsetWidth + 36; // немного запас для курсора и иконки
    document.body.removeChild(span);
    width = Math.max(minWidth, Math.min(width, maxWidth));
    searchInput.style.width = width + 'px';
  }

  function typePhrase() {
    if (!typewriterActive) return;
    
    const phrase = currentPhrases[phraseIndex];
    if (typing) {
      if (charIndex <= phrase.length) {
        const currentText = phrase.slice(0, charIndex);
        const cursor = charIndex < phrase.length ? '|' : '';
        searchInput.setAttribute('placeholder', currentText + cursor);
        updateInputWidth(currentText);
        charIndex++;
        // Более плавная скорость печати
        typewriterTimeout = setTimeout(typePhrase, 80 + Math.random() * 50);
      } else {
        typing = false;
        // Пауза после завершения печати
        typewriterTimeout = setTimeout(typePhrase, 2000 + Math.random() * 1000);
      }
    } else {
      if (charIndex > 0) {
        const currentText = phrase.slice(0, charIndex - 1);
        const cursor = charIndex > 1 ? '|' : '';
        searchInput.setAttribute('placeholder', currentText + cursor);
        updateInputWidth(currentText);
        charIndex--;
        // Более быстрое удаление
        typewriterTimeout = setTimeout(typePhrase, 40 + Math.random() * 20);
      } else {
        typing = true;
        phraseIndex = (phraseIndex + 1) % currentPhrases.length;
        if (phraseIndex === 0) shuffle(currentPhrases);
        // Пауза перед началом нового слова
        typewriterTimeout = setTimeout(typePhrase, 600 + Math.random() * 400);
      }
    }
  }

  let typewriterActive = true;
  let typewriterTimeout;
  
  function startTypewriter() {
    if (typewriterActive) {
      typewriterTimeout = setTimeout(typePhrase, 100);
    }
  }
  
  function stopTypewriter() {
    typewriterActive = false;
    if (typewriterTimeout) {
      clearTimeout(typewriterTimeout);
    }
    searchInput.setAttribute('placeholder', 'Поиск пользователей или #тегов...');
    searchInput.classList.remove('typewriter-active');
  }
  
  function resumeTypewriter() {
    if (searchInput.value === '') {
      typewriterActive = true;
      searchInput.classList.add('typewriter-active');
      startTypewriter();
    }
  }
  
  startTypewriter();
  
  // Остановка typewriter при взаимодействии пользователя
  searchInput.addEventListener('focus', () => {
    searchInput.style.width = maxWidth + 'px';
    stopTypewriter();
  });
  
  searchInput.addEventListener('blur', () => {
    updateInputWidth('');
    setTimeout(resumeTypewriter, 1000); // Возобновляем через секунду после потери фокуса
  });
  
  searchInput.addEventListener('input', () => {
    if (searchInput.value.length > 0) {
      stopTypewriter();
    } else {
      resumeTypewriter();
    }
  });
} 