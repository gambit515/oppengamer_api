import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ContextTypes
import DB2
from DB2 import is_authorized_user, get_user_by_telegram_id

# Версия бота
bot_version = "0.0.4"

# ID администратора
admin_ids = [1170089312, 1764899079]

# Глобальные переменные
present_list = []
state_machine = 0
message_thread_id = 0
target_chat_id = 0
student_list_id = 0
message_list_ids = set()

# Список всех пользователей
all_users = [
    "артеменко никита", "банзаракцаев золто", "бережных илья",
    "вирчик кирилл", "герасимчук аделина", "гузанов иван", "гусев юрий", "дмитриев кирилл",
    "доброхотов данила", "есиков глеб", "желтоухов владимир", "козлов тимофей",
    "колмачихина дарья", "кунов максим", "кырова влада", "марковцова дарья",
    "мартын златослава", "медведев дмитрий", "меркулов сергей", "петрянин евгений", "рома", "суркова анастасия",
    "терещенко никита", "филиппов никита", "хавроничева екатерина", "хозяев богдан",
    "хребтов дмитрий", "черных егор", "чуприкова анна", "швец анна"
]


def get_current_group_id(chat_id):
    """
    Возвращает ID группы, связанной с указанным chat_id.
    Если группа не найдена, возвращает None.
    """
    groups_url = "http://gambitcorporation.ru:8001/api/students/groups/"
    response = requests.get(groups_url)

    if response.status_code != 200:
        print(f"Ошибка при получении списка групп: {response.text}")
        return None

    groups = response.json()
    target_group = next((group for group in groups if group.get("chat") == chat_id), None)

    if target_group:
        return target_group["id"]
    return None


def send_message(text, context_arg: CallbackContext, chat_id=None, **kwargs):
    """
    Функция для отправки сообщения.
    Если `chat_id` не указан, используется `target_chat_id` по умолчанию.
    """
    global target_chat_id
    if chat_id is None:
        chat_id = target_chat_id

    try:
        message = context_arg.bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return message.message_id
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return None


def open_list(context: CallbackContext):
    text = 'Начинаем сбор списка присутствующих. Пожалуйста, напишите свое фамилию и имя. Закрытие сбора через час!'
    start_attendance_function(target_chat_id, context, text)


def close_list(context: CallbackContext):
    close_list_fucntion(target_chat_id, context)


def activation(update: Update, context: CallbackContext):
    # Получаем текст после команды `/activation`
    args = context.args

    if args:
        # Объединяем аргументы в строку, если есть текст после команды
        phone_text = " ".join(args)
        # Вызываем функцию активации пользователя в базе данных
        success = DB2.activate_user(phone_text, update.effective_user.id)
        if success:
            update.message.reply_text("Учётка успешно активирована")
        else:
            update.message.reply_text("При активации учётки произошла ошибка")
    else:
        update.message.reply_text("Пожалуйста, введите данные после команды /activate.")


def close_list_fucntion(target_chat_id, context):
    global state_machine
    if state_machine == 1:
        state_machine = 0

        for msg_id in message_list_ids:
            try:
                context.bot.delete_message(
                    chat_id=target_chat_id,
                    message_id=msg_id
                )
            except Exception as e:
                print(f"Ошибка при удалении сообщения {msg_id}: {e}")

        absent_list = [user for user in all_users if user not in present_list]

        present_str = '\n'.join(present_list) if present_list else "Никто не отметился."
        absent_str = '\n'.join(absent_list) if absent_list else "Все присутствуют."

        # Отправка результатов
        send_message(f"Присутствующие:\n{present_str}\n\nОтсутствующие:\n{absent_str}", chat_id=target_chat_id,
                     context_arg=context)


