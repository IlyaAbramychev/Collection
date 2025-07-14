// Автосохранение черновиков профиля
class ProfileAutosave {
    constructor() {
        this.storageKey = 'profile_draft';
        this.saveInterval = 3000; // 3 секунды
        this.fields = [
            'full_name', 'status', 'bio', 'birthdate', 'location',
            'degree', 'organization', 'interests', 'scholar_links',
            'public_email', 'telegram', 'website'
        ];
        this.visibilityFields = [
            'show_full_name', 'show_status', 'show_bio', 'show_birthdate', 'show_location',
            'show_degree', 'show_organization', 'show_interests', 'show_scholar_links',
            'show_public_email', 'show_telegram', 'show_website'
        ];
        this.lastSaved = null;
        this.isDirty = false;
        
        this.init();
    }
    
    init() {
        // Загружаем черновик при открытии модального окна
        document.getElementById('editProfileBtn').addEventListener('click', () => {
            setTimeout(() => this.loadDraft(), 100);
        });
        
        // Сохраняем при изменении полей
        this.fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => this.markDirty());
            }
        });
        
        this.visibilityFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', () => this.markDirty());
            }
        });
        
        // Автосохранение каждые 3 секунды
        setInterval(() => {
            if (this.isDirty) {
                this.saveDraft();
            }
        }, this.saveInterval);
        
        // Сохраняем при закрытии модального окна
        document.getElementById('closeEditModal').addEventListener('click', () => this.saveDraft());
        document.getElementById('closeEditModalX').addEventListener('click', () => this.saveDraft());
        
        // Очищаем черновик при успешном сохранении
        document.querySelector('.profile-edit-form').addEventListener('submit', () => {
            this.clearDraft();
        });
        
        // Показываем уведомление о восстановлении черновика
        this.showDraftNotification();
    }
    
    markDirty() {
        this.isDirty = true;
        this.updateSaveIndicator('Несохранено');
    }
    
    saveDraft() {
        if (!this.isDirty) return;
        
        const draft = {};
        
        // Сохраняем значения полей
        this.fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                draft[fieldId] = field.value;
            }
        });
        
        // Сохраняем состояние чекбоксов
        this.visibilityFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                draft[fieldId] = field.checked;
            }
        });
        
        // Сохраняем текущую активную вкладку
        const activeTab = document.querySelector('.profile-edit-tab.active');
        if (activeTab) {
            draft.activeTab = activeTab.dataset.section;
        }
        
        draft.timestamp = Date.now();
        
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(draft));
            this.lastSaved = Date.now();
            this.isDirty = false;
            this.updateSaveIndicator('Сохранено');
        } catch (error) {
            console.error('Ошибка при сохранении черновика:', error);
        }
    }
    
    loadDraft() {
        try {
            const draftData = localStorage.getItem(this.storageKey);
            if (!draftData) return;
            
            const draft = JSON.parse(draftData);
            
            // Проверяем, не слишком ли старый черновик (более 24 часов)
            const dayInMs = 24 * 60 * 60 * 1000;
            if (Date.now() - draft.timestamp > dayInMs) {
                this.clearDraft();
                return;
            }
            
            // Восстанавливаем значения полей
            this.fields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field && draft[fieldId] !== undefined) {
                    field.value = draft[fieldId];
                }
            });
            
            // Восстанавливаем состояние чекбоксов
            this.visibilityFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field && draft[fieldId] !== undefined) {
                    field.checked = draft[fieldId];
                }
            });
            
            // Восстанавливаем активную вкладку
            if (draft.activeTab) {
                const tab = document.querySelector(`[data-section="${draft.activeTab}"]`);
                if (tab) {
                    tab.click();
                }
            }
            
            this.showDraftRestoredNotification();
            
        } catch (error) {
            console.error('Ошибка при загрузке черновика:', error);
            this.clearDraft();
        }
    }
    
    clearDraft() {
        try {
            localStorage.removeItem(this.storageKey);
            this.isDirty = false;
            this.updateSaveIndicator('');
        } catch (error) {
            console.error('Ошибка при очистке черновика:', error);
        }
    }
    
    updateSaveIndicator(text) {
        let indicator = document.querySelector('.autosave-indicator');
        
        if (!indicator && text) {
            indicator = document.createElement('div');
            indicator.className = 'autosave-indicator';
            indicator.style.cssText = `
                position: absolute;
                top: 16px;
                right: 60px;
                font-size: 0.8em;
                color: #666;
                background: rgba(255,255,255,0.9);
                padding: 4px 8px;
                border-radius: 4px;
                transition: all 0.2s;
                z-index: 10;
            `;
            
            const header = document.querySelector('.profile-edit-header');
            if (header) {
                header.style.position = 'relative';
                header.appendChild(indicator);
            }
        }
        
        if (indicator) {
            indicator.textContent = text;
            
            if (text === 'Сохранено') {
                indicator.style.color = '#27ae60';
                setTimeout(() => {
                    if (indicator.textContent === 'Сохранено') {
                        indicator.textContent = '';
                    }
                }, 2000);
            } else if (text === 'Несохранено') {
                indicator.style.color = '#f39c12';
            }
        }
    }
    
    showDraftNotification() {
        const draftData = localStorage.getItem(this.storageKey);
        if (!draftData) return;
        
        try {
            const draft = JSON.parse(draftData);
            const dayInMs = 24 * 60 * 60 * 1000;
            
            if (Date.now() - draft.timestamp < dayInMs) {
                const notification = document.createElement('div');
                notification.className = 'draft-notification';
                notification.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px; background: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 12px; margin: 16px 0; font-size: 0.9em;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2196f3" stroke-width="2">
                            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                            <polyline points="17,21 17,13 7,13 7,21"></polyline>
                            <polyline points="7,3 7,8 15,8"></polyline>
                        </svg>
                        <span style="flex: 1; color: #1976d2;">Найден несохраненный черновик профиля</span>
                        <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: #666; cursor: pointer; font-size: 1.2em;">×</button>
                    </div>
                `;
                
                const form = document.querySelector('.profile-edit-form');
                if (form) {
                    form.insertBefore(notification, form.firstChild);
                }
            }
        } catch (error) {
            console.error('Ошибка при показе уведомления о черновике:', error);
        }
    }
    
    showDraftRestoredNotification() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 0.9em;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = 'Черновик восстановлен';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Добавляем CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Инициализируем автосохранение
document.addEventListener('DOMContentLoaded', function() {
    new ProfileAutosave();
}); 