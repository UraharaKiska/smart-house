import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
from connect_database import *
import pytz

class Graphic():
    title: str = "x"
    ylabel: str = "y"
    xlabel: str 
    date_format :str

    def __init__(self, title="", ylabel="", xlabel="", date_format="%H:%M:%S"):
        self.title = title
        self.ylabel = ylabel
        self.xlabel = xlabel
        self.date_format = date_format

    # @staticmethod
    # def get_query(data, x_column, y_column):
    #     x = [round(float(i[x_column]), 1) for i in data]
    #     y = [i[y_column] for i in data]
    #     return x, y
        
    def plot_graph(self, x, y):   
        plt.plot_date(y, x, 'r')
        plt.gcf().autofmt_xdate()
        date_format = mpl_dates.DateFormatter(self.date_format, tz='Europe/Moscow')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.grid()
        plt.title(self.title)
        plt.ylabel(self.ylabel)
        plt.xlabel(self.xlabel)
    
    
    def save_png(self, name):
        plt.savefig(name)




# conn = database_connect()  
# query = f"SELECT *, date_create FROM dht22 where date(date_create) = date(now()) ORDER BY date_create  "
# cursor = conn.cursor()
# cursor.execute(query)
# data = cursor.fetchall()

# plot = Graphic(title="Temperature")
# x, y = Graphic.get_query(data, 1, 4)  
# plot.plot_graph(x, y)

# plot = Graphic(title="Humiidity")
# x, y = Graphic.get_query(data, 2, 4)  
# plot.plot_graph(x, y)

# plot = Graphic(title="Heatindex")
# x, y = Graphic.get_query(data, 3, 5)  
# plot.plot_graph(x, y)
# plot = Graphic(title="humidity", ylabel="%", xlabel="date", date_format="%H:%M")  
# # data = plot.get_query("humidity", "where date(date_create) = date(now())")
# plot.plot_graph(x, y)

# plot = Graphic(title="heatindex", ylabel="°C", xlabel="date")  
# # data = plot.get_query("heatindex", "where date(date_create) = date(now())")
# plot.plot_graph(x, y)
    
    
    
# conn = database_connect()
# cursor = conn.cursor()
# query = "select temperature, humidity, date_create from dht22 where date(date_create) = date(now()) order by date_create"
# cursor.execute("""select temperature as t, humidity as h, date_create as d from dht22 where date(date_create) = date(now()) order by date_create """)
# info = cursor.fetchall()
# x = [round(float(i[0]), 1) for i in info]
# y = [i[2] for i in info]
# x1 = [round(float(i[1]), 1) for i in info]
# y1 = [i[2] for i in info]
# lines = plt.plot_date(y, x, 'r')

# # df = pd.read_sql(query, conn)
# # print(df.to_dict("df"))

# plt.gcf().autofmt_xdate()

# date_format = mpl_dates.DateFormatter('%H:%M:%S')
# plt.grid()
# plt.title('Temperature')
# plt.ylabel('°C')
# plt.gca().xaxis.set_major_formatter(date_format)
# # plt.gca().xaxis.set_major_formatter(date_format)

# # fig, ax = plt.subplots()
# plt.show()
