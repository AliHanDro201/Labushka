# core/agent.py
import asyncio
import elevenlabs as eleven
from concurrent.futures import ThreadPoolExecutor
import openai
from utils.tts import generate_audio
import json
# Импортируем нужные конфиги
from core.conversation import Conversation
from core.config import prompt, GPT_MODEL, GPT_TEMPERATURE, GPT_MAX_TOKENS, OPENAI_API_KEY
from commands.commands_as_json import commands

# Устанавливаем API ключ
openai.api_key = OPENAI_API_KEY

# Создаем глобальный пул потоков (можно настроить количество потоков по необходимости)
executor = ThreadPoolExecutor(max_workers=4)

# Conversation с промптом из config.py
conversation = Conversation(prompt)

def get_voices():
    """
    Use this to view the list of voices that can be used
    for text-to-speech.
    """
    return eleven.voices()  


# * The following Voice ID is for my preferred voice --> Caroline
# * You can view all the voices available to you with this link, 
# * then set the ID of the voice you want:
# https://api.elevenlabs.io/docs#/voices/Get_voices_v1_voices_get
VOICE_ID : str = "XrExE9yKIg1WjnnlVkGX"

try:
    voices = get_voices()

    main_voice = list(filter(lambda voice: voice.voice_id == VOICE_ID, voices))

    # * If my voice isn't available to you, then a default voice is selected.
    if len(main_voice) > 0:
        main_voice = main_voice[0]
    else:
        main_voice = list(filter(lambda voice: voice.name.lower() == "matilda", voices))[0]
except:
    main_voice = None
# *******************************


# === Основная функция ===
async def async_chat_completion(user_text: str) -> dict:
    status = {
        "status": 200,
        "statusMessage": "",
        "gptMessage": "",
        "go_to_sleep": False
    }
    # Создаем новый объект conversation для каждого запроса
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
        return {"status": 500, "statusMessage": str(e)}
    ##########################################
    print("Raw response from OpenAI:", response)
    ##########################################
    message = response["choices"][0]["message"]

    if message.get("function_call"):
        # Обработка вызова функции
        function_name = message["function_call"]["name"]
        arguments = message["function_call"].get("arguments", "{}")
        print(f"GPT вызвал функцию: {function_name} с аргументами {arguments}")

        local_conversation.add_message(role="function", content=f"Вызов функции {function_name} с аргументами {arguments}")

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

    conversation.add_message(content=message["content"], role="assistant")
    print(message["content"])

        # * Generate audio from ChatGPT's response
        # * Generate audio from ChatGPT's response
        # * Generate audio from ChatGPT's response
    if main_voice:
        try:
            # * Генерация аудио с ElevenLabs (Dmitry)
            audio = eleven.generate(
                text=message["content"],
                voice="Dmitry",
                model="eleven_multilingual_v1"
            )
            
            eleven.save(audio, "audio/message.wav")
        except Exception as e:
            print(f"Eleven Labs error: {e}")
            print("Используем встроенный TTS с голосом Svetlana")

                # * Генерация аудио с голосом Светланы
            asyncio.run(generate_audio(message["content"], output_file="audio/message.mp3", voice="ru-RU-SvetlanaNeural"))
    else:
        # * Если ElevenLabs не работает, используем голос Светланы
        asyncio.run(generate_audio(message["content"], output_file="audio/message.mp3", voice="ru-RU-SvetlanaNeural"))



        # * Get the message to the frontend.
        status["gptMessage"] = message["content"]
        status["statusMessage"] = "Success"

        return json.dumps(status)

    local_conversation.add_message(role="assistant", content=message["content"])

    return {"status": 200, "gptMessage": message["content"], "go_to_sleep": False}
    

