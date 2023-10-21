import flask
import conf
import telebot
from telebot import types
import sqlite3
import pytz
import datetime
import re
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import json

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

menu = '1. Американо 200 мл – 80 ₽\n2. Американо 300 мл – 100 ₽\n3. Капучино 200 мл – 120 ₽\n4. Капучино 300 мл – 170 ₽\n5. Капучино 400 мл – 200 ₽\n6. Латте 300 мл – 120 ₽\n7. Латте 400 мл – 170 ₽\n8. БейбиЧино 100 мл – 50 ₽\n9. Чёрный чай с лемонграссом, мятой и цедрой лимона 300 мл – 50 ₽\n10. Зелёный чай с кусочками клубники, вишни, красной и чёрной смородины 300 мл – 50 ₽\n11.Иван-чай со смородиной 300 мл – 50 ₽\n12. Сок яблочный 200 мл – 50 ₽\n13. Пряник 190 гр – 120 ₽\n14. Шоколад 5 гр – 10 ₽'
menu_items = {
    'Американо 200 мл': 1,
    'Американо 300 мл': 2,
    'Капучино 200 мл': 3,
    'Капучино 300 мл': 4,
    'Капучино 400 мл': 5,
    'Латте 300 мл': 6,
    'Латте 400 мл': 7,
    'БейбиЧино 100 мл': 8,
    'Чёрный чай с лемонграссом, мятой и цедрой лимона 300 мл': 9,
    'Зелёный чай с кусочками клубники, вишни, красной и чёрной смородины 300 мл': 10,
    'Иван-чай со смородиной 300 мл': 11,
    'Сок яблочный 200 мл': 12,
    'Пряник 190 гр': 13,
    'Шоколад 5 гр': 14,
}

menu_items_inverse = {
	1: 80,
	2: 100,
	3: 120,
	4: 170,
	5: 200,
	6: 120,
	7: 170,
	8: 50,
	9: 50,
	10: 50,
	11: 50,
	12: 50,
	13: 120,
	14: 10,
}


owners = {"OWNERNAME": "OWNER_ID"}

# Create a dictionary to store authorized users' usernames or user IDs
authorized_users = {"OWNERNAME": "OWNER_ID"}

# Create a file path for your JSON file
user_data_file = 'mysite/user_data.json'

# Function to save user data to a JSON file
def save_user_data():
    data = {
        "authorized_users": authorized_users,
        "owners": owners
    }
    with open(user_data_file, 'w') as file:
        json.dump(data, file, indent=4)

# Function to load user data from the JSON file
def load_user_data():
    try:
        with open(user_data_file, 'r') as file:
            data = json.load(file)
            return data.get("authorized_users", {}), data.get("owners", {})
    except FileNotFoundError:
        return {}, {}  # Return empty dictionaries if the file doesn't exist

# Initialize the authorized_users and owners dictionaries by loading from the JSON file
authorized_users, owners = load_user_data()


def is_user_authorized(user_id):
    return user_id in list(authorized_users.values())

