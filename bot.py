import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: </n> `/start` - начать работу с ботом и получить приветственное сообщение. </n> `/help` - получить список доступных команд. </n> `/show_city <city_name>` - отобразить указанный город на карте. </n> `/remember_city <city_name>` - сохранить город в список избранных. </n> `/show_my_cities` - показать все сохраненные города.")
    


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Укажи название города после команды")
        return
    if manager.create_map(city_name):
        with open('map.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "Не удалось найти такой город или построить для него карту. Убедись, что название написано на английском!")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Укажи название города после команды")
        return
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} сохранен!')
    else:
        bot.send_message(message.chat.id, 'У меня нет такого города. Напиши на английском')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)
    if cities:
        cities_list = "\n".join([city[0] for city in cities]) if isinstance(cities[0], tuple) else "\n".join(cities)
        bot.send_message(message.chat.id, f"Твои сохраненные города:\n{cities_list}")
    else:
        bot.send_message(message.chat.id, "Ты еще ничего не сохранил")

@bot.message_handler(commands=['country'])
def handle_country(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи страну")
        return
    
    country = parts[1]
    cities = manager.get_cities_by_country(country)
    if cities:
        manager.create_grapf('country_map.png', cities)
        with open('country_map.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "Не удалось найти города в этой стране")

@bot.message_handler(commands=['weather'])
def handle_weather(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи город")
        return
    city = parts[1]
    weather_info = get_weather(city)
    bot.send_message(message.chat.id, weather_info)

@bot.message_handler(commands=['time'])
def handle_time(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи город")
        return
    city = parts[1]
    coords = manager.get_coordinates(city)
    if coords:
        lat, lng = coords
        time_info = get_local_time(lat, lng)
        bot.send_message(message.chat.id, f"{city} — {time_info}")
    else:
        bot.send_message(message.chat.id, "Город не найден в базе.")

if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
