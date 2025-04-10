# core/agent.py
import os
import asyncio
import elevenlabs as eleven
from concurrent.futures import ThreadPoolExecutor
import openai
import json
import threading

from utils.tts import generate_audio
from core.conversation import Conversation
from core.config import prompt, GPT_MODEL, GPT_TEMPERATURE, GPT_MAX_TOKENS, OPENAI_API_KEY
from commands.commands_as_json import commands

# Устанавливаем API ключ
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# Создаем глобальный пул потоков
executor = ThreadPoolExecutor(max_workers=4)

# Блок для команд
from commands import commands as cmd_functions
from commands.commands_as_json import commands  # это список описаний команд
available_commands = {}
for command in commands:
    command_name = command["name"]
    try:
        # Получаем функцию из модуля cmd_functions по имени
        available_commands[command_name] = getattr(cmd_functions, command_name)
    except AttributeError:
        print(f"Команда {command_name} не найдена в модуле commands.")


        
# Функция для получения голосов ElevenLabs
def get_voices():
    return eleven.voices()

VOICE_ID = "XrExE9yKIg1WjnnlVkGX"

try:
    voices = get_voices()
    if voices:
        filtered = [voice for voice in voices if getattr(voice, "voice_id", "") == VOICE_ID]
        if filtered:
            main_voice = filtered[0]
        else:
            filtered = [voice for voice in voices if "matilda" in getattr(voice, "name", "").lower()]
            if filtered:
                main_voice = filtered[0]
            else:
                main_voice = None
                print("Не найден подходящий голос, используем None")
    else:
        main_voice = None
        print("Список голосов пуст.")
except Exception as e:
    main_voice = None
    print("Ошибка получения голоса:", e)

async def async_chat_completion(user_text: str) -> dict:
    # Создаем новый объект Conversation для каждого запроса с базовым prompt
    local_conversation = Conversation(prompt)
    local_conversation.add_message(role="user", content=user_text)

    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(
            executor,
            lambda: openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=local_conversation.get_messages(),
                functions=commands,
                function_call="auto",
                temperature=GPT_TEMPERATURE,
                max_tokens=GPT_MAX_TOKENS,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        )
    except Exception as e:
        print("Ошибка при вызове OpenAI:", e)
        return {"status": 500, "statusMessage": str(e)}
    
    print("Raw response from OpenAI:", response)
    try:
        message = response["choices"][0]["message"]
    except Exception as e:
        print("Ошибка при обработке ответа:", e)
        return {"status": 500, "statusMessage": "Ошибка при обработке ответа"}
    
    function_name = None  # объявляем переменную заранее
    
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        arguments = message["function_call"].get("arguments", "{}")
        print(f"GPT вызвал функцию: {function_name} с аргументами {arguments}")

        local_conversation.add_message(
            role="function",
            content=f"Вызов функции {function_name} с аргументами {arguments}",
            function_name=function_name  # передаем имя функции явно
        )

        try:
            response = await loop.run_in_executor(
                executor,
                lambda: openai.ChatCompletion.create(
                    model=GPT_MODEL,
                    messages=local_conversation.get_messages(),
                    temperature=GPT_TEMPERATURE,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            )
            message = response["choices"][0]["message"]
        except Exception as e:
            print("Ошибка при повторном вызове OpenAI:", e)
            return {"status": 500, "statusMessage": str(e)}
    local_conversation.add_message(role="assistant", content=message["content"])
    print("Ответ от GPT:", message["content"])

    if function_name in available_commands:
        func = available_commands[function_name]
        # Попробуем извлечь аргументы
        import json
        args = json.loads(arguments)
        result = func(**args)
        print("Результат выполнения функции:", result)
    else:
        print(f"Функция {function_name} не найдена в available_commands.")

    # Генерация аудио:
    if main_voice:
        try:
            # Попытка генерации аудио через ElevenLabs (используем голос "Dmitry")
            audio = eleven.generate(
                text=message["content"],
                voice="Dmitry",
                model="eleven_multilingual_v1"
            )
            eleven.save(audio, "audio/message.wav")
        except Exception as e:
            print(f"Eleven Labs error: {e}")
            print("Используем встроенный TTS с голосом Svetlana")
            threading.Thread(
                target=lambda: asyncio.run(
                    generate_audio(message["content"], output_file="audio/message.mp3", voice="ru-RU-SvetlanaNeural")
                ),
                daemon=True
            ).start()
    else:
        threading.Thread(
            target=lambda: asyncio.run(
                generate_audio(message["content"], output_file="audio/message.mp3", voice="ru-RU-SvetlanaNeural")
            ),
            daemon=True
        ).start()
    # После обработки ответа от GPT, добавляем сообщение от ассистента в контекст
    local_conversation.add_message(role="assistant", content=message["content"])
    print("Ответ от GPT:", message["content"])

    # Формируем статус для возврата
    status = {
        "status": 200,
        "gptMessage": message["content"],
        "go_to_sleep": False,
        "statusMessage": "Success"
    }

    # Запускаем озвучку в отдельном потоке (fire-and-forget)
    

    def run_tts():
        import asyncio
        # Используем встроенный TTS с голосом Svetlana
        asyncio.run(generate_audio(message["content"], output_file="audio/message.mp3", voice="ru-RU-SvetlanaNeural"))

    threading.Thread(target=run_tts, daemon=True).start()

    # Немедленно возвращаем статус, не дожидаясь завершения озвучки
    return status