import pytesseract
from fastapi import UploadFile
from PIL import Image
import io

def ocr_image_to_text(textboox_image: UploadFile):
    image_byte = textboox_image.file.read()
    image = Image.open(io.BytesIO(image_byte))
    text = pytesseract.image_to_string(image, lang='kor+eng')
    
    return text