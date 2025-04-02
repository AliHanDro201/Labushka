"""
Этот файл содержит функции, которые обрабатывают функцию преобразования текста в речь. 
Функция generate_audio — единственная, которая вам нужна для генерации и воспроизведения звука.
"""

import os
import time
import asyncio
import pygame
import edge_tts
import keyboard
import threading

# Импортируем централизованный менеджер событий
from utils.event_manager import event_manager
# Импортируем настройки TTS из config.py
from core.config import TTS_DEFAULT_VOICE

# Если есть логгер, можно импортировать его (опционально)
# from utils.logger import logger

def stop_audio():
    """Останавливает озвучку при нажатии CapsLock."""
    event_manager.request_stop_audio()  # Устанавливаем флаг остановки
    pygame.mixer.quit()  # Полностью сбрасываем аудиосистему
    print("🔇 Озвучка остановлена (CapsLock).")
    # logger.info("Озвучка остановлена (CapsLock).")  # если настроен логгер

def listen_capslock():
    """Отслеживает нажатие CapsLock и останавливает озвучку."""
    while True:
        keyboard.wait("caps lock")
        stop_audio()

# Регистрируем горячую клавишу CapsLock для остановки озвучки
keyboard.add_hotkey("caps lock", stop_audio)
# Запускаем прослушиватель CapsLock в отдельном потоке
capslock_thread = threading.Thread(target=listen_capslock, daemon=True)
capslock_thread.start()

async def generate_audio(text: str, output_file: str = "audio/message.mp3", voice: str = TTS_DEFAULT_VOICE):
    """
    Генерирует аудио и воспроизводит его.
    
    Использует edge_tts для генерации аудио, а затем воспроизводит его через pygame.
    """
    # Сбрасываем флаг остановки перед началом генерации
    event_manager.reset_stop_audio()

    try:
        pygame.mixer.quit()  # Очищаем прошлые звуки
        pygame.mixer.init()

        # Генерация аудио с помощью edge_tts
        tts = edge_tts.Communicate(text, voice)
        await tts.save(output_file)

        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()

        # Проверяем флаг остановки аудио каждые 0.1 сек
        while pygame.mixer.music.get_busy():
            if event_manager.should_stop_audio():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                print("🔇 Озвучка была остановлена.")
                # logger.info("Озвучка была остановлена.")
                return
            time.sleep(0.1)

    except pygame.error:
        print("⚠️ Ошибка: Плеер pygame уже остановлен.")
        # logger.error("Ошибка: Плеер pygame уже остановлен.")
    except Exception as e:
        print(f"Ошибка воспроизведения: {e}")
        # logger.exception("Ошибка воспроизведения аудио:")

def listen(awake=False) -> dict:
    """
    Эта функция для распознавания речи на Python.
    Сейчас она не используется, так что можно игнорировать.
    """
    import speech_recognition as sr
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("слушаю...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        print("вы сказали:", text)
        return {"message": text, "error": False}
    
    except sr.UnknownValueError:
        message = "Распознавание не смогло понять, что вы сказали."
        return {"message": message, "error": True}
    
    except sr.RequestError:
        message = "Проблемы с сервисом распознавания речи."
        return {"message": message, "error": True}
