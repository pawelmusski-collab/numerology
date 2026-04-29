"""
Генерация PNG-изображения психоматрицы (квадрат Пифагора) через Pillow.
"""
import io
from PIL import Image, ImageDraw, ImageFont

# Цвета
BG_COLOR = (18, 18, 28)          # тёмно-синий фон
CARD_COLOR = (28, 28, 42)        # фон карточки
BORDER_COLOR = (80, 60, 140)     # фиолетовая рамка
HEADER_COLOR = (45, 35, 75)      # фон заголовка
DIGIT_COLOR = (200, 170, 255)    # цвет цифр в ячейках
EMPTY_COLOR = (70, 60, 100)      # цвет точки (пусто)
LABEL_COLOR = (140, 120, 200)    # цвет подписей
TITLE_COLOR = (230, 210, 255)    # цвет заголовка
SUBTITLE_COLOR = (160, 140, 210) # цвет подзаголовка
STRONG_COLOR = (100, 220, 150)   # зелёный — сильные стороны
WEAK_COLOR = (220, 150, 100)     # оранжевый — зоны роста
LINE_COLOR = (60, 50, 100)       # цвет разделителей

MATRIX_LAYOUT = [
    [3, 6, 9],
    [2, 5, 8],
    [1, 4, 7],
]

CELL_MEANINGS = {
    1: "Характер",
    2: "Энергия",
    3: "Интерес",
    4: "Здоровье",
    5: "Интуиция",
    6: "Труд",
    7: "Удача",
    8: "Долг",
    9: "Память",
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


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Загружаем шрифт — пробуем системные, fallback на default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def generate_psychomatrix_image(counts: dict, birth_date: str, belova_number: int) -> io.BytesIO:
    """
    Генерирует PNG психоматрицы и возвращает BytesIO для отправки в Telegram.
    """
    # Размеры
    W = 600
    CELL_SIZE = 120
    GRID_X = 60          # начало сетки по X
    GRID_Y = 130         # начало сетки по Y
    GRID_W = CELL_SIZE * 3
    GRID_H = CELL_SIZE * 3
    LEGEND_Y = GRID_Y + GRID_H + 30
    H = LEGEND_Y + 320

    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Шрифты
    font_title = _get_font(22, bold=True)
    font_subtitle = _get_font(15)
    font_digit = _get_font(36, bold=True)
    font_label = _get_font(12)
    font_legend_title = _get_font(13, bold=True)
    font_legend_text = _get_font(12)

    # --- Заголовок ---
    draw.text((W // 2, 22), "Психоматрица (квадрат Пифагора)",
              font=font_title, fill=TITLE_COLOR, anchor="mm")
    draw.text((W // 2, 52), f"Дата рождения: {birth_date}  •  Число Беловой: {belova_number}",
              font=font_subtitle, fill=SUBTITLE_COLOR, anchor="mm")

    # Разделитель
    draw.line([(40, 72), (W - 40, 72)], fill=BORDER_COLOR, width=1)

    # Подписи строк (справа от сетки)
    row_labels = ["3 · 6 · 9", "2 · 5 · 8", "1 · 4 · 7"]
    col_labels = ["3", "6", "9", "2", "5", "8", "1", "4", "7"]

    # --- Сетка 3x3 ---
    for row_i, row in enumerate(MATRIX_LAYOUT):
        for col_i, digit in enumerate(row):
            x0 = GRID_X + col_i * CELL_SIZE
            y0 = GRID_Y + row_i * CELL_SIZE
            x1 = x0 + CELL_SIZE
            y1 = y0 + CELL_SIZE

            count = counts[digit]

            # Фон ячейки — чуть светлее если есть цифры
            cell_bg = (35, 28, 58) if count > 0 else (22, 18, 38)
            draw.rectangle([x0, y0, x1, y1], fill=cell_bg)

            # Цифры в ячейке
            cx = x0 + CELL_SIZE // 2
            cy = y0 + CELL_SIZE // 2 - 12

            if count > 0:
                digit_str = str(digit) * count
                # Размер шрифта зависит от количества цифр
                if count <= 2:
                    f = _get_font(38, bold=True)
                elif count <= 4:
                    f = _get_font(28, bold=True)
                else:
                    f = _get_font(20, bold=True)
                draw.text((cx, cy), digit_str, font=f, fill=DIGIT_COLOR, anchor="mm")
            else:
                draw.text((cx, cy), "·", font=_get_font(32), fill=EMPTY_COLOR, anchor="mm")

            # Подпись качества под цифрами
            label = CELL_MEANINGS.get(digit, "")
            draw.text((cx, y0 + CELL_SIZE - 16), label,
                      font=font_label, fill=LABEL_COLOR, anchor="mm")

    # Рамка сетки и линии
    for i in range(4):
        # Вертикальные линии
        x = GRID_X + i * CELL_SIZE
        draw.line([(x, GRID_Y), (x, GRID_Y + GRID_H)], fill=BORDER_COLOR, width=2)
        # Горизонтальные линии
        y = GRID_Y + i * CELL_SIZE
        draw.line([(GRID_X, y), (GRID_X + GRID_W, y)], fill=BORDER_COLOR, width=2)

    # --- Легенда справа от сетки ---
    leg_x = GRID_X + GRID_W + 30
    leg_y = GRID_Y

    draw.text((leg_x, leg_y), "Значение ячеек:", font=font_legend_title, fill=TITLE_COLOR)
    leg_y += 22

    for row in MATRIX_LAYOUT:
        for digit in row:
            meaning = CELL_MEANINGS_FULL[digit]
            draw.text((leg_x, leg_y), f"{digit} — {meaning['name']}",
                      font=font_legend_text, fill=LABEL_COLOR)
            leg_y += 16
        leg_y += 4

    # --- Блок сильных сторон и зон роста ---
    draw.line([(40, LEGEND_Y - 10), (W - 40, LEGEND_Y - 10)], fill=LINE_COLOR, width=1)

    strong = [(d, c) for d, c in counts.items() if c >= 3]
    weak = [(d, c) for d, c in counts.items() if c == 0]

    ly = LEGEND_Y + 5

    if strong:
        draw.text((50, ly), "💪 Сильные стороны:", font=font_legend_title, fill=STRONG_COLOR)
        ly += 20
        for digit, _ in strong:
            m = CELL_MEANINGS_FULL[digit]
            draw.text((60, ly), f"• {m['name']}: {m['high']}", font=font_legend_text, fill=STRONG_COLOR)
            ly += 17

    ly += 8

    if weak:
        draw.text((50, ly), "🔮 Зоны роста:", font=font_legend_title, fill=WEAK_COLOR)
        ly += 20
        for digit, _ in weak:
            m = CELL_MEANINGS_FULL[digit]
            draw.text((60, ly), f"• {m['name']}: {m['low']}", font=font_legend_text, fill=WEAK_COLOR)
            ly += 17

    if not strong and not weak:
        draw.text((50, ly), "✨ Гармоничная психоматрица — все качества развиты в меру.",
                  font=font_legend_text, fill=LABEL_COLOR)

    # Обрезаем по реальной высоте
    actual_h = max(ly + 30, LEGEND_Y + 60)
    img = img.crop((0, 0, W, actual_h))

    # Сохраняем в BytesIO
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf
