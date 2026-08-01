from datasource.model.user_model import UserModel

# 1. Создаем пользователя
user = UserModel()
user.uuid = "test-uuid-123"
user.login = "diana"

# 2. Устанавливаем пароль (он автоматически захешируется!)
user.set_password("my_super_secret_password")

print(f"Логин: {user.login}")
print(f"Хеш в базе: {user.hashed_password}")

# 3. Проверяем правильный пароль
is_correct = user.check_password("my_super_secret_password")
print(f"Пароль 'my_super_secret_password' верный? {is_correct}") # Должно быть True

# 4. Проверяем неправильный пароль
is_wrong = user.check_password("wrong_password")
print(f"Пароль 'wrong_password' верный? {is_wrong}") # Должно быть False