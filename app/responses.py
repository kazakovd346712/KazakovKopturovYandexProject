from dataclasses import dataclass


@dataclass
class Phrases:
    """Датакласс для фраз Алисы"""

    greeting = ('Начинаем игру в города. Напиши "{}", чтобы узнать правила. Я называю город {}.', )

    name_city = ("city {} [1]", 'city {} [2]', "city {} [3]")

    invalid_first_letter = ('invalid first letter. Should start with "{}" [1]',
                            'invalid first letter. Should start with "{}" [2]',
                            'invalid first letter. Should start with "{}" [3]')

    city_not_found = ("dont know this city [1]", "dont know this city [1]", "dont know this city [1]")

    city_already_used = ("city already used [1]", "city already used [2]", "city already used [3]")

    surrender = ("surrender [1]", "surrender [2]", "surrender [3]")

    win = ("I won [1]", "I won [2]", "I won [3]")

    rules = ("""Правила игры "Города":
1. Называешь город России
2. Я называю город на последнюю букву твоего
3. Повторяться нельзя
5. Буквы Ъ, Ь и Ы игнорируются (берётся предпоследняя)

Команды:
"{}" - сдаться
"{}" - показать город на карте
"{}" - показать это сообщение""", )

