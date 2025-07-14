import sqlite3

def add_visibility_flags():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    # Список флагов для добавления
    flags = [
        'show_status',
        'show_bio',
        'show_full_name',
        'show_degree',
        'show_interests',
        'show_organization',
        'show_location',
        'show_scholar_links',
        'show_website',
        'show_birthdate',
        'show_public_email',
        'show_telegram'
    ]
    
    # Добавляем каждый флаг
    for flag in flags:
        try:
            c.execute(f'ALTER TABLE user ADD COLUMN {flag} BOOLEAN DEFAULT 1')
            print(f'Added column {flag}')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'Column {flag} already exists')
            else:
                print(f'Error adding {flag}: {e}')
    
    conn.commit()
    conn.close()
    print('Finished adding visibility flags')

if __name__ == '__main__':
    add_visibility_flags() 