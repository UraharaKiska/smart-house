import asyncio
import sys
import aiohttp
sys.path.append('/home/gregorok/mikrohui/server/services')
from config import API_TOKEN_BOT
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import aioschedule
import requests
from graphik import Graphic
from models import Dht22
from pydantic import ValidationError
import json
import dateutil.parser
from matplotlib import pyplot as plt
from connect_database import *


URL = "http://127.0.0.1:8000/api/v1/dht22/{}"
URL_LOGIN = "http://127.0.0.1:8000/auth/token/login/"
URL_LOGOUT = "http://127.0.0.1:8000/auth/token/logout/"
URL_AUTH = "http://127.0.0.1:8000/api/v1/auth/users/"
URL_ADD_TO_GROUP = "http://127.0.0.1:8000/api/v1/groups/adduser/"
URL_GROUP = "http://127.0.0.1:8000/api/v1/groups/"

API_TOKEN = API_TOKEN_BOT

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


allowed_command = ["/start", "/help", "/sign_up","/login", "/logout",
                   "/statistic_temperature", "/statistic_humidity", "/current_th"]
command_for_get_graphic = ["/for_hour", "/for_day", "/for_week"]
manager_allowed_command = ["/add_to_group", "add_group"]


class ClientStatesGroup(StatesGroup):
    get_dtth22_data = State() 
    username = State()
    email = State()
    password = State() 
    
class LoginStates(StatesGroup):
    username = State()
    password = State()

class UserGroupState(StatesGroup):
    username = State()
    group = State()


HELP_COMMAND = """
<b>/help</b> - <em></em>
<b>/sign_up</b> - create account <em></em>
<b>/login</b> - login <em></em>
<b>/logout</b> - logout <em></em>
<b>/current_th</b> - get current temperature and humidity <em></em>
<b>/statistic_temperature</b> - get temperature graphic <em></em> 
<b>/statistic_humidity</b> - get humidity graphic<em></em>

"""

kb_help = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_get_data = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_get_data.add(KeyboardButton('/current_th'))
kb_get_data.add(KeyboardButton('/statistic_temperature'))
kb_get_data.add(KeyboardButton('/statistic_humidity'))

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_start.add(KeyboardButton('/sign_up'))
kb_start.add(KeyboardButton('/login'))
kb_start.add(KeyboardButton('/logout'))


kb_get = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_get.add(KeyboardButton('/for_hour'))
kb_get.add(KeyboardButton('/for_day'))
kb_get.add(KeyboardButton('/for_week'))


async def get_data_graphic(column_name, message, state):
    url = ""
    data = await state.get_data()
    title = data['title']
    ylabel = "°C" if title == "temperature" else "%"
    if message.text == "/for_hour":
        url = URL.format("hour")
        plot = Graphic(date_format="%H:%M", title=title, ylabel=ylabel, xlabel="date" )
    if message.text == "/for_day":
        url = URL.format("day")
        plot = Graphic(date_format="%H:%m")
    if message.text == "/for_week":
        url = URL.format("week")
        plot = Graphic(date_format="%Y-%m-%d")
    engine = database_connect()
    cursor = engine.cursor()
    cursor.execute(f"SELECT api_token from telegram_users WHERE user_id = {message.from_user.id} ")
    data = cursor.fetchall()
    response = requests.get(url, headers={'Authorization': f'Token {data[0][0]}'})
    if response.status_code == 200:
        text = json.loads(response.text, object_hook=DecodeDateTime)
        x = [round(float(i[column_name]), 1) for i in text]
        y = [i['date_create'] for i in text]
        plot.plot_graph(x, y)
        name = message.from_user.id
        plot.save_png(f"data/{name}.png")
        photo = open(f'data/{name}.png', 'rb')
        plt.close()
        return response.status_code, photo
    else:
        return response.status_code, response.text


@dp.message_handler(lambda message: message.get_command() not in allowed_command)
async def answer_unknown_command(message: types.Message):
    await message.answer(f"Not available this command: {message.text}\nSend /help for see allowed commands")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    hello = "Hi, Pidor"
    engine = database_connect()
    cursor = engine.cursor()
    cursor.execute(f"INSERT INTO telegram_users (user_id, username) values ({message.from_user.id}, '{message.from_user.username}')")
    engine.commit()
    cursor.close()
    engine.close()
    await message.answer(text=hello, reply_markup=kb_start)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    await message.answer(text=HELP_COMMAND, parse_mode='HTML')


@dp.message_handler(commands=['sign_up'])
async def sign_up(message: types.Message) -> None:
    await message.answer(text="Enter the username")
    await ClientStatesGroup.username.set()


@dp.message_handler(commands=['logout'])
async def logout(message: types.Message) -> None:
    conn = database_connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT api_token, is_active FROM telegram_users WHERE user_id = {message.from_user.id}")
    token = cursor.fetchall()
    if token[0][1] == False:
            await message.answer(text="You are already logout")
    else:
        # print(token[0][0])
        async with aiohttp.ClientSession() as session:
            async with session.post(URL_LOGOUT, headers={'Authorization': f'Token {token[0][0]}'}) as resp:
                if resp.status == 204:
                    cursor.execute(f"UPDATE telegram_users SET api_token = '', is_active = False WHERE user_id = {message.from_user.id}")
                    conn.commit()
                    await message.answer(text="You are logout", reply_markup=kb_start)
                else:
                    await message.answer(text="Server error")          
    conn.close()




@dp.message_handler(commands=['login'])
async def login(message: types.Message) -> None:
    engine = database_connect()
    cursor = engine.cursor()
    cursor.execute(f"SELECT is_active from telegram_users WHERE user_id = {message.from_user.id} ")
    data = cursor.fetchall()
    cursor.close()
    engine.close()
    if data[0][0] == True:
        await message.answer(text="You are already logged in!", reply_markup=kb_start)
    else:
        await message.answer(text="Enter the username")
        await LoginStates.username.set()
    