def get_access(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    if not is_user_authorized(user_id):
        # Create an inline keyboard for granting access
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подтвердить", callback_data=f"allow_{user_id}_{user_name}"))
        markup.add(types.InlineKeyboardButton("Отклонить", callback_data=f"decline_{user_id}_{user_name}"))

        # Send a message with the inline keyboard
        for owner in owners:
            bot.send_message(
                chat_id=owners[owner],
              text=f"Пользователь с именем @{user_name} (id пользователя: {user_id}) хочет воспользоваться ботом. Подтвердить или отклонить?",
              reply_markup=markup
            )
        bot.send_message(message.chat.id, "Извините, но у Вас нет доступа к боту. Запрос на использование бота отправлен владельцу бота.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("allow") or call.data.startswith("decline"))
def callback_handler(message):
    user_id = int(message.data.split("_")[1])
    user_name = message.data.split("_")[2]
    if message.data.startswith("allow"):
        authorized_users[user_name] = user_id  # Add the user to the authorized_users dictionary
        save_user_data()  # Save the updated dictionaries to the JSON file
        bot.send_message(message.from_user.id, "Доступ предоставлен.")
        bot.send_message(user_id, "Доступ предоставлен! Теперь Вы можете пользоваться ботом. Введите нужную команду.")
    elif message.data.startswith("decline"):
        bot.send_message(message.from_user.id, "Пользователю отказано в доступе.")
        bot.send_message(user_id, "Извините, Вам отказано в доступе.")


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Здравствуйте! \n\nНапишите /help, чтобы узнать о всех возможностях нашего телеграм-бота.')


@bot.message_handler(commands=["help"])
def help(message):
	bot.send_message(message.chat.id, 'Чтобы добавить новый заказ, введите /neworder.\nЧтобы изменить цену позиции в меню, введите /change.\nЧтобы добавить новую позицию, введите /add.\nЧтобы удалить старую позицию, введите /delete.\nЧтобы получить статистику за день, введите /todaystatistics.\nЧтобы получить статистику за месяц, введите /monthstatistics.\nЧтобы получить статистику за нужный период, введите /periodstatistics.')


order_sum = 0
order_items = {}

@bot.message_handler(commands=["neworder"])
def order(message):
    if is_user_authorized(message.from_user.id):
        global order_sum
        order_sum = 0
        global order_items
        order_items = {}
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item_buttons = [types.KeyboardButton(item) for item in menu_items.keys()]
        markup.add(*item_buttons)
        msg = bot.send_message(message.chat.id, 'Выберите позицию из меню:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_selected_item)
    else:
        get_access(message)

def process_selected_item(message):
    selected_item = message.text
    if selected_item in menu_items:
        global selected_item_id
        selected_item_id = menu_items[selected_item]  # Store the selected item's ID

        # Create a custom keyboard for quantity selection
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        quantity_buttons = [types.KeyboardButton(str(i)) for i in range(1, 11)]  # Let the user select quantities from 1 to 10
        markup.add(*quantity_buttons)

        msg = bot.send_message(message.chat.id, f'Выбрано: {selected_item}. Выберите количество:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_quantity)
    else:
        bot.send_message(message.chat.id, 'Выберите пожалуйста позицию из меню.')

def process_quantity(message):
    try:
        quantity = int(message.text)
        order_items[selected_item_id] = quantity  # Store the selected item and its quantity
        global order_sum
        order_sum += menu_items_inverse[selected_item_id] * quantity  # Update the order_sum
        markup = types.ReplyKeyboardRemove()  # Remove the custom keyboard

        # Create buttons for choosing the step
        confirmation_buttons = [types.KeyboardButton("Да"), types.KeyboardButton("Нет")]
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(*confirmation_buttons)

        msg = bot.send_message(message.chat.id, f'Сумма заказа: {str(order_sum)}. Добавить еще позицию в заказ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_continue_step)  # Register for the next step
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное количество (целое число).')

def process_continue_step(message):
    try:
        if message.text.lower() == 'да':
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)  # Create custom keyboard
            item_buttons = [types.KeyboardButton(item) for item in menu_items.keys()]
            markup.add(*item_buttons)
            msg = bot.send_message(message.chat.id, 'Выберите еще одну позицию из меню:', reply_markup=markup)
            bot.register_next_step_handler(msg, process_selected_item)
        elif message.text.lower() == 'нет':
            # Ask for confirmation before saving the order
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            confirm_buttons = [types.KeyboardButton("Подтвердить"), types.KeyboardButton("Отменить")]
            markup.add(*confirm_buttons)
            msg = bot.send_message(message.chat.id, f'Итоговая сумма заказа: {str(order_sum)}. Подтвердите заказ или отмените его:', reply_markup=markup)
            bot.register_next_step_handler(msg, process_confirmation)
        else:
            msg = bot.send_message(message.chat.id, 'Пожалуйста, выберите "Да" или "Нет".')
            bot.register_next_step_handler(msg, process_continue_step)
    except Exception as e:
        print("Error processing continue step:", e)  # Debug print

def process_confirmation(message):
    markup = types.ReplyKeyboardRemove()  # Remove the custom keyboard
    if message.text.lower() == 'подтвердить':
        conn = sqlite3.connect('mysite/cafe.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO orders (sum, created) VALUES (?, ?)", (order_sum, _get_now_formatted()))
        conn.commit()

        # Add information about each item in the order to the items_orders table
        order_id = cur.lastrowid
        for item_id, quantity in order_items.items():
            cur.execute("INSERT INTO items_orders (item_id, amount, order_id) VALUES (?, ?, ?)", (item_id, quantity, order_id))
        conn.commit()

        conn.close()
        bot.send_message(message.chat.id, 'Заказ подтвержден и сохранен в базу данных.', reply_markup=markup)
    elif message.text.lower() == 'отменить':
        bot.send_message(message.chat.id, 'Заказ отменен.', reply_markup=markup)
    else:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, выберите "Подтвердить" или "Отменить".')
        bot.register_next_step_handler(msg, process_confirmation)


@bot.message_handler(commands=["change"])
def change(message):
    if is_user_authorized(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item_buttons = [types.KeyboardButton(item) for item in menu_items.keys()]
        markup.add(*item_buttons)
        markup.add(types.KeyboardButton("Отмена"))  # Add a "Cancel" button
        msg = bot.send_message(message.chat.id, 'Выберите позицию из меню для изменения цены:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_selected_item_for_price_change)
    else:
        get_access(message)

def process_selected_item_for_price_change(message):
    selected_item = message.text
    markup = types.ReplyKeyboardRemove()  # Remove the custom keyboard
    if selected_item == "Отмена":
        bot.send_message(message.chat.id, 'Изменение цены отменено.', reply_markup=markup)
    elif selected_item in menu_items:
        global selected_item_id
        selected_item_id = menu_items[selected_item]
        msg = bot.send_message(message.chat.id, f'Выбрано: {selected_item}. Введите новую цену:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_new_price)
    else:
        bot.send_message(message.chat.id, 'Выберите пожалуйста позицию из меню.')

def process_new_price(message):
    try:
        new_price = int(message.text)
        conn = sqlite3.connect('mysite/cafe.db')
        cur = conn.cursor()
        cur.execute("UPDATE items SET price = ? WHERE id = ?", (new_price, selected_item_id))
        conn.commit()
        cur.execute("SELECT item, volume, price FROM items WHERE id = ?", (selected_item_id,))
        item, volume, price = cur.fetchone()
        conn.close()
        bot.send_message(message.chat.id, f'Цена товара успешно изменена. Теперь {item} {volume} стоит {new_price}.')
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректную цену (целое число).')
        msg = bot.send_message(message.chat.id, 'Введите новую цену:')
        bot.register_next_step_handler(msg, process_new_price)


@bot.message_handler(commands=["add"])
def add(message):
    if is_user_authorized(message.from_user.id):
        msg = bot.send_message(message.chat.id, f'{menu}\n\nВведите полное название новой позиции, объем (если нужно) и цену через пробел.')
        bot.register_next_step_handler(msg, process_add_step)
    else:
        get_access(message)

def process_add_step(message):
	res = re.match(r'([А-яЁё,\- ]+) ((\d+)[А-я₽\. ]+)((\d+)[А-я₽\. ]+)*', message.text)
	global item
	global volume
	global price
	print(res)
	print(res.groups())
	if res.group(4):
		item, volume, price = res.group(1), res.group(2).strip(), res.group(5)
	else:
		item, price = res.group(1), res.group(3)
		volume = None
	print(item, volume, price, sep=' + ')

	# Create buttons for choosing the step
	confirmation_buttons = [types.KeyboardButton("Да"), types.KeyboardButton("Нет")]
	markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
	markup.add(*confirmation_buttons)

	msg = bot.send_message(message.chat.id, 'Вы действительно хотите добавить новую позицию?', reply_markup=markup)
	bot.register_next_step_handler(msg, process_confirm_step)

def process_confirm_step(message):
	markup = types.ReplyKeyboardRemove()  # Remove the custom keyboard
	if message.text.lower() == 'да':
		conn = sqlite3.connect('mysite/cafe.db')
		cur = conn.cursor()
		cur.execute("INSERT INTO items (item, volume, price) VALUES (?, ?, ?)", (item, volume, price))
		conn.commit()
		conn.close()
		bot.send_message(message.chat.id, 'Новый товар успешно добавлен.', reply_markup=markup)
	elif message.text.lower() == 'нет':
		bot.send_message(message.chat.id, 'Меню осталось прежним.', reply_markup=markup)
	else:
		msg = bot.send_message(message.chat.id, 'Введите "Да" или "Нет".')
		bot.register_next_step_handler(msg, process_confirm_step)


@bot.message_handler(commands=["delete"])
def delete(message):
    if is_user_authorized(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item_buttons = [types.KeyboardButton(item) for item in menu_items.keys()]
        markup.add(*item_buttons)
        markup.add(types.KeyboardButton("Отмена"))  # Add a "Cancel" button
        msg = bot.send_message(message.chat.id, 'Выберите позицию из меню для удаления:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_selected_item_for_deletion)
    else:
        get_access(message)

def process_selected_item_for_deletion(message):
    selected_item = message.text
    if selected_item == "Отмена":
        markup = types.ReplyKeyboardRemove()  # Remove the custom keyboard
        bot.send_message(message.chat.id, 'Удаление отменено.', reply_markup=markup)
    elif selected_item in menu_items:
        global selected_item_id
        selected_item_id = menu_items[selected_item]  # Store the selected item's ID

        # Create buttons for choosing the step
        confirmation_buttons = [types.KeyboardButton("Да"), types.KeyboardButton("Нет")]
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(*confirmation_buttons)

        msg = bot.send_message(message.chat.id, 'Вы действительно хотите удалить эту позицию из меню?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_confirm_deletion)
    else:
        bot.send_message(message.chat.id, 'Выберите пожалуйста позицию из меню.')

def process_confirm_deletion(message):
    if message.text.lower() == 'да':
        try:
            conn = sqlite3.connect('mysite/cafe.db')
            cur = conn.cursor()
            cur.execute("DELETE FROM items WHERE id = ?", (selected_item_id,))
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, 'Товар успешно удален.')
        except Exception as e:
            bot.send_message(message.chat.id, 'Произошла ошибка при удалении товара. Пожалуйста, попробуйте позже.')
    elif message.text.lower() == 'нет':
        bot.send_message(message.chat.id, 'Товар не будет удален.')
    else:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите "Да" или "Нет".')
        bot.register_next_step_handler(msg, process_confirm_deletion)


@bot.message_handler(commands=["todaystatistics"])
def todaystatistics(message):
    if is_user_authorized(message.from_user.id):
        conn = sqlite3.connect('mysite/cafe.db')
        cur = conn.cursor()
        cur.execute("SELECT id, sum FROM orders WHERE created BETWEEN ? AND ?", (_get_now_datetime().date(), _get_now_datetime().replace(minute=59, hour=23, second=59)))
        result = cur.fetchall()
        today_sum = sum([t[1] for t in result])
        ids = [t[0] for t in result]
        max_id = max(ids, default=0)
        min_id = min(ids, default=0)
        cur.execute("""
            SELECT item, amount
            FROM items_orders
            JOIN items ON items.id = items_orders.item_id
            WHERE items_orders.order_id between ? AND ?
        """, (min_id, max_id))
        statistics = cur.fetchall()
        today_list = [i[0] + ' – ' + str(i[1]) for i in statistics]
        today_list = '\n'.join(today_list)
        conn.close()
        bot.send_message(message.chat.id, f'Сегодняшняя выручка: {today_sum}.\nКоличество заказов: {len(result)}.\n\nКупили:\n{today_list}')
    else:
        get_access(message)


@bot.message_handler(commands=["monthstatistics"])
def monthstatistics(message):
    if is_user_authorized(message.from_user.id):
        conn = sqlite3.connect('mysite/cafe.db')
        cur = conn.cursor()

        # Calculate the start and end dates of the current month
        today = _get_now_datetime()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = today.replace(day=1, month=today.month+1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(seconds=1)

        # Fetch orders within the current month
        cur.execute("SELECT id, sum FROM orders WHERE created BETWEEN ? AND ?", (start_of_month, end_of_month))
        result = cur.fetchall()
        month_sum = sum([t[1] for t in result])

        ids = [t[0] for t in result]
        max_id = max(ids, default=0)
        min_id = min(ids, default=0)

        # Fetch items ordered within the current month
        cur.execute("""
             SELECT item, amount
             FROM items_orders
             JOIN items ON items.id = items_orders.item_id
             WHERE items_orders.order_id between ? AND ?
        """, (min_id, max_id))

        statistics = cur.fetchall()
        month_list = [i[0] + ' – ' + str(i[1]) for i in statistics]
        month_list = '\n'.join(month_list)

        conn.close()
        bot.send_message(message.chat.id, f'Статистика за текущий месяц: \nВыручка: {month_sum}. \nКоличество заказов: {len(result)}. \n\nКупили:\n{month_list}')
    else:
        get_access(message)


# Define a dictionary to store start and end dates for each user
date_selection = {}

translations = {
    'day': 'день',
    'month': 'месяц',
    'year': 'год',
}

@bot.message_handler(commands=['periodstatistics'])
def periodstatistics_start(message):
    if is_user_authorized(message.from_user.id):
        user_id = message.chat.id
        date_selection[user_id] = {}  # Create a dictionary for this user if not exists

        # Create a calendar for the start date selection
        calendar_start, step_start = DetailedTelegramCalendar(locale='ru').build()
        bot.send_message(user_id, f"Выберите начальную дату периода ({LSTEP[step_start]}):", reply_markup=calendar_start)

        # Set the step to indicate that we are selecting the start date
        date_selection[user_id]['step'] = 'start'
    else:
        get_access(message)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    user_id = c.message.chat.id
    result, key, step = DetailedTelegramCalendar(locale='ru').process(c.data)

    if not result and key:
        bot.edit_message_text(f"Выберите {translations[LSTEP[step]]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        # Check which step (start or end) we are in
        current_step = date_selection.get(user_id, {}).get('step', None)

        if current_step == 'start':
            date_selection[user_id]['start_date'] = result

            # Create a calendar for the end date selection
            calendar_end, step_end = DetailedTelegramCalendar(locale='ru').build()
            bot.send_message(user_id, f"Выберите конечную дату периода ({LSTEP[step_end]}):", reply_markup=calendar_end)

            # Set the step to indicate that we are selecting the end date
            date_selection[user_id]['step'] = 'end'
        elif current_step == 'end':
            date_selection[user_id]['end_date'] = result

            # Now you have both start and end dates in date_selection[user_id]
            start_date = date_selection[user_id]['start_date']
            end_date = date_selection[user_id]['end_date']

            # Perform your statistics calculation here using start_date and end_date
            # For example, fetch orders within the specified date range
            conn = sqlite3.connect('mysite/cafe.db')
            cur = conn.cursor()
            cur.execute("SELECT id, sum FROM orders WHERE created BETWEEN ? AND ?", (start_date, end_date))
            result = cur.fetchall()
            month_sum = sum([t[1] for t in result])

            ids = [t[0] for t in result]
            max_id = max(ids, default=0)
            min_id = min(ids, default=0)

            # Fetch items ordered within the specified date range
            cur.execute("""
                SELECT item, amount
                FROM items_orders
                JOIN items ON items.id = items_orders.item_id
                WHERE items_orders.order_id BETWEEN ? AND ?
            """, (min_id, max_id))

            statistics = cur.fetchall()
            month_list = [i[0] + ' – ' + str(i[1]) for i in statistics]
            month_list = '\n'.join(month_list)

            conn.close()

            # Send the statistics as a message
            bot.send_message(user_id, f'Статистика за период с {start_date.strftime("%d-%m-%Y")} по {end_date.strftime("%d-%m-%Y")}: \nВыручка: {month_sum}. \nКоличество заказов: {len(result)}. \n\nКупили:\n{month_list}')

            # Optionally, clear the date selection data for this user
            date_selection.pop(user_id, None)



def _get_now_formatted():
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")

def _get_now_datetime():
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
