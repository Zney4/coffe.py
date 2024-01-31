import json
import requests
import folium
from geopy import distance
import os
from dotenv import load_dotenv
import logging
from flask import Flask


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lat, lon


def cofee_coord(user_coords):
    all_coffe = []
    with open("coffee.json", "r", encoding="CP1251 ") as my_file:
        file_contents = json.loads(my_file.read())
        logging.info(type(file_contents))

    for coffe in file_contents:
        coffe_cords = coffe["Latitude_WGS84"], coffe["Longitude_WGS84"]

        distance_coffe = distance.distance(user_coords, coffe_cords).km

        info_coffe = {
            "title": coffe["Name"],
            "distance": distance_coffe,
            "latitude": coffe["Latitude_WGS84"],
            "longitude": coffe["Longitude_WGS84"],
        }

        all_coffe.append(info_coffe)
    return all_coffe


def distanse_coffe(all_coffee):
    return all_coffee["distance"]


def do_coffe_map(sorted_coffee_user_coords_5, user_coords):
    m = folium.Map(user_coords, zoom_start=12)

    folium.Marker(
        location=(user_coords[0], user_coords[1]),
        tooltip="user_coords",
        popup="user_coords",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    for coords_metka in sorted_coffee_user_coords_5:
        folium.Marker(
            location=(coords_metka["latitude"], coords_metka["longitude"]),
            tooltip=coords_metka["title"],
            popup="Кофейня",
            icon=folium.Icon(icon="coffe"),
        ).add_to(m)
        logging.info(m)
    return m


def coffe():
    with open("map.html") as file:
        return file.read()


if __name__ == "__main__":
    load_dotenv()
    cordinati = input("Введите ваши кординаты:")
    apikey = os.environ["APIKEY"]
    user_coords = fetch_coordinates(apikey, cordinati)

    app = Flask(__name__)
    app.add_url_rule("/", "COFFE!", coffe)
    app.run("0.0.0.0")

    all_coffe = cofee_coord(user_coords)

    sorted_coffee = sorted(all_coffe, key=distanse_coffe)
    sorted_coffee_user_coords_5 = sorted_coffee[:5]

    m = do_coffe_map(sorted_coffee_user_coords_5, user_coords)
    m.save("map.html")