@dp.message_handler(state=LoginStates.username)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Enter the password")
    await LoginStates.next() # либо же UserState.address.set()

 
@dp.message_handler(state=LoginStates.password)
async def login_user(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await message.answer(f"username: {data['username']}\n"
                        f"password: {data['password']}\n")
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_LOGIN, json=data) as resp:
            get = await resp.json()
            if resp.status == 200:
                engine = database_connect()
                cursor = engine.cursor()
                cursor.execute(f"UPDATE telegram_users SET api_token = '{get['auth_token']}', is_active = True WHERE user_id = {message.from_user.id}")
                engine.commit()
                engine.close()
                await message.answer(text = "SUCCESS")  
            elif resp.status == 401:
                await message.answer(text = "Wrong login or password")      
            else:
                error = await resp.json()
                text = ""
                for k, e in error.items() :
                    text += f"{k}: {e}\n"
                await message.answer(text = text)
    await state.finish()
    
    

@dp.message_handler(state=ClientStatesGroup.username)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Enter the email")
    await ClientStatesGroup.next() # либо же UserState.address.set()


@dp.message_handler(state=ClientStatesGroup.email)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Enter the password")
    await ClientStatesGroup.next() # либо же UserState.address.set()
    
        
@dp.message_handler(state=ClientStatesGroup.password)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await message.answer(f"username: {data['username']}\n"
                        f"email: {data['email']}\n"
                        f"password: {data['password']}\n")
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_AUTH, json=data) as resp:
            if resp.status == 201:
                await message.answer(text="Success, now you should login", reply_markup=kb_start)
            else:
                error = await resp.json()
                text = ""
                for k, e in error.items() :
                    text += f"{k}: {e}\n"
                await message.answer(text = text)
    await state.finish()
    
    

def DecodeDateTime(empDict):
    if 'date_create' in empDict:
        empDict["date_create"] = dateutil.parser.parse(empDict["date_create"])
        return empDict



async def current_th_former(response, user_id, data):
    text = f"Temperature: {data['temperature']} °C\nHumidity: {data['humidity']} %"
    await bot.send_message(user_id, text=text, parse_mode='HTML')


@dp.message_handler(commands=['current_th'])
async def send_current_data(message: types.Message) -> None:
    url = URL.format("current")
    engine = database_connect()
    cursor = engine.cursor()
    cursor.execute(f"SELECT is_active, api_token FROM telegram_users WHERE user_id = {message.from_user.id}")
    user = cursor.fetchall()
    if user[0][0] == False:
        await message.answer(text="You should login", reply_markup=kb_start)
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'Authorization': f'Token {user[0][1]})'}) as resp:            
                if resp.status == 200:
                    data = await resp.json()
                    await current_th_former(resp, message.from_user.id, data)
                else:
                    await message.answer(text="No information")
                    

    

async def current_data():
    url = URL.format("current")
    engine = database_connect()
    cursor = engine.cursor()
    cursor.execute(f"SELECT user_id, api_token FROM telegram_users WHERE is_active = True")
    users = cursor.fetchall()
    for user in users:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'Authorization': f'Token {user[1]})'}) as resp:            
                if resp.status == 200:
                    data = await resp.json()
                    await current_th_former(resp, user[0], data)
                else:
                    await bot.send_message(user[0], text=text, parse_mode='HTML')
                    




@dp.message_handler(commands=['statistic_temperature', 'statistic_humidity'])
async def activate_stat(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await ClientStatesGroup.get_dtth22_data.set()
    title = "temperature" if message.text == "/statistic_temperature" else "humidity"
    await state.update_data(title=title)
    
    await message.answer(
        text="Choose interval to view graphic", reply_markup=kb_get)


@dp.message_handler(state=ClientStatesGroup.get_dtth22_data)
async def send_data_graphic(message: types.Message, state: FSMContext):
    if (message.text in command_for_get_graphic):
        data = await state.get_data()
        column_name = data['title']
        status, data = await get_data_graphic(column_name, message, state)
        if status == 200:
            await message.answer_photo(data, reply_markup=kb_get_data)
        else:
            await message.answer(data)   
    else:
        await answer_unknown_command(message)
    await state.finish()
    


@dp.message_handler(commands=['add_to_group'])
async def check_permission(message: types.Message, state: FSMContext):
    conn = database_connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT is_admin FROM telegram_users WHERE user_id = {message.from_user.id}")
    data = cursor.fetchall()
    if data[0][0] == True:
        await UserGroupState.username.set()
        await message.answer(text="Enter the username")
    else:
        await answer_unknown_command(message)
        
    
@dp.message_handler(state=UserGroupState.username)
async def get_username_for_group(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await UserGroupState.next()
    await message.answer(text="Enter the group")


@dp.message_handler(state=UserGroupState.group)
async def get_group_for_user(message: types.Message, state: FSMContext):
    group = message.text
    await state.update_data(group=group)
    data = await state.get_data()
    await message.answer(text=f"{data['username']}\n{data['group']}")
    conn = database_connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT api_token FROM telegram_users WHERE user_id = {message.from_user.id}")
    token = cursor.fetchall()
    print(token[0][0])
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_ADD_TO_GROUP, json=data, headers={'Authorization': f'Token {token[0][0]}'}) as resp:
            await message.answer(text=await resp.json())
    await state.finish()
    



async def scheduler():
    aioschedule.every().day.at("6:22").do(current_data)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(5)


async def on_startup(_):
    asyncio.create_task(scheduler())



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
