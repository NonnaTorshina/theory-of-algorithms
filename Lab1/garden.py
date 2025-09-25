#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def flowers():
    # в саду сорвали цветы
    garden = ('ромашка', 'роза', 'одуванчик', 'ромашка', 'гладиолус', 'подсолнух', 'роза', )
    # на лугу сорвали цветы
    meadow = ('клевер', 'одуванчик', 'ромашка', 'клевер', 'мак', 'одуванчик', 'ромашка', )
    # создайте множество цветов, произрастающих в саду и на лугу
    # garden_set =
    # meadow_set =
    # TODO здесь ваш код
    garden_set = set(garden)
    meadow_set = set(meadow)
    print("Множество цветов в саду:", garden_set)
    print("Множество цветов на лугу:", meadow_set)
    # выведите на консоль все виды цветов
    # TODO здесь ваш код
    all_flowers = garden_set | meadow_set
    # выведите на консоль те, которые растут и там и там
    # TODO здесь ваш код
    common_flowers = garden_set & meadow_set
    # выведите на консоль те, которые растут в саду, но не растут на лугу
    # TODO здесь ваш код
    only_garden = garden_set - meadow_set
    # выведите на консоль те, которые растут на лугу, но не растут в саду
    # TODO здесь ваш код
    only_meadow = meadow_set - garden_set
    return garden_set, meadow_set, all_flowers, common_flowers, only_garden, only_meadow

def demo():
    garden_set, meadow_set, all_flowers, common_flowers, only_garden, only_meadow = flowers()
    print("Все виды цветов: ", all_flowers)
    print("Цветы, которые растут и в саду и на лугу: ", common_flowers)
    print("Цветы, которые растут в саду, но не растут на лугу:", only_garden)
    print("Цветы, которые растут на лугу, но не растут в саду:", only_meadow)

