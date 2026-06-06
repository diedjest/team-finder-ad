import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.conf import settings


def generate_avatar(name):
    size = (200, 200)
    colors = ['#5b86e5', '#36d1dc', '#ff9966', '#ff5e62', '#11998e', '#38ef7d']
    bg_color = random.choice(colors)

    image = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(image)

    letter = name[0].upper() if name else "U"

    font_name = "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
    font_path = settings.BASE_DIR / "static" / "fonts" / font_name

    try:
        font = ImageFont.truetype(str(font_path), 100)
    except IOError:
        font = ImageFont.load_default()

    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    text_width = right - left
    text_height = bottom - top
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2 - top)

    draw.text(position, letter, fill="white", font=font)

    buffer = BytesIO()
    image.save(buffer, format='PNG')

    file_name = f"avatar_{random.randint(1000, 9999)}.png"
    return ContentFile(buffer.getvalue(), name=file_name)
