import json

def save_ban_list(ban_list, filename="banned_users.json"):
    with open(filename, "w") as file:
        json.dump(ban_list, file)
    file.close()
    print(f"Список забаненных пользователей сохранен в файл {filename}.")

# Функция для загрузки списка забаненных пользователей из файла
def load_ban_list(filename="banned_users.json"):
    try:
        with open(filename, "r") as file:
            ban_list = json.load(file)
        file.close()
        return ban_list
    except FileNotFoundError:
        return []

# Функция для добавления ID пользователя в список забаненных
def ban_user(user_id):
    ban_list = load_ban_list()
    if user_id not in ban_list:
        ban_list.append(user_id)
        print(f"Пользователь с ID {user_id} был забанен.")
    else:
        print(f"Пользователь с ID {user_id} уже забанен.")
    save_ban_list(ban_list)

# Функция для удаления ID пользователя из списка забаненных (разбан)
def unban_user(user_id):
    ban_list = load_ban_list()
    if user_id in ban_list:
        ban_list.remove(user_id)
        print(f"Пользователь с ID {user_id} был разбанен.")
    else:
        print(f"Пользователь с ID {user_id} не найден в списке забаненных.")
    save_ban_list(ban_list)

def check_ban(user_id):
    print(user_id)
    ban_list = load_ban_list()
    if user_id in ban_list:
        return "ban"
    else:
        return "no"




