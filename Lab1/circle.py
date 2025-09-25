#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Есть значение радиуса круга
# import math

radius = 42
S = 0
# Выведите на консоль значение прощади этого круга с точностю до 4-х знаков после запятой
# подсказки:
#       формулу можно подсмотреть в интернете,
#       пи возьмите равным 3.1415926
#       точность указывается в функции round()
# TODO здесь ваш код
def circle_area(radius):
    """Расчёт площади круга"""
    S = round(3.1415926 * (radius**2), 4)
    return S

# Далее, пусть есть координаты точки
point_1 = (23, 34)
# где 23 - координата х, 34 - координата у

# Если точка point лежит внутри того самого круга [центр в начале координат (0, 0), radius = 42],
# то выведите на консоль True, Или False, если точка лежит вовне круга.
# подсказки:
#       нужно определить расстояние от этой точки до начала координат (0, 0)
#       формула так же есть в интернете d = √((x2 - x1)^2 + (y2 - y1)^2)
#       квадратный корень - это возведение в степень 0.5
#       операции сравнения дают булевы константы True и False
# TODO здесь ваш код
def check_point(point, radius):
    """Проверка точки внутри круга"""
    coordinates = {'point1': (23, 34)}
    result = True
    c1 = coordinates['point1'][0]
    c2 = coordinates['point1'][1]
    dist = round((c1 - 0)**2 + (c2 - 0)**2) ** 0.5
    if dist < radius:
        result1 = True
    else:
        result1 = False
    return result1


# Аналогично для другой точки
point_2 = (30, 30)
# Если точка point_2 лежит внутри круга (radius = 42), то выведите на консоль True,
# Или False, если точка лежит вовне круга.
# TODO здесь ваш код
def check_point2(point2, radius):
    coordinates = {'point2': (30, 30)}
    result = True
    c3 = coordinates['point2'][0]
    c4 = coordinates['point2'][1]
    dist = round((c3 - 0)**2 + (c4 - 0)**2) ** 0.5
    if dist < radius:
        result2 = True
    else:
        result2 = False
    return result2


def demo():
    area = circle_area(radius)
    is_inside_1 = check_point(point_1, radius)
    is_inside_2 = check_point2(point_2, radius)

    print(f"Площадь круга: {round(area, 4)}")
    print(f"Точка {point_1} внутри круга: {is_inside_1}")
    print(f"Точка {point_2} внутри круга: {is_inside_2}")


# Пример вывода на консоль:
# 77777.7777
# False
# False


