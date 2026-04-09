import json, csv

with open("russia-cities.json", encoding="utf-8") as file:
    data = json.load(file)

with open("cities.csv", encoding="utf8", mode="w") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "name_alt", "lat", "lon"])

    used_names = []
    for city in data:
        name = city["name"]
        name_alt = city["name_alt"]
        lat = city["coords"]["lat"]
        lon = city["coords"]["lon"]
        if name not in used_names:
            used_names.append(name)
            writer.writerow([name, name_alt, lat, lon])