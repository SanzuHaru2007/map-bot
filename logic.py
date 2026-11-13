import requests
import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_grapf(self, path, cities):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.stock_img()
        for city_name in cities:
            coords = self.get_coordinates(city_name)
            if coords:
                lat, lng = coords
                ax.plot(lng, lat, marker='o', color='red', markersize=6, transform=ccrs.Geodetic())
                ax.text(lng + 1, lat + 1, city_name, transform=ccrs.Geodetic(), fontsize=9, color='blue')

        plt.savefig(path)
        plt.close()
        
    def get_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT city FROM cities WHERE country = ?", (country,))
            return [row[0] for row in cur.fetchall()]

    def get_cities_by_population(self, min_pop, max_pop):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT city FROM cities WHERE population BETWEEN ? AND ?", (min_pop, max_pop))
            return [row[0] for row in cur.fetchall()]

    def get_cities_by_country_and_pop(self, country, min_pop, max_pop):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT city FROM cities WHERE country = ? AND population BETWEEN ? AND ?",
                (country, min_pop, max_pop)
            )
            return [row[0] for row in cur.fetchall()]

    def get_weather(city_name):
        url = f"https://wttr.in/{city_name}?format=j1"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                temp = current['temp_C']
                desc = current['weatherDesc'][0]['value']
                return f"Погода в {city_name}: {temp}°C, {desc}"
        except Exception:
            pass
        return "Не удалось получить данные о погоде."


    def get_local_time(lat, lng):
        url = f"https://timeapi.io/api/Time/current/coordinate?latitude={lat}&longitude={lng}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return f"Местное время: {data.get('time', 'неизвестно')} (Дата: {data.get('date', 'неизвестно')})"
        except Exception:
            pass
        return "Не удалось определить время."

if __name__=="__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
