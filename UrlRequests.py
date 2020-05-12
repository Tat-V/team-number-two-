import Shushushu as sh
import requests
import random


class UrlRequests:
    TOKEN = ''  # insert your token weather here
    CITY = 'Nizhny Novgorod'
    request_url_weather = f'http://api.weatherstack.com/current?access_key={TOKEN}&query={CITY}'

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

    @staticmethod
    def get_weather():
        r = requests.get(UrlRequests.request_url_weather)
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

    @staticmethod
    def get_cat_fact():
        r = requests.get('https://cat-fact.herokuapp.com/facts')
        cat_fact = ''
        if r.status_code == 200:
            cats_dict = dict(r.json())
            cats_dict = cats_dict.get('all')
            kol_fact = len(cats_dict)
            fact_upvotes = cats_dict[0]['upvotes']
            cat_fact = cats_dict[0]['text']
            for i in range(1, kol_fact):
                if cats_dict[i]['upvotes'] > fact_upvotes:
                    fact_upvotes = cats_dict[i]['upvotes']
                    cat_fact = cats_dict[i]['text']
        return cat_fact
