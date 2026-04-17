from app.cities_service import group_cities_by_letters, map_names_to_alt, check_city, choose_city, remove_city
from app.responses import Phrases
from app.commands import Commands

# импортируем библиотеки
from flask import Flask, request, jsonify
import logging
from random import choice


# создаём приложение
# мы передаём __name__, в нём содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например, произошло внутри модуля logging,
# то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    logging.info(f'Request: {request.json!r}')

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            "cities_names": group_cities_by_letters(),
            "alt_names": map_names_to_alt(),
            "used_cities": [],
            "last_letter": None
        }
        # Заполняем текст ответа

        session = sessionStorage[user_id]
        message, alice_city = first_turn(session)

        res['response']['text'] = choice(Phrases.greeting).format(alice_city)
        return

    # Сюда дойдем только, если пользователь не новый,

    session = sessionStorage[user_id]
    city_name = res['response']['text'].strip()

    message, result = process_turn(city_name, session)

    if message == "city_already_used":
        res['response']['text'] = choice(Phrases.city_already_used)
    elif message == "city_not_found":
        res['response']['text'] = choice(Phrases.city_not_found)
    elif message == "invalid_first_letter":
        res['response']['text'] = choice(Phrases.invalid_first_letter).format(session["last_letter"])
    elif message == "player_win":
        res['response']['text'] = choice(Phrases.surrender)
    elif message == "OK":
        res['response']['text'] = choice(Phrases.name_city).format(result)


def process_turn(city_name: str, session: dict):
    first_letter = city_name[0]

    if city_name in session["used_cities"] or (
            city_name in session["alt_names"] and session["alt_names"][city_name] in session[
        "used_cities"]):
        return "city_already_used", None

    if not check_city(city_name, session["cites_names"], session["alt_names"]):
        return "city_not_found", None

    if session["last_letter"] and session["last_letter"] != first_letter:
        return "invalid_first_letter", None

    session["last_letter"] = get_last_letter(city_name)
    session["used_cities"].append(city_name)
    remove_city(city_name, session["cities_names"], session["alt_names"])

    if city_name in session["alt_names"]:
        session["used_cities"].append(session["alt_names"][city_name])

    alice_city = choose_city(session["last_letter"], session["cities_names"])

    if not alice_city:
        return "player_win", None

    session["last_letter"] = get_last_letter(alice_city)
    session["used_cities"].append(alice_city)

    return "OK", alice_city


def first_turn(session: dict):
    alice_city = choose_city(session["last_letter"], session["cities_names"])

    session["last_letter"] = get_last_letter(alice_city)
    session["used_cities"].append(alice_city)

    return "OK", alice_city


def get_last_letter(city_name: str) -> str:
    normalized = city_name.lower()

    for i in range(len(normalized) - 1, -1, -1):
        if normalized[i] not in ['ь', 'ъ', 'ы']:
            return normalized[i]

    return None



if __name__ == '__main__':
    app.run()
