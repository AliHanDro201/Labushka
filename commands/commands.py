"""
These commands are functions that ChatGPT will use 
if the user requests it. 

So far the user can ask ChatGPT to:
- Open or close an application
- Interact with their spotify by:
    - Playing an album, playlist, or song.
"""

# ************************************************
# * Utilities
import AppOpener
from dotenv import load_dotenv
import psutil
import webbrowser
import traceback
import requests
import os
import re
import time
from spotify_player import Spotify_Player
import pyautogui
from helium import *
import pywinctl as gw
import pytesseract
import cv2
import numpy as np
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import keyboard
from utils.tts import stop_audio
load_dotenv( dotenv_path='.evn')

NEWS_API_KEY = os.getenv("NEWS_API_KEY") 
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_news() -> str:
    """
    Получает последние новости.

    Returns:
    - str: Топ-3 новости.
    """
    if not NEWS_API_KEY:
        return "API ключ для новостей не найден."
    
    url = f"https://newsapi.org/v2/top-headlines?country=ru&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    
    if "articles" not in response:
        return "Ошибка при получении новостей."
    
    news_list = [f"{idx+1}. {article['title']}" for idx, article in enumerate(response["articles"][:3])]
    return "\n".join(news_list)



def get_weather(city: str) -> str:
    """
    Получает текущую погоду из WeatherAPI.

    Parameters:
    - city : str
        - Название города.

    Returns:
    - str: Погода.
    """
    if not WEATHER_API_KEY:
        return "API ключ для погоды не найден."

    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru"
    
    try:
        response = requests.get(url).json()
        
        if "error" in response:
            return "Ошибка: " + response["error"]["message"]

        location = response["location"]["name"]
        country = response["location"]["country"]
        condition = response["current"]["condition"]["text"]
        temp_c = response["current"]["temp_c"]
        feels_like = response["current"]["feelslike_c"]
        wind_kph = response["current"]["wind_kph"]
        humidity = response["current"]["humidity"]

        return (f"Погода в {location}, {country}: {condition}, {temp_c}°по цельсю.\n"
                f"Ощущается как {feels_like}°по цельсю. Ветер {wind_kph} километров в час, влажность {humidity}%.")
    
    except Exception as e:
        return f"Ошибка при получении погоды: {str(e)}"

# ************************************************


# * Utility functions
def is_open(app_name: str, include_exe: bool = False) -> bool:
    """
    Confirms if an application is open or not.
    
    Parameters:
    - include_exe : bool (optional)
        - Determines if .exe should be included in the application 
          name to search for.
    Returns:

    """

    if include_exe:
        app_name = str.strip(app_name) + ".exe"


    opened = False
    for i in psutil.process_iter():
        if str.lower(app_name) in str.lower(i.name()):
            opened = True
            break
    
    return opened

# *********************************
# * Commands

# * Open an app
def open_app(name: str) -> str:
    """
    Uses the AppOpener python package to open an application

    Parameters:
    - name : str
        - The name of the application
    """


    # * First check if the app is already opened
    # for i in psutil.process_iter():
    #     if str.lower(name) in str.lower(i.name()):
    #         print(i.name())
    #         not_opened = False
            
    # opened = is_open(name)

    # if not opened:
    try:
        print("Attempting to open app")
        AppOpener.open(name, match_closest=True, throw_error=True, output=False)
    except:
        error = traceback.format_exc
        traceback.print_exc()
        return error
    else:
        output = format("{name} was successfully opened")
        return output

# * Close an app
def close_app(name: str) -> str:
    """
    Uses the AppOpener python package to close an application

    Parameters:
    - name : str
        - The name of the application
    """

    try:
        AppOpener.close(name, match_closest=True, throw_error=True, output=False)
    except:
        traceback.print_exc()
    else:
        output = format("{name} was successfully closed".format(name=name))
        return output


# * Commands that will use the Spotify_Player class

def search_web(query: str) -> str:
    """
    Открывает браузер и выполняет поиск информации в Google.

    Parameters:
    - query : str
        - Запрос для поиска.

    Returns:
    - str: Сообщение о выполнении поиска.
    """
    """
    Если запрос совпадает с известным сайтом — открывает его напрямую.
    """
    websites = {
        "YouTube": "https://www.youtube.com",
        "Википедия": "https://ru.wikipedia.org",
        "Google": "https://www.google.com",
        "Новости": "https://news.google.com",
        "е-кызмет":"https://eqyzmet.gov.kz/#/main/start"
    }

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Ищу информацию по запросу: {query}"




def sleep() -> None:
    """
    This function will be passed to ChatGPT. This function will help
    determine if user input should continue to be processed or not.
    """
    return ""




    
