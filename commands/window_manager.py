import os
import cv2
import json
import time
import pyautogui
import pytesseract
import numpy as np
import pywinctl as gw
from typing import Optional, Tuple, Dict

# Путь для хранения кэша интерфейсов
CACHE_DIR = "interface_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """
    Убирает неподдерживаемые символы из имени файла.
    """
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in filename)

def get_active_window_screenshot() -> Optional[str]:
    """
    Делает скриншот активного окна и сохраняет его.
    """
    try:
        active_window = gw.getActiveWindow()
        if not active_window:
            print("⚠ Не удалось получить активное окно.")
            return None

        # Фильтруем имя файла, убирая неподдерживаемые символы
        window_title = sanitize_filename(active_window.title)
        
        screenshot_path = os.path.join(CACHE_DIR, f"{window_title}_{int(time.time())}.png")

        print(f"📸 Делаем скриншот окна: {window_title}")

        # Проверяем размеры окна
        if active_window.width == 0 or active_window.height == 0:
            print("❌ Ошибка: Окно имеет нулевые размеры!")
            return None

        # Делаем скриншот
        img = pyautogui.screenshot(region=(
            active_window.left,
            active_window.top,
            active_window.width,
            active_window.height
        ))

        img.save(screenshot_path)

        # Проверяем, создался ли файл
        if not os.path.exists(screenshot_path):
            print(f"❌ Ошибка: Файл {screenshot_path} не создан!")
            return None

        print(f"✅ Скриншот сохранен: {screenshot_path}")
        return screenshot_path

    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None

from PIL import Image

def extract_text_elements(image_path: str) -> Dict[str, Tuple[int, int]]:
    """
    Распознает текст на скриншоте и возвращает координаты каждого элемента.
    """
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            print(f"❌ Ошибка: Файл {image_path} не найден!")
            return {}

        # Проверяем размер файла
        if os.path.getsize(image_path) == 0:
            print(f"❌ Ошибка: Файл {image_path} пуст!")
            return {}

        print(f"🔍 Анализируем изображение: {image_path}")

        # Открываем изображение через PIL (устраняет проблемы с cv2)
        img = Image.open(image_path).convert("RGB")

        # Конвертируем в OpenCV для обработки
        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Используем pytesseract для распознавания текста
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        elements = {}
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                elements[text] = (x + w//2, y + h//2)

        print(f"✅ Найдено {len(elements)} элементов интерфейса")
        return elements

    except Exception as e:
        print(f"❌ Ошибка при извлечении текста: {e}")
        return {}

def save_interface_cache(window_title: str, elements: Dict[str, Tuple[int, int]]):
    """
    Сохраняет данные интерфейса в JSON-файл для кэширования.
    """
    cache_path = os.path.join(CACHE_DIR, f"{window_title}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(elements, f, ensure_ascii=False, indent=4)

def load_interface_cache(window_title: str) -> Optional[Dict[str, Tuple[int, int]]]:
    """
    Загружает данные интерфейса из кэша, если они существуют.
    """
    cache_path = os.path.join(CACHE_DIR, f"{window_title}.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None





import string
import re

def normalize_text(text: str) -> str:
    """
    Убирает из текста кавычки, пунктуацию в начале/конце
    и приводит к нижнему регистру.
    """
    # Удаляем распространённые типы кавычек
    for ch in ["‘", "’", "“", "”", "'", "\"", "«", "»"]:
        text = text.replace(ch, "")

    # Можно убрать и всю пунктуацию, но аккуратно:
    # text = text.translate(str.maketrans('', '', string.punctuation))

    # Для точечной очистки от :, . в начале/конце можно использовать регулярку:
    text = text.strip(string.punctuation + " ")

    return text.lower()










def click_button(button_text: str) -> str:
    """
    Находит и нажимает кнопку с указанным текстом,
    каждый раз делая новый скриншот (без использования кэша).
    """
    from PIL import Image

    active_window = gw.getActiveWindow()
    if not active_window:
        return "Не удалось определить активное окно."

    # 1. Делаем скриншот активного окна
    screenshot_path = get_active_window_screenshot()
    if not screenshot_path:
        return "Ошибка: не удалось сделать скриншот окна."

    # 2. Открываем скриншот
    img = Image.open(screenshot_path)
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

    # 3. С помощью pytesseract распознаём слова
    data = pytesseract.image_to_data(img_cv, lang="rus+eng", output_type=pytesseract.Output.DICT)
    elements = {}
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        raw_word = data['text'][i].strip()
        if raw_word:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            cx, cy = x + w // 2, y + h // 2
            # Используем вашу функцию normalize_text, чтобы убрать кавычки и т.д.
            norm_word = normalize_text(raw_word)
            if norm_word:
                elements[norm_word] = (cx, cy)

    print("🔍 Найденные (нормализованные) слова:", elements.keys())

    # 4. Сопоставляем нужное слово
    search_key = normalize_text(button_text)
    if search_key in elements:
        x, y = elements[search_key]
        pyautogui.click(x, y)
        return f"✅ Нажал кнопку '{button_text}'."

    return f"❌ Кнопка '{button_text}' не найдена. Убедитесь, что она видна на экране."

