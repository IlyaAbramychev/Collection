#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности индивидуальных стен
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_walls():
    """Тестируем функциональность стен"""
    
    print("=== Тестирование индивидуальных стен ===\n")
    
    # 1. Проверяем главную страницу
    print("1. Проверяем главную страницу...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Главная страница доступна")
        else:
            print("   ✗ Главная страница недоступна")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 2. Проверяем общую стену
    print("\n2. Проверяем общую стену...")
    try:
        response = requests.get(f"{BASE_URL}/wall")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Общая стена доступна")
        elif response.status_code == 302:
            print("   ✓ Общая стена перенаправляет на регистрацию (ожидаемо)")
        else:
            print("   ✗ Общая стена недоступна")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 3. Проверяем несуществующую индивидуальную стену
    print("\n3. Проверяем несуществующую индивидуальную стену...")
    try:
        response = requests.get(f"{BASE_URL}/user/nonexistent_user")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Перенаправление на регистрацию (ожидаемо)")
        else:
            print("   ✗ Неожиданный статус")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n=== Тест завершен ===")
    print("\nДля полного тестирования нужно:")
    print("1. Зарегистрироваться на сайте")
    print("2. Создать несколько постов")
    print("3. Перейти на /user/<username> для проверки индивидуальной стены")
    print("4. Проверить, что посты отображаются только для конкретного пользователя")

if __name__ == "__main__":
    test_walls() 