def bot_refresh(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id in admin_ids:
        global present_list, student_list_id, message_list_ids, state_machine
        present_list = []
        student_list_id = 0
        message_list_ids = set()
        state_machine = 0
        send_message("Перезапуск завершён", chat_id=update.message.chat_id, context_arg=context)
    else:
        send_message('Пошёл %@!^#^&!@ (без негатива)', context_arg=context, chat_id=update.message.chat_id)


def start_attendance(update: Update, context: CallbackContext) -> None:
    global state_machine
    message_list_ids.add(update.message.message_id)
    if state_machine == 0:
        if update.effective_user.id in admin_ids:
            start_attendance_function(update.message.chat_id, context)
        else:
            send_message(text='Пошёл %@!^#^&!@ (без негатива)', chat_id=update.message.chat_id, context_arg=context)
    else:
        send_message(text='State machine error блин', chat_id=update.message.chat_id, context_arg=context)


# Функция для регистрации присутствующих
def register_user(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if state_machine == 1:
        if update.message.reply_to_message and update.message.reply_to_message.message_id == student_list_id:
            user_input = update.message.text.lower()

            if user_input == "+":
                telegram_id = update.effective_user.id
                chat_id = update.message.chat_id  # Получаем chat_id текущего чата
                group_id = get_current_group_id(chat_id)  # Находим группу по chat_id

                if not group_id:
                    send_message("Группа для этого чата не установлена.", context_arg=context, chat_id=chat_id)
                    return

                # Проверяем авторизацию пользователя через API
                auth_url = f"http://gambitcorporation.ru:8001/api/students/is_authorized/{telegram_id}/"
                auth_response = requests.get(auth_url)

                if auth_response.status_code != 200:
                    send_message("Ошибка при проверке авторизации.", context_arg=context, chat_id=chat_id)
                    return

                is_authorized = auth_response.json().get("is_authorized", False)
                if not is_authorized:
                    send_message("Вы не авторизованы.", context_arg=context, chat_id=chat_id)
                    return

                # Получаем информацию о пользователе через API
                user_url = f"http://gambitcorporation.ru:8001/api/students/student/{telegram_id}/"
                user_response = requests.get(user_url)

                if user_response.status_code != 200:
                    send_message("Пользователь не найден.", context_arg=context, chat_id=chat_id)
                    return

                user_data = user_response.json()
                surname_name = f"{user_data['surname']} {user_data['name']}".lower()

                # Проверяем, был ли пользователь уже отмечен
                attendance_url = f"http://gambitcorporation.ru:8001/api/students/attendance/{group_id}/"
                attendance_response = requests.get(attendance_url)

                if attendance_response.status_code != 200:
                    send_message("Ошибка при проверке списка присутствующих.", context_arg=context, chat_id=chat_id)
                    return

                # Проверяем, есть ли пользователь в ответе API
                already_present = any(
                    record["student"] == user_data["student_id"] for record in attendance_response.json()
                )

                if already_present:
                    send_message(f"{surname_name} уже отмечен в списке присутствующих.", context_arg=context, chat_id=chat_id)
                    return

                # Отправляем запрос на регистрацию присутствия через API
                attendance_create_url = "http://gambitcorporation.ru:8001/api/students/attendance/"
                attendance_data = {
                    "student_id": user_data["student_id"],
                    "group_id": group_id  # Используем найденный group_id
                }
                attendance_response = requests.post(attendance_create_url, json=attendance_data)

                if attendance_response.status_code == 201:
                    send_message(f"{surname_name} добавлен в список присутствующих.", context_arg=context, chat_id=chat_id)
                else:
                    send_message("Ошибка при добавлении в список присутствующих.", context_arg=context, chat_id=chat_id)
            else:
                send_message("Некорректный ввод.", context_arg=context, chat_id=chat_id)


# Команда для завершения списка и публикации
def finalize_list(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if update.effective_user.id in admin_ids:

        group_id = get_current_group_id(chat_id)  # Находим группу по chat_id

        if not group_id:
            send_message("Группа для этого чата не установлена.", context_arg=context, chat_id=chat_id)
            return

        # Получаем список присутствующих через API
        attendance_url = f"http://gambitcorporation.ru:8001/api/students/attendance/{group_id}/"
        attendance_response = requests.get(attendance_url)

        if attendance_response.status_code != 200:
            send_message("Ошибка при получении списка присутствующих.", context_arg=context, chat_id=chat_id)
            return

        attendance_data = attendance_response.json()

        clear_attendance_url = f"http://gambitcorporation.ru:8001/api/students/attendance/{group_id}/clear/"
        clear_response = requests.post(clear_attendance_url)

        if clear_response.status_code != 200:
            send_message("Ошибка при очистке предыдущих записей о присутствии.", context_arg=context, chat_id=chat_id)
            return

        present_students = []
        for record in attendance_data:
            student_id = record.get("student")
            if student_id:
                # Дополнительный запрос для получения информации о студенте
                student_url = f"http://gambitcorporation.ru:8001/api/students/student/id/{student_id}/"
                student_response = requests.get(student_url)

                if student_response.status_code == 200:
                    student_data = student_response.json()
                    present_students.append(f"{student_data['surname']} {student_data['name']}")
                else:
                    print(f"Не удалось получить информацию о студенте с ID {student_id}")

        # Получаем список всех студентов в группе
        all_students_url = f"http://gambitcorporation.ru:8001/api/students/group/{group_id}/students/"
        all_students_response = requests.get(all_students_url)

        if all_students_response.status_code != 200:
            send_message("Ошибка при получении списка студентов.", context_arg=context, chat_id=chat_id)
            return

        all_students = [
            f"{student['surname']} {student['name']}" for student in all_students_response.json()
        ]

        absent_students = list(set(all_students) - set(present_students))

        present_str = '\n'.join(present_students) if present_students else "Никто не отметился."
        absent_str = '\n'.join(absent_students) if absent_students else "Все присутствуют."

        # Отправка результатов
        send_message(
            f"Присутствующие:\n{present_str}\n\nОтсутствующие:\n{absent_str}",
            context_arg=context,
            chat_id=chat_id
        )
    else:
        send_message('Пошёл %@!^#^&!@ (без негатива)', context_arg=context, chat_id=chat_id)


def bot_init_schedule_channel(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if update.effective_user.id in admin_ids:
        group_name = context.args[0] if context.args else None  # Получаем имя группы из аргументов команды

        if not group_name:
            send_message("Пожалуйста, укажите имя группы после команды /init_schedule_channel.", context_arg=context,
                         chat_id=chat_id)
            return

        # Получаем список всех групп через API
        groups_url = "http://gambitcorporation.ru:8001/api/students/groups/"
        response = requests.get(groups_url)

        if response.status_code != 200:
            send_message(f"Ошибка при получении списка групп: {response.text}", context_arg=context, chat_id=chat_id)
            return

        groups = response.json()
        target_group = next((group for group in groups if group["name"].lower() == group_name.lower()), None)

        if not target_group:
            send_message(f"Группа '{group_name}' не найдена.", context_arg=context, chat_id=chat_id)
            return

        # Обновляем chat_id группы через PATCH-запрос
        group_id = target_group["id"]
        update_url = f"http://gambitcorporation.ru:8001/api/students/group/{group_id}/"
        update_data = {"chat": chat_id}
        update_response = requests.patch(update_url, json=update_data)

        if update_response.status_code == 200:
            send_message(f"Канал расписания успешно установлен для группы {group_name}.", context_arg=context,
                         chat_id=chat_id)
        else:
            send_message(f"Ошибка при обновлении группы: {update_response.text}", context_arg=context, chat_id=chat_id)
    else:
        send_message('Пошёл %@!^#^&!@ (без негатива)', context_arg=context, chat_id=chat_id)


def start_attendance_function(chat_id, context, text='Начинаем сбор списка присутствующих. Пожалуйста, напишите свое '
                                                     'фамилию и имя.'):
    global state_machine
    state_machine = 1
    present_list.clear()
    global student_list_id
    student_list_id = send_message(text, chat_id=chat_id, context_arg=context)
    message_list_ids.add(student_list_id)


def close_list_fucntion(target_chat_id, context: CallbackContext):
    """
    Закрытие списка и публикация присутствующих/отсутствующих.
    """
    global state_machine, present_list, message_list_ids
    if state_machine == 1:
        state_machine = 0

        for msg_id in message_list_ids:
            try:
                context.bot.delete_message(
                    chat_id=target_chat_id,
                    message_id=msg_id
                )
            except Exception as e:
                print(f"Ошибка при удалении сообщения {msg_id}: {e}")

        absent_list = [user for user in all_users if user not in present_list]

        present_str = '\n'.join(present_list) if present_list else "Никто не отметился."
        absent_str = '\n'.join(absent_list) if absent_list else "Все присутствуют."

        # Отправка результатов
        send_message(f"Присутствующие:\n{present_str}\n\nОтсутствующие:\n{absent_str}", chat_id=target_chat_id,
                     context_arg=context)
