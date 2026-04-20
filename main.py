from app.cities_service import (
    group_cities_by_letters,
    map_names_to_alt,
    map_names_to_cords,
    check_city,
    choose_city,
    remove_city,
)
from app.responses import Phrases
from app.commands import Commands

from flask import Flask, request, jsonify
import logging
from random import choice

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route("/post", methods=["POST"])
def main():
    logging.info(f"Request: {request.json!r}")
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {"end_session": False, "buttons": []},
    }

    handle_dialog(request.json, response)

    logging.info(f"Response:  {response!r}")

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req["session"]["user_id"]
    if req["session"]["new"]:
        sessionStorage[user_id] = {
            "cities_names": group_cities_by_letters(),
            "alt_names": map_names_to_alt(),
            "cities_cords": map_names_to_cords(),
            "used_cities": [],
            "last_letter": None,
        }

        session = sessionStorage[user_id]
        message, alice_city = first_turn(session)

        res["response"]["text"] = choice(Phrases.greeting).format(alice_city)
        make_yandex_maps_suggest(res, alice_city, session)
        make_suggests(res)

        return

    session = sessionStorage[user_id]
    request_text = req["request"]["original_utterance"].lower().strip()

    if request_text in Commands.rules:
        res["response"]["text"] = choice(Phrases.rules).format(
            Commands.surrender[0], Commands.show_location[0], Commands.rules[0]
        )
        return

    if request_text in Commands.show_location:
        res["response"]["text"] = choice(Phrases.send_map)
        make_suggests(res)
        return

    if request_text in Commands.surrender:
        res["response"]["text"] = choice(Phrases.win)
        res["response"]["end_session"] = True
        return

    city_name = request_text

    message, result = process_turn(city_name, session)

    if message == "city_already_used":
        res["response"]["text"] = choice(Phrases.city_already_used)
    elif message == "city_not_found":
        res["response"]["text"] = choice(Phrases.city_not_found)
    elif message == "invalid_first_letter":
        res["response"]["text"] = choice(Phrases.invalid_first_letter).format(
            session["last_letter"]
        )
    elif message == "player_win":
        res["response"]["text"] = choice(Phrases.surrender)
        res["response"]["end_session"] = True
    elif message == "OK":
        res["response"]["text"] = choice(Phrases.name_city).format(result)
        make_yandex_maps_suggest(res, result, session)

    make_suggests(res)


def process_turn(city_name: str, session: dict):
    first_letter = city_name[0]

    if city_name in session["used_cities"] or (
            city_name in session["alt_names"]
            and session["alt_names"][city_name] in session["used_cities"]
    ):
        return "city_already_used", None

    if not check_city(city_name, session["cities_names"], session["alt_names"]):
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

    return "OK", alice_city.capitalize()


def first_turn(session: dict):
    alice_first_letter = choice(list(session["cities_names"].keys()))
    alice_city = choose_city(alice_first_letter, session["cities_names"])

    session["last_letter"] = get_last_letter(alice_city)
    session["used_cities"].append(alice_city)

    return "OK", alice_city.capitalize()


def get_last_letter(city_name: str) -> str:
    normalized = city_name.lower()

    for i in range(len(normalized) - 1, -1, -1):
        if normalized[i] not in ["ь", "ъ", "ы"]:
            return normalized[i]

    return None


def make_suggests(res):
    buttons = [
        {
            "title": Commands.rules[0],
            "hide": True
        },
        {
            "title": Commands.surrender[0],
            "hide": True
        },
    ]

    res["response"]["buttons"].extend(buttons)


def make_yandex_maps_suggest(res, city_name: str, session):
    button = {
            "title": Commands.show_location[0],
            "url": get_yandex_maps_link(city_name, session),
            "hide": True
        }

    res["response"]["buttons"].append(button)


def get_yandex_maps_link(city_name: str, session):
    lon, lat = session["cities_cords"][city_name.lower()]["lon"], session["cities_cords"][city_name.lower()]["lat"]

    return f"https://yandex.ru/maps/?ll={lon},{lat}&z=6.8&pt={lon},{lat},pm2rdm"


if __name__ == "__main__":
    app.run()
