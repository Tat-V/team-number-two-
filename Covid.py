import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import requests

import Shushushu as sh


class CovidStatistics:
    def top_five(self):
        raise RuntimeError

    def image_create(self):
        raise RuntimeError


class CovidStats(CovidStatistics):

    def upload_chosen_date(self, y, m, d):
        if len(d) == 1:
            d = '0' + d
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
              f'csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
        data = pd.read_csv(url).sort_values('Confirmed', ascending=False)
        data['Province_State'] = data['Province_State'].fillna('')
        return data

    def upload(self, y=str(date.today() - timedelta(days=1))[:4],
               m=str(date.today() - timedelta(days=1))[5:7],
               d=str(date.today() - timedelta(days=1))[8:]):

        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
              f'csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
        # data = pd.read_csv(url)
        try:
            # data = pd.read_csv(covid_collection.find()).sort_values('Confirmed', ascending=False)
            data = pd.DataFrame(sh.covid_collection_t.find()).sort_values('Confirmed', ascending=False)

        except:
            data = pd.read_csv(url).sort_values('Confirmed', ascending=False)
            with open("source_pack/Covid.csv", "wb") as file_c:
                file_c.write(requests.get(url).content)
                # data_dict = data.to_dict(orient='records')
                sh.covid_collection_t.insert_many(data.to_dict(orient='records'))
        data['Province_State'] = data['Province_State'].fillna('')
        return data

    def top_five(self, data):
        top_5 = data[['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
        text = ''
        for col in top_5:
            text += col + '\t\t'
        text += '\n\n'
        for i in top_5.values:
            for j in i:
                text += str(j) + '\t\t'
            text += '\n\n'
        return text

    def image_create(self, data):
        week_ago = date.today() - timedelta(days=7)
        y = str(week_ago)[: 4]
        m = str(week_ago)[5: 7]
        d = str(week_ago)[8:]

        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
              f'csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
        # data_ago = pd.read_csv(url)
        # data_ago = data_ago.sort_values('Confirmed', ascending=False)

        try:
            # data = pd.read_csv(covid_collection.find()).sort_values('Confirmed', ascending=False)
            data_ago = pd.DataFrame(sh.covid_collection_wa.find()).sort_values('Confirmed', ascending=False)
        except:
            data_ago = pd.read_csv(url).sort_values('Confirmed', ascending=False)
            with open("source_pack/Covid.csv", "wb") as file_c:
                file_c.write(requests.get(url).content)
                # data_dict = data.to_dict(orient='records')
                sh.covid_collection_wa.insert_many(data_ago.to_dict(orient='records'))

        all_confirmed = data['Confirmed'].sum()
        all_confirmed_ago = data_ago['Confirmed'].sum()
        all_dead = data['Deaths'].sum()
        all_dead_ago = data_ago['Deaths'].sum()
        all_recov = data['Recovered'].sum()
        all_recov_ago = data_ago['Recovered'].sum()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.bar("Confirmed til yesterday", all_confirmed, color="#FFA07A")
        ax.bar("Confirmed til week ago", all_confirmed_ago, color="#7CFC00")
        ax.bar("Dead til yesterday", all_dead, color="#FFA07A")
        ax.bar("Dead til week ago", all_dead_ago, color="#7CFC00")
        ax.bar("Recovered til yesterday", all_recov, color="#FFA07A")
        ax.bar("Recovered til week ago", all_recov_ago, color="#7CFC00")
        plt.title("Covid_statistics")
        fig.savefig("source_pack/Covid_statistics")

        fig, ax = plt.subplots(figsize=(15, 15))

        ax.bar("Confirmed", all_confirmed - all_confirmed_ago, color="#FFA07A")
        ax.bar("Dead", all_dead - all_dead_ago, color="#B0E0E6")
        ax.bar("Recovered", all_recov - all_recov_ago, color="#7CFC00")
        plt.title("Weekly changes in...")
        fig.savefig("source_pack/Covid_weekly_changes")


class CovidStatsDaily(CovidStatistics):
    @staticmethod
    def read_covid_data(date):
        y = str(date)[: 4]
        m = str(date)[5: 7]
        d = str(date)[8:]

        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
              f'csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
        return pd.read_csv(url)

    def __init__(self):
        self.today = date.today() - timedelta(days=1)  # т.к. выкладывают поздно, от-но мск времени
        self.yesterday = date.today() - timedelta(days=2)

        self.data_t = self.read_covid_data(self.today)
        self.data_y = self.read_covid_data(self.yesterday)

        self.data_t = self.data_t.sort_values('Confirmed', ascending=False)
        self.data_y = self.data_y.sort_values('Confirmed', ascending=False)

        self.confirmed_dif = self.data_t['Confirmed'].sum() - self.data_y['Confirmed'].sum()
        self.dead_dif = self.data_t['Deaths'].sum() - self.data_y['Deaths'].sum()
        self.recov_dif = self.data_t['Recovered'].sum() - self.data_y['Recovered'].sum()

    def image_create(self):
        fig, ax = plt.subplots(figsize=(15, 15))

        ax.bar("Confirmed", self.confirmed_dif, color="#FFA07A")
        ax.bar("Dead", self.dead_dif, color="#B0E0E6")
        ax.bar("Recovered", self.recov_dif, color="#7CFC00")
        # plt.text("Confirmed", all_confirmed_dif, str(all_confirmed_dif))
        plt.title(f"Daily changes in... (from {self.yesterday} to {self.today})")
        fig.savefig("source_pack/Covid_stats")

    def top_five(self):
        top_5_t = self.data_t[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
        top_5_y = self.data_y[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]

        fig = plt.figure(figsize=(15, 15))
        plt.subplot(1, 2, 1).set_title("Today")
        ax = plt.pie(top_5_t["Confirmed"], labels=top_5_t["Country_Region"], autopct='%1.1f%%')
        plt.subplot(1, 2, 2).set_title("Yesterday")
        ax = plt.pie(top_5_y["Confirmed"], labels=top_5_t["Country_Region"], autopct='%1.1f%%')
        fig.savefig("source_pack/Top_5_pie")

        fig = plt.figure(figsize=(15, 15))
        plt.subplot(2, 1, 1).set_title("Today")
        ax = plt.bar(top_5_t["Country_Region"], top_5_t["Confirmed"], color="#FF6347")
        plt.subplot(2, 1, 2).set_title("Yesterday")
        ax = plt.bar(top_5_y["Country_Region"], top_5_y["Confirmed"], color="#87CEFA")
        fig.savefig("source_pack/Top_5_bar")

        self.data_t = self.data_t.sort_values('Deaths', ascending=False)
        self.data_y = self.data_y.sort_values('Deaths', ascending=False)
        top_5_t = self.data_t[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
        top_5_y = self.data_y[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]

        fig = plt.figure(figsize=(15, 15))
        plt.subplot(2, 1, 1).set_title("Today")
        ax = plt.bar(top_5_t["Country_Region"], top_5_t["Deaths"], color="#FF6347")
        plt.subplot(2, 1, 2).set_title("Yesterday")
        ax = plt.bar(top_5_y["Country_Region"], top_5_y["Deaths"], color="#87CEFA")
        fig.savefig("source_pack/Top_5_bar_death")
