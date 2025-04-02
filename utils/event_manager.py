# utils/event_manager.py
import threading

class EventManager:
    def __init__(self):
        # Используем объект threading.Event для контроля состояния
        self._stop_audio_event = threading.Event()
    
    def request_stop_audio(self):
        """Устанавливает флаг остановки аудио."""
        self._stop_audio_event.set()
    
    def reset_stop_audio(self):
        """Сбрасывает флаг остановки аудио."""
        self._stop_audio_event.clear()
    
    def should_stop_audio(self) -> bool:
        """Проверяет, установлен ли флаг остановки аудио."""
        return self._stop_audio_event.is_set()

# Создаем глобальный экземпляр (при необходимости можно создать его и передавать как зависимость)
event_manager = EventManager()
