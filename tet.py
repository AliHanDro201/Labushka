from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Открываем ваш скриншот
img_path = "interface_cache/_W _ _80890_.png"
image = Image.open(img_path)

# Распознаем текст
text = pytesseract.image_to_string(image, lang="rus")

print("Распознанный текст:", text)