import io
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
FONT_PATH = "/tmp/Nunito.ttf"

BG_COLOR = (18, 18, 28)
BORDER_COLOR = (80, 60, 140)
DIGIT_COLOR = (200, 170, 255)
EMPTY_COLOR = (70, 60, 100)
LABEL_COLOR = (140, 120, 200)
TITLE_COLOR = (230, 210, 255)
SUBTITLE_COLOR = (160, 140, 210)
STRONG_COLOR = (100, 220, 150)
WEAK_COLOR = (220, 150, 100)
LINE_COLOR = (60, 50, 100)

# Исправленный порядок: 1-4-7 / 2-5-8 / 3-6-9
MATRIX_LAYOUT = [
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
]

CELL_MEANINGS = {
    1: "Характер", 2: "Энергия", 3: "Интерес",
    4: "Здоровье", 5: "Интуиция", 6: "Труд",
    7: "Удача", 8: "Долг", 9: "Память",
}

CELL_MEANINGS_FULL = {
    1: {"name": "Характер / Воля", "low": "Мягкий, уступчивый", "high": "Волевой, упрямый"},
    2: {"name": "Энергия / Биополе", "low": "Низкий потенциал", "high": "Мощная сила"},
    3: {"name": "Интерес к науке", "low": "Практик без теории", "high": "Аналитический ум"},
    4: {"name": "Здоровье", "low": "Слабое здоровье", "high": "Богатырское здоровье"},
    5: {"name": "Интуиция / Логика", "low": "Логик без интуиции", "high": "Мощная интуиция"},
    6: {"name": "Трудолюбие", "low": "Труд даётся тяжело", "high": "Трудоголик"},
    7: {"name": "Удача / Везение", "low": "Удача через труд", "high": "Баловень судьбы"},
    8: {"name": "Долг / Ответственность", "low": "Избегает обязательств", "high": "Гиперответственный"},
    9: {"name": "Память / Интеллект", "low": "Практический ум", "high": "Феноменальная память"},
}


def _ensure_font():
    if not os.path.exists(FONT_PATH):
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        _ensure_font()
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def generate_psychomatrix_image(counts: dict, birth_date: str, main_number: int,
                                 extra_numbers: dict | None = None) -> io.BytesIO:
    W, CELL_SIZE = 600, 120
    GRID_X, GRID_Y = 60, 130
    GRID_W, GRID_H = CELL_SIZE * 3, CELL_SIZE * 3
    LEGEND_Y = GRID_Y + GRID_H + 30

    img = Image.new("RGB", (W, LEGEND_Y + 380), BG_COLOR)
    draw = ImageDraw.Draw(img)

    ft = _get_font(22, bold=True)
    fs = _get_font(15)
    fl = _get_font(12)
    flt = _get_font(13, bold=True)
    fle = _get_font(12)

    draw.text((W // 2, 22), "Психоматрица (квадрат Пифагора)", font=ft, fill=TITLE_COLOR, anchor="mm")
    draw.text((W // 2, 52), f"Дата рождения: {birth_date}  •  Нумерологическое число: {main_number}",
              font=fs, fill=SUBTITLE_COLOR, anchor="mm")
    draw.line([(40, 72), (W - 40, 72)], fill=BORDER_COLOR, width=1)

    # Доп числа под заголовком
    if extra_numbers:
        n = extra_numbers
        extra_text = (f"Метацикл: {n['metacycle']}  •  Базовое: {n['base']}  •  "
                      f"Икс: {n['x_number']}  •  Ком.: {n['communicative']}  •  Душа: {n['soul_level']}")
        draw.text((W // 2, 90), extra_text, font=_get_font(11), fill=LABEL_COLOR, anchor="mm")

    for row_i, row in enumerate(MATRIX_LAYOUT):
        for col_i, digit in enumerate(row):
            x0 = GRID_X + col_i * CELL_SIZE
            y0 = GRID_Y + row_i * CELL_SIZE
            count = counts[digit]
            draw.rectangle([x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE],
                           fill=(35, 28, 58) if count > 0 else (22, 18, 38))
            cx, cy = x0 + CELL_SIZE // 2, y0 + CELL_SIZE // 2 - 12
            if count > 0:
                f = _get_font(38 if count <= 2 else 28 if count <= 4 else 20, bold=True)
                draw.text((cx, cy), str(digit) * count, font=f, fill=DIGIT_COLOR, anchor="mm")
            else:
                draw.text((cx, cy), "·", font=_get_font(32), fill=EMPTY_COLOR, anchor="mm")
            draw.text((cx, y0 + CELL_SIZE - 16), CELL_MEANINGS.get(digit, ""),
                      font=fl, fill=LABEL_COLOR, anchor="mm")

    for i in range(4):
        draw.line([(GRID_X + i * CELL_SIZE, GRID_Y), (GRID_X + i * CELL_SIZE, GRID_Y + GRID_H)],
                  fill=BORDER_COLOR, width=2)
        draw.line([(GRID_X, GRID_Y + i * CELL_SIZE), (GRID_X + GRID_W, GRID_Y + i * CELL_SIZE)],
                  fill=BORDER_COLOR, width=2)

    leg_x, leg_y = GRID_X + GRID_W + 30, GRID_Y
    draw.text((leg_x, leg_y), "Значение ячеек:", font=flt, fill=TITLE_COLOR)
    leg_y += 22
    for row in MATRIX_LAYOUT:
        for digit in row:
            draw.text((leg_x, leg_y), f"{digit} — {CELL_MEANINGS_FULL[digit]['name']}",
                      font=fle, fill=LABEL_COLOR)
            leg_y += 16
        leg_y += 4

    draw.line([(40, LEGEND_Y - 10), (W - 40, LEGEND_Y - 10)], fill=LINE_COLOR, width=1)
    strong = [(d, c) for d, c in counts.items() if c >= 3]
    weak = [(d, c) for d, c in counts.items() if c == 0]
    ly = LEGEND_Y + 5

    if strong:
        draw.text((50, ly), "Сильные стороны:", font=flt, fill=STRONG_COLOR)
        ly += 20
        for digit, _ in strong:
            draw.text((60, ly), f"• {CELL_MEANINGS_FULL[digit]['name']}: {CELL_MEANINGS_FULL[digit]['high']}",
                      font=fle, fill=STRONG_COLOR)
            ly += 17
    ly += 8
    if weak:
        draw.text((50, ly), "Зоны роста:", font=flt, fill=WEAK_COLOR)
        ly += 20
        for digit, _ in weak:
            draw.text((60, ly), f"• {CELL_MEANINGS_FULL[digit]['name']}: {CELL_MEANINGS_FULL[digit]['low']}",
                      font=fle, fill=WEAK_COLOR)
            ly += 17
    if not strong and not weak:
        draw.text((50, ly), "Гармоничная психоматрица — все качества развиты в меру.",
                  font=fle, fill=LABEL_COLOR)
        ly += 17

    img = img.crop((0, 0, W, max(ly + 30, LEGEND_Y + 60)))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf
