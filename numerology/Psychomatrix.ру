"""
Психоматрица (квадрат Пифагора) — классическая нумерологическая таблица 3x3.
Расчёт: из даты рождения извлекаем рабочие числа, считаем кол-во каждой цифры 1-9.
"""
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

MATRIX_LAYOUT = [
    [3, 6, 9],
    [2, 5, 8],
    [1, 4, 7],
]


def _get_working_numbers(day: int, month: int, year: int) -> list[int]:
    """Вычисляем рабочие числа для психоматрицы."""
    dob = f"{day:02d}{month:02d}{year}"
    first_sum = sum(int(d) for d in dob)

    # Редуцируем до однозначного
    second_sum = sum(int(d) for d in str(first_sum))
    if first_sum > 9:
        second_sum = sum(int(d) for d in str(first_sum))
    else:
        second_sum = first_sum

    third_sum = first_sum - 2 * int(str(day)[0]) if day >= 10 else first_sum - 2 * day
    fourth_sum = sum(int(d) for d in str(third_sum))

    return [day, month, year, first_sum, second_sum, third_sum, fourth_sum]


def calculate_psychomatrix(day: int, month: int, year: int) -> dict:
    """Считаем кол-во каждой цифры 1-9 в рабочих числах."""
    numbers = _get_working_numbers(day, month, year)
    all_digits = "".join(str(n) for n in numbers)

    counts = {i: 0 for i in range(1, 10)}
    for ch in all_digits:
        digit = int(ch)
        if 1 <= digit <= 9:
            counts[digit] += 1

    return counts


def get_psychomatrix_summary(counts: dict) -> str:
    """Краткое описание сильных и слабых сторон по психоматрице."""
    strong = []
    weak = []

    for digit, count in counts.items():
        meaning = CELL_MEANINGS[digit]
        if count >= 3:
            strong.append(f"• {meaning['name']}: {meaning['high']}")
        elif count == 0:
            weak.append(f"• {meaning['name']}: {meaning['low']}")

    result = ""
    if strong:
        result += "💪 *Сильные стороны:*\n" + "\n".join(strong) + "\n\n"
    if weak:
        result += "🔮 *Зоны роста:*\n" + "\n".join(weak)

    if not result:
        result = "Гармоничная психоматрица — все качества развиты в меру."

    return result


def format_psychomatrix_table(counts: dict) -> str:
    """Красивая текстовая матрица 3x3."""
    def cell(digit: int) -> str:
        c = counts[digit]
        return str(digit) * c if c > 0 else "·"

    rows = []
    for row in MATRIX_LAYOUT:
        rows.append("│ " + " │ ".join(f"{cell(d):^5}" for d in row) + " │")

    separator = "├" + "───────┼" * 2 + "───────┤"
    top = "┌" + "───────┬" * 2 + "───────┐"
    bottom = "└" + "───────┴" * 2 + "───────┘"

    header = "│  3/9  │  6/5  │  9/7  │"

    table = f"`{top}\n{rows[0]}\n{separator}\n{rows[1]}\n{separator}\n{rows[2]}\n{bottom}`"
    return table


def psychomatrix_to_json(counts: dict) -> str:
    return json.dumps(counts)
