import random
import re
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_WIDTH = 200
AVATAR_HEIGHT = 200
AVATAR_SIZE = (AVATAR_WIDTH, AVATAR_HEIGHT)
AVATAR_FONT_SIZE = 100
DEFAULT_AVATAR_LETTER = "U"

COLOR_BLUE = "#5b86e5"
COLOR_CYAN = "#36d1dc"
COLOR_ORANGE = "#ff9966"
COLOR_RED = "#ff5e62"
COLOR_TEAL = "#11998e"
COLOR_GREEN = "#38ef7d"

AVATAR_BG_COLORS = [
    COLOR_BLUE,
    COLOR_CYAN,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_TEAL,
    COLOR_GREEN,
]
TEXT_COLOR = "white"

IMAGE_MODE = "RGB"
IMAGE_FORMAT = "PNG"
IMAGE_EXTENSION = "png"
FONT_FILE_NAME = "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"

RANDOM_FILENAME_MIN = 1000
RANDOM_FILENAME_MAX = 9999

TEXT_ANCHOR_X = 0
TEXT_ANCHOR_Y = 0

PHONE_PREFIX_RU = "8"
PHONE_PREFIX_INTL = "+7"


def generate_avatar(name):
    bg_color = random.choice(AVATAR_BG_COLORS)

    image = Image.new(IMAGE_MODE, AVATAR_SIZE, color=bg_color)
    draw = ImageDraw.Draw(image)

    letter = name[0].upper() if name else DEFAULT_AVATAR_LETTER

    font_path = settings.BASE_DIR / "static" / "fonts" / FONT_FILE_NAME

    try:
        font = ImageFont.truetype(str(font_path), AVATAR_FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    left, top, right, bottom = draw.textbbox(
        (TEXT_ANCHOR_X, TEXT_ANCHOR_Y), letter, font=font
    )
    text_width = right - left
    text_height = bottom - top
    position = (
        (AVATAR_SIZE[0] - text_width) / 2,
        (AVATAR_SIZE[1] - text_height) / 2 - top,
    )

    draw.text(position, letter, fill=TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format=IMAGE_FORMAT)

    file_name = f"avatar_{random.randint(RANDOM_FILENAME_MIN, RANDOM_FILENAME_MAX)}.{IMAGE_EXTENSION}"
    return ContentFile(buffer.getvalue(), name=file_name)


def normalize_and_validate_phone(phone, exclude_pk=None):
    if not phone:
        raise ValidationError("Это поле обязательно.")

    if not re.match(r"^(8|\+7)\d{10}$", phone):
        raise ValidationError(
            "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )

    if phone.startswith(PHONE_PREFIX_RU):
        phone = PHONE_PREFIX_INTL + phone[1:]

    User = get_user_model()
    qs = User.objects.filter(phone=phone)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError("Пользователь с таким номером телефона уже существует.")

    return phone
