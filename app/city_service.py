import csv
from random import randint

CITIES_FILE = "data/cities.csv"


def _group_cities_by_letters() -> dict:
    """Возвращает словарь городов с ключами по первым буквам"""

    result = {}

    with open(CITIES_FILE, encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=",")

        for row in reader:
            city_name = row["name"]
            first_letter = city_name[0].lower()
            if first_letter not in result:
                result[first_letter] = [city_name]
            else:
                result[first_letter].append(city_name)

    return result


def _map_names_to_alt() -> dict:
    """Возвращает словарь именами городов по ключам name_alt (только для различающихся name и name_alt)"""

    result = {}

    with open(CITIES_FILE, encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=",")

        for row in reader:
            city_name = row["name"]
            city_name_alt = row["name_alt"]
            if city_name_alt not in result and city_name != city_name_alt:
                result[city_name_alt] = city_name

    return result


CITIES_NAMES = _group_cities_by_letters()
ALT_NAMES = _map_names_to_alt()


def check_city(city_name: str) -> bool:
    """Проверяет, есть ли город в базе городов"""

    first_letter = city_name[0].lower()

    if first_letter in CITIES_NAMES:
        names = CITIES_NAMES[first_letter]

        if city_name in names:
            return True

        else:
            if city_name in ALT_NAMES:
                city_name = ALT_NAMES[city_name]

                if city_name in names:
                    return True

    return False


def choose_city(first_letter: str) -> str:
    """Возвращает случайный город из CITIES_NAMES и удаляет его отттуда. Возвращает None при неправильной первой букве,
     False при невозможности выбора"""

    if first_letter in CITIES_NAMES:
        if CITIES_NAMES[first_letter]:
            return CITIES_NAMES[first_letter].pop(randint(0, len(CITIES_NAMES[first_letter]) - 1))
        else:
            return False
    else:
        return None
