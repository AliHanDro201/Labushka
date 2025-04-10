# integrations/browser_chat.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def send_query_to_chatgpt(query: str) -> str:
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Открываем новую вкладку с сайтом ChatGPT
        driver.execute_script("window.open('https://chatgpt.com/', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get("https://chatgpt.com/")
        print("Открываем https://chatgpt.com/ в новой вкладке...")

        # Создаём объект ожидания (15 секунд)
        wait = WebDriverWait(driver, 15)
        # Ждём, пока элемент для ввода запроса (div с id 'prompt-textarea' и contenteditable='true')
        # не станет кликабельным.
        input_box = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div#prompt-textarea[contenteditable='true']"))
        )
        
        # Прокручиваем элемент в видимую область и фокусируем его
        driver.execute_script("arguments[0].scrollIntoView(true);", input_box)
        time.sleep(1)  # Задержка для завершения анимации/перемещения
        
        # Очищаем содержимое элемента (так как это div, используем JS)
        driver.execute_script("arguments[0].innerHTML = '';", input_box)
        
        # Устанавливаем фокус и отправляем запрос
        input_box.click()
        input_box.send_keys(query)
        input_box.send_keys(Keys.RETURN)
        
        print("Отправлен запрос, ожидаем появления ответа...")
        # Ждём появления блока с ответом
        answer_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.flex-col.gap-3"))
        )
        
        messages = driver.find_elements(By.CSS_SELECTOR, ".flex.flex-col.gap-3")
        answer_text = messages[-1].text if messages else "Ответ не найден."
        print("Получен ответ:", answer_text)
        return answer_text
    except Exception as e:
        print("Ошибка при получении ответа:", e)
        return f"Ошибка: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    result = send_query_to_chatgpt("Расскажи о Казахстане")
    print("Ответ от ChatGPT:", result)
