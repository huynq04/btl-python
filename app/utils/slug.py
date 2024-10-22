import re
import unicodedata

def generate_slug(text: str) -> str:
    # Chuyển chuỗi sang chữ thường
    text = text.lower()

    # Loại bỏ dấu (nếu có) và chuẩn hóa chuỗi
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    # Thay thế các ký tự không phải chữ cái hoặc số bằng dấu gạch ngang
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # Loại bỏ dấu gạch ngang dư thừa ở đầu và cuối
    text = text.strip('-')

    return text
