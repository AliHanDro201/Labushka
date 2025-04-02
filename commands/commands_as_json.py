"""
In order for ChatGPT to use our functions, they need 
they need to be described in a the format Dict[str, str]. If you have 
a custom function, write the details of your function in 
a new dictionary object in the commands array.

For more details, you can read the ChatGPT official documentation here:
https://platform.openai.com/docs/guides/gpt/function-calling
"""

commands = [
    {
        "name": "open_app",
        "description": "Start an application on the user's computer if asked to, \
                        If the application is already opened, inform the user of that.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the application"
                },
            },
            "required": ["name"]
        }
    },
    {
        "name": "close_app",
        "description": "Close an application on the user's computer if asked to. \
                        If the application is already closed, inform the user of that",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the application"
                },
            },
            "required": ["name"]
        }
    },
    
    {
        "name": "sleep",
        "description": "If the user doesn't need any more assistance at the moment,\
                        or if you presume they are finished speaking to you for now, \
                        then this function should be called. You will take no more input until the user \
                        says the wake command 'hey stella' and requests more assistance.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
    "name": "search_web",
    "description": "Открывает браузер и выполняет поиск информации в Google.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Поисковый запрос"
            }
        },
        "required": ["query"]
    }
    },
    {
    "name": "get_news",
    "description": "Получает последние новости.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
    },
    {
    "name": "get_weather",
    "description": "Получает текущий прогноз погоды через WeatherAPI. WEATHER_API_KEY = os.getenv(6f8ea0a7ef574115a6b40611251002)",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Название города"
            }
        },
        "required": ["city"]
    }
    },

    {
    "name": "search_web",
    "description": "Открывает браузер и выполняет поиск информации в Google или открывает сайт напрямую.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Поисковый запрос или название сайта (например, YouTube, Википедия)."
            }
        },
        "required": ["query"]
    }
    },
    {
    "name": "open_ekyzmet",
    "description": "Открывает сайт e-Кызмет и нажимает на кнопку 'Вход/Регистрация'.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
    },
    {
    "name": "go_back",
    "description": "Возвращается на предыдущую страницу в браузере.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
    },
    {
        "name": "go_forward",
        "description": "Переходит на следующую страницу в браузере.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "scroll_up",
        "description": "Прокручивает страницу вверх.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "scroll_down",
        "description": "Прокручивает страницу вниз.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "open_website",
        "description": "Открывает указанный сайт в браузере.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL сайта, который нужно открыть"
                }
            },
            "required": ["url"]
        }
    },







    
    {
    "name": "click_button",
    "description": "Нажимает указанную кнопку в активном окне.",
    "parameters": {
        "type": "object",
        "properties": {
            "button_text": {
                "type": "string",
                "description": "Текст кнопки, которую нужно нажать"
            }
        },
        "required": ["button_text"]
    }
    },





    
    {
        "name": "switch_tab_by_number",
        "description": "Переключается на вкладку по её номеру (абсолютная нумерация во всём браузере).",
        "parameters": {
            "type": "object",
            "properties": {
                "tab_number": {
                    "type": "integer",
                    "description": "Номер вкладки (начиная с 1)."
                }
            },
            "required": ["tab_number"]
        }
    },   
    {
    "name": "refresh_page",
    "description": "Обновляет текущую страницу в браузере.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
    },
    {
        "name": "clear_cache",
        "description": "Очищает кэш данной страницы и обновляет её.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "clear_cache_and_cookies",
        "description": "Очищает cookies, local storage и кэш, затем обновляет страницу.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },



    {
    "name": "play_pause_media",
    "description": "Ставит на паузу (или воспроизводит) любое воспроизведение медиа в системе (YouTube, Spotify, VLC и другие).",
    "parameters": {
        "type": "object",
        "properties": {}
    }
    },

    




    






]
