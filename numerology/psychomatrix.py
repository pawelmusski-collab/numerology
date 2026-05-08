import json

CELL_MEANINGS = {
    1: {"name": "Характер / Воля", "low": "Мягкий, уступчивый", "mid": "Целеустремлённый", "high": "Волевой, упрямый"},
    2: {"name": "Энергия / Биополе", "low": "Низкий энергетический потенциал", "mid": "Хороший энергобаланс", "high": "Мощная жизненная сила"},
    3: {"name": "Интерес к науке", "low": "Практик без теории", "mid": "Любознательный", "high": "Аналитический ум, учёный"},
    4: {"name": "Здоровье", "low": "Слабое здоровье, нужна забота", "mid": "Среднее здоровье", "high": "Богатырское здоровье"},
    5: {"name": "Интуиция / Логика", "low": "Логик, интуиция слабая", "mid": "Баланс логики и интуиции", "high": "Мощная интуиция"},
    6: {"name": "Трудолюбие", "low": "Труд даётся тяжело", "mid": "Работоспособный", "high": "Трудоголик"},
    7: {"name": "Удача / Везение", "low": "Удача приходит через труд", "mid": "Периодически везёт", "high": "Баловень судьбы"},
    8: {"name": "Долг / Ответственность", "low": "Избегает обязательств", "mid": "Ответственный", "high": "Гиперответственный"},
    9: {"name": "Память / Интеллект", "low": "Практический ум", "mid": "Хорошая память", "high": "Феноменальная память"},
}

# Исправленный порядок строк: 1-4-7 / 2-5-8 / 3-6-9
MATRIX_LAYOUT = [
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
]


def calculate_numbers(day: int, month: int, year: int) -> dict:
    """Считает все числа: метацикл, базовое, икс, коммуникативное, уровень души."""
    dob = f"{day:02d}{month:02d}{year}"
    metacycle = sum(int(d) for d in dob)          # двузначное (или однозначное)
    base = sum(int(d) for d in str(metacycle))    # сумма цифр метацикла
    first_digit_of_day = int(str(day)[0])
    x_number = metacycle - 2 * first_digit_of_day
    communicative = sum(int(d) for d in str(x_number)) if x_number > 0 else 0
    soul_level = base + communicative
    return {
        "metacycle": metacycle,
        "base": base,
        "x_number": x_number,
        "communicative": communicative,
        "soul_level": soul_level,
    }


def calculate_psychomatrix(day: int, month: int, year: int) -> dict:
    """Считаем кол-во каждой цифры 1-9 во всех рабочих числах включая новые."""
    nums = calculate_numbers(day, month, year)
    metacycle = nums["metacycle"]
    base = nums["base"]
    x_number = nums["x_number"]
    communicative = nums["communicative"]

    # Рабочие числа для матрицы: дата + метацикл + базовое + икс + коммуникативное
    all_digits = f"{day:02d}{month:02d}{year}{metacycle}{base}{x_number}{communicative}"

    counts = {i: 0 for i in range(1, 10)}
    for ch in all_digits:
        digit = int(ch)
        if 1 <= digit <= 9:
            counts[digit] += 1
    return counts


def get_psychomatrix_summary(counts: dict) -> str:
    strong, weak = [], []
    for digit, count in counts.items():
        m = CELL_MEANINGS[digit]
        if count >= 3:
            strong.append(f"• {m['name']}: {m['high']}")
        elif count == 0:
            weak.append(f"• {m['name']}: {m['low']}")
    result = ""
    if strong:
        result += "💪 *Сильные стороны:*\n" + "\n".join(strong) + "\n\n"
    if weak:
        result += "🔮 *Зоны роста:*\n" + "\n".join(weak)
    return result or "Гармоничная психоматрица — все качества развиты в меру."


def psychomatrix_to_json(counts: dict) -> str:
    return json.dumps(counts)
