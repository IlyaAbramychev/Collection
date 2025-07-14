// Валидация полей профиля в реальном времени
document.addEventListener('DOMContentLoaded', function() {
    // Валидация email
    const emailInput = document.getElementById('public_email');
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            validateEmail(this);
        });
    }

    // Валидация URL
    const websiteInput = document.getElementById('website');
    if (websiteInput) {
        websiteInput.addEventListener('input', function() {
            validateURL(this);
        });
    }

    // Валидация Telegram
    const telegramInput = document.getElementById('telegram');
    if (telegramInput) {
        telegramInput.addEventListener('input', function() {
            validateTelegram(this);
        });
    }

    // Валидация даты рождения
    const birthdateInput = document.getElementById('birthdate');
    if (birthdateInput) {
        birthdateInput.addEventListener('input', function() {
            validateBirthdate(this);
        });
    }

    // Счетчики символов для текстовых полей
    addCharacterCounters();
});

function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const value = input.value.trim();
    
    clearValidationMessage(input);
    
    if (value && !emailRegex.test(value)) {
        showValidationMessage(input, 'Некорректный формат email', 'error');
        return false;
    } else if (value && emailRegex.test(value)) {
        showValidationMessage(input, 'Email корректен', 'success');
        return true;
    }
    return true;
}

function validateURL(input) {
    const value = input.value.trim();
    
    clearValidationMessage(input);
    
    if (value) {
        try {
            // Добавляем протокол если его нет
            let url = value;
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                url = 'https://' + url;
                input.value = url;
            }
            
            new URL(url);
            showValidationMessage(input, 'URL корректен', 'success');
            return true;
        } catch {
            showValidationMessage(input, 'Некорректный URL', 'error');
            return false;
        }
    }
    return true;
}

function validateTelegram(input) {
    const value = input.value.trim();
    
    clearValidationMessage(input);
    
    if (value) {
        // Автоматически добавляем @ если его нет
        if (!value.startsWith('@')) {
            input.value = '@' + value;
        }
        
        const telegramRegex = /^@[a-zA-Z0-9_]{5,32}$/;
        if (!telegramRegex.test(input.value)) {
            showValidationMessage(input, 'Некорректный username Telegram (5-32 символа)', 'error');
            return false;
        } else {
            showValidationMessage(input, 'Username корректен', 'success');
            return true;
        }
    }
    return true;
}

function validateBirthdate(input) {
    const value = input.value;
    
    clearValidationMessage(input);
    
    if (value) {
        const birthDate = new Date(value);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear();
        
        if (birthDate > today) {
            showValidationMessage(input, 'Дата не может быть в будущем', 'error');
            return false;
        } else if (age > 120) {
            showValidationMessage(input, 'Проверьте корректность даты', 'error');
            return false;
        } else if (age < 13) {
            showValidationMessage(input, 'Минимальный возраст 13 лет', 'error');
            return false;
        } else {
            showValidationMessage(input, `Возраст: ${age} лет`, 'success');
            return true;
        }
    }
    return true;
}

function showValidationMessage(input, message, type) {
    clearValidationMessage(input);
    
    const messageElement = document.createElement('div');
    messageElement.className = `validation-message validation-${type}`;
    messageElement.textContent = message;
    messageElement.style.cssText = `
        font-size: 0.8em;
        margin-top: 4px;
        padding: 4px 8px;
        border-radius: 4px;
        animation: fadeIn 0.2s ease-in-out;
        ${type === 'error' ? 'color: #e74c3c; background: rgba(231,76,60,0.1);' : 'color: #27ae60; background: rgba(39,174,96,0.1);'}
    `;
    
    input.parentElement.appendChild(messageElement);
    
    // Изменяем цвет рамки поля
    if (type === 'error') {
        input.style.borderColor = '#e74c3c';
    } else {
        input.style.borderColor = '#27ae60';
    }
}

function clearValidationMessage(input) {
    const existingMessage = input.parentElement.querySelector('.validation-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Возвращаем стандартный цвет рамки
    input.style.borderColor = '#4db6e2';
}

function addCharacterCounters() {
    const fieldsWithCounters = [
        { id: 'bio', max: 500 },
        { id: 'status', max: 100 },
        { id: 'interests', max: 200 },
        { id: 'organization', max: 100 }
    ];
    
    fieldsWithCounters.forEach(field => {
        const input = document.getElementById(field.id);
        if (input) {
            const counter = document.createElement('div');
            counter.className = 'character-counter';
            counter.style.cssText = `
                font-size: 0.75em;
                color: #999;
                text-align: right;
                margin-top: 4px;
            `;
            
            const updateCounter = () => {
                const length = input.value.length;
                counter.textContent = `${length}/${field.max}`;
                
                if (length > field.max * 0.9) {
                    counter.style.color = '#e74c3c';
                } else if (length > field.max * 0.7) {
                    counter.style.color = '#f39c12';
                } else {
                    counter.style.color = '#999';
                }
            };
            
            input.addEventListener('input', updateCounter);
            input.parentElement.appendChild(counter);
            updateCounter();
        }
    });
}

// Функция для проверки всех полей перед отправкой
function validateAllFields() {
    const emailValid = validateEmail(document.getElementById('public_email'));
    const urlValid = validateURL(document.getElementById('website'));
    const telegramValid = validateTelegram(document.getElementById('telegram'));
    const birthdateValid = validateBirthdate(document.getElementById('birthdate'));
    
    return emailValid && urlValid && telegramValid && birthdateValid;
}

// Добавляем обработчик на форму
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.profile-edit-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateAllFields()) {
                e.preventDefault();
                alert('Пожалуйста, исправьте ошибки в форме перед сохранением');
            }
        });
    }
}); 