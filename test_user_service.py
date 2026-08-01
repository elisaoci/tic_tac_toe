from di.container import Container

container = Container()

# Тест 1: Регистрация нового пользователя
print("=== Тест 1: Регистрация ===")
success = container.user_service.register("diana", "my_password_123")
print(f"Регистрация успешна? {success}")  # Должно быть True

# Тест 2: Попытка зарегистрировать того же пользователя
print("\n=== Тест 2: Повторная регистрация ===")
success = container.user_service.register("diana", "another_password")
print(f"Регистрация успешна? {success}")  # Должно быть False (логин занят)

# Тест 3: Аутентификация с правильным паролем
print("\n=== Тест 3: Правильный пароль ===")
uuid = container.user_service.authenticate("diana", "my_password_123")
print(f"UUID пользователя: {uuid}")  # Должен быть UUID

# Тест 4: Аутентификация с неправильным паролем
print("\n=== Тест 4: Неправильный пароль ===")
uuid = container.user_service.authenticate("diana", "wrong_password")
print(f"UUID пользователя: {uuid}")  # Должно быть None

# Тест 5: Получение пользователя по UUID
print("\n=== Тест 5: Получение по UUID ===")
if uuid:
    user = container.user_service.get_user_by_uuid(uuid)
    print(f"Логин: {user.login}")  # Должно быть "diana"