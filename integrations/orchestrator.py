# integrations/orchestrator.py
from integrations.browser_chat import send_query_to_chatgpt
import threading
import asyncio
from utils.tts import generate_audio

def orchestrate_browser_chat(query: str) -> dict:
    """
    Выполняет запрос к ChatGPT через браузер, получает ответ,
    затем запускает TTS для озвучки и возвращает ответ.
    """
    answer = send_query_to_chatgpt(query)
    print("Ответ из браузера:", answer)
    
    # Запускаем TTS в отдельном потоке (чтобы не блокировать основной поток)
    def run_tts():
        asyncio.run(generate_audio(answer, output_file="audio/message.mp3", voice="ru-RU-SvetlanaNeural"))
    
    threading.Thread(target=run_tts, daemon=True).start()
    
    return {"status": 200, "message": answer, "source": "browser_chat"}

# Пример вызова:
if __name__ == "__main__":
    result = orchestrate_browser_chat("Расскажи о Казахстане")
    print("Orchestrator result:", result)