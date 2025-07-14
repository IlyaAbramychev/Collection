#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы подписок и поиска пользователей
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_follow_system():
    """Тестируем систему подписок и поиска"""
    
    print("=== Тестирование системы подписок и поиска ===\n")
    
    # 1. Проверяем страницу поиска
    print("1. Проверяем страницу поиска пользователей...")
    try:
        response = requests.get(f"{BASE_URL}/search")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Страница поиска доступна")
        elif response.status_code == 302:
            print("   ✓ Страница поиска перенаправляет на регистрацию (ожидаемо)")
        else:
            print("   ✗ Страница поиска недоступна")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 2. Проверяем API поиска пользователей
    print("\n2. Проверяем API поиска пользователей...")
    try:
        response = requests.get(f"{BASE_URL}/search/users?q=test")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ API требует авторизации (ожидаемо)")
        else:
            print("   ✗ Неожиданный статус")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 3. Проверяем API подписки
    print("\n3. Проверяем API подписки...")
    try:
        response = requests.post(f"{BASE_URL}/follow/test_user")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ API подписки требует авторизации (ожидаемо)")
        else:
            print("   ✗ Неожиданный статус")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 4. Проверяем API отписки
    print("\n4. Проверяем API отписки...")
    try:
        response = requests.post(f"{BASE_URL}/unfollow/test_user")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ API отписки требует авторизации (ожидаемо)")
        else:
            print("   ✗ Неожиданный статус")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n=== Тест завершен ===")
    print("\nДля полного тестирования нужно:")
    print("1. Зарегистрироваться на сайте")
    print("2. Создать несколько пользователей")
    print("3. Протестировать поиск пользователей на /search")
    print("4. Протестировать подписку/отписку")
    print("5. Проверить отображение подписчиков/подписок в профиле")

if __name__ == "__main__":
    test_follow_system() 