def open_ekyzmet():
    """
    Открывает сайт e-Кызмет и автоматически нажимает кнопку 'Вход/Регистрация' с помощью Helium.
    """
    try:
        # Открываем браузер
        browser = start_chrome("https://eqyzmet.gov.kz/#/main/start", headless=False)
        
        # Ожидаем загрузки страницы
        time.sleep(5)
        
        # Находим и нажимаем кнопку 'Вход/Регистрация'
        click("Вход/Регистрация")
        time.sleep(2)
        
        print("Кнопка 'Вход/Регистрация' успешно нажата.")
        return "Сайт e-Кызмет открыт, вход выполнен."

    except Exception as e:
        return f"Ошибка при открытии e-Кызмет: {str(e)}"


def go_back():
    """Возвращает пользователя на предыдущую страницу в браузере."""
    pyautogui.hotkey("alt", "left")  # Работает в любом браузере
    return "Перехожу назад."

def go_forward():
    """Перемещает пользователя вперёд в истории браузера."""
    pyautogui.hotkey("alt", "right")
    return "Перехожу вперёд."

def scroll_up():
    """Прокручивает страницу вверх на 1 экран."""
    pyautogui.press("pageup")
    return "Прокручиваю вверх."

def scroll_down():
    """Прокручивает страницу вниз на 1 экран."""
    pyautogui.press("pagedown")
    return "Прокручиваю вниз."



from .window_manager import click_button
#def click_button(button_text: str):
#    """Нажимает кнопку с указанным текстом в браузере."""
#    pyautogui.press("tab")  # Переключение между элементами
#    pyautogui.press("enter")  # Подтверждение
#    return f"Нажимаю кнопку: {button_text}"



def open_website(url: str):
    """Открывает указанный сайт в браузере."""
    webbrowser.open(url)
    return f"Открываю сайт: {url}"

# Глобальные команды
keyboard.add_hotkey("caps lock", stop_audio)  # Останавливает озвучку даже в свернутом режиме



































def get_active_tab_index() -> int:
    """
    Определяет текущую активную вкладку по ее позиции.
    Работает с Chrome, Edge и Firefox.
    """
    for i in range(1, 10):  # Проверяем вкладки 1-9
        pyautogui.hotkey('ctrl', str(i))
        time.sleep(0.1)  # Даем браузеру время переключиться
        active_window = pyautogui.getActiveWindowTitle()  # Получаем заголовок активного окна
        if active_window:
            return i
    return 1  # Если не удалось определить, считаем, что активна 1-я вкладка


def switch_tab_by_number(tab_number: int):
    """
    Переключается на вкладку по её номеру (в том числе если вкладок больше 9).
    """
    if tab_number < 1:
        return "❌ Введите корректный номер вкладки (1 или выше)."

    current_tab = get_active_tab_index()  # Определяем текущую вкладку

    if tab_number == current_tab:
        return f"✅ Уже на вкладке №{tab_number}."

    if tab_number <= 9:
        # Если вкладка в пределах 1-9, переключаемся напрямую
        pyautogui.hotkey('ctrl', str(tab_number))
    elif tab_number > current_tab:
        # Если вкладка справа, переключаемся вперёд
        steps = tab_number - current_tab
        for _ in range(steps):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.2)
    else:
        # Если вкладка слева, переключаемся назад
        steps = current_tab - tab_number
        for _ in range(steps):
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            time.sleep(0.2)

    return f"🔀 Переключаюсь на вкладку №{tab_number}."




def refresh_page():
    """Обновляет текущую страницу в браузере."""
    
    pyautogui.hotkey("ctrl", "r")  # ✅ Горячая клавиша для обновления страницы
    time.sleep(0.5)  # ⏳ Небольшая задержка, чтобы обновление произошло
    return "🔄 Страница обновлена."

def clear_cache():
    """Очищает кэш данной страницы и обновляет её."""
    
    pyautogui.hotkey("ctrl", "shift", "r")  # ✅ Горячая клавиша для обновления с очисткой кэша
    time.sleep(0.5)  # ⏳ Небольшая задержка для выполнения команды
    return "🧹 Кэш страницы очищен и обновлён."

def clear_cache_and_cookies():
    """Очищает cookies, local storage и кэш, затем обновляет страницу."""
    
    # ✅ Открываем DevTools
    pyautogui.hotkey("ctrl", "shift", "i")
    time.sleep(1)

    # ✅ Открываем панель "Приложение"
    pyautogui.hotkey("ctrl", "shift", "p")
    time.sleep(0.5)
    pyautogui.write("Clear site data")  # ✅ Вводим команду очистки
    time.sleep(0.5)
    pyautogui.press("enter")  # ✅ Подтверждаем очистку

    time.sleep(1)  # ⏳ Ожидание завершения очистки

    # ✅ Закрываем DevTools
    pyautogui.hotkey("ctrl", "shift", "i")

    return "🧹 Кэш, cookies и local storage очищены, страница обновлена!"





def play_pause_media():
    """Ставит на паузу любое воспроизведение медиа в системе."""
    pyautogui.press("playpause")  # Работает с YouTube, Spotify, VLC
    return "Понял!"










