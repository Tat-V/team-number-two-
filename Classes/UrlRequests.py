import Shushushu as sh
import requests
import random


class UrlRequests:

    # @staticmethod
    def get_film(self, update):
        text = open(sh.files.FilmFile, 'r')
        film_list = text.read().split()
        film_name = film_list[random.randint(0, len(film_list) - 1)]
        url = f"https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/{film_name}"
        headers = {
            'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
            'x-rapidapi-key': "99bdeb0c42mshab03bca44e75a6fp188e06jsn6d8755719252"
        }
        r = requests.request("GET", url, headers=headers)
        r = dict(r.json())
        title = r['title']
        rating = r['rating']
        length = r['length']
        main_role = r['cast'][0]['actor']
        return [title,rating,length,main_role]

    def get_weather(TOKEN, CITY):
        url = f'http://api.weatherstack.com/current?access_key={TOKEN}&query={CITY}'

        r = requests.get(url)
        if r.status_code == 200:
            r = r.json()
            city = r.get('request')['query']
            time = r.get('current')['observation_time']
            temperature = r.get('current')['temperature']
            weather_descriptions = r.get('current')['weather_descriptions'][0]
            wind_speed = r.get('current')['wind_speed']
            wind_speed = round(wind_speed * 1000.0 / 3600.0)
            weather_now = 'Город: ' + city + '\n' + 'Время снятия данных: ' + str(time) + '\n' + 'Температура: ' + \
                          str(temperature) + '℃' + '\n' + 'Скорость ветра: ' + str(wind_speed) + ' м/c' + '\n' \
                          + weather_descriptions
        else:
            weather_now = 'Функция в данный момент недоступна'
        return weather_now
