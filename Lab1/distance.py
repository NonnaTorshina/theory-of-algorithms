#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Есть словарь координат городов
def calculate_distances():
    """Расчёт расстояний между городами"""
    sites = {
        'Moscow': (550, 370),
        'London': (510, 510),
        'Paris': (480, 480),
    }

# Составим словарь словарей расстояний между ними
# расстояние на координатной сетке - ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    distances = { }

    # TODO здесь заполнение словаря
    for city1, c1 in sites.items():  # точки отправления
        distances[city1] = {}
        for city2, c2 in sites.items(): # пункт прибытия
            if city1 != city2:
                distance = ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5
                distances[city1][city2] = round(distance, 3)
    return(distances)

def demo():
    distances = calculate_distances()
    print("Расстояния между городами:")
    for city1 in distances:
        print(f"от города {city1}:")
        for city2, dist in distances[city1].items():
            print(f"до {city2}: {dist} ")
