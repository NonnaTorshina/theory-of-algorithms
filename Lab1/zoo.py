#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# есть список животных в зоопарке
def manage_zoo():
    zoo = ['lion', 'kangaroo', 'elephant', 'monkey' ]

# посадите медведя (bear) между львом и кенгуру
#  и выведите список на консоль
# TODO здесь ваш код
    zoo.insert(1, 'bear')
# добавьте птиц из списка birds в последние клетки зоопарка
    birds = ['rooster', 'ostrich', 'lark', ]
#  и выведите список на консоль
# TODO здесь ваш код
    zoo.extend(birds)
# уберите слона
#  и выведите список на консоль
# TODO здесь ваш код
    zoo.remove('elephant')
# выведите на консоль в какой клетке сидит лев (lion) и жаворонок (lark).
# Номера при выводе должны быть понятны простому человеку, не программисту.
# TODO здесь ваш код
    lion_c = zoo.index('lion') + 1
    lark_c = zoo.index('lark') + 1

    return zoo, lion_c, lark_c

def demo():
    zoo, lion_c, lark_c = manage_zoo()

    print(f"Лев сидит в {lion_c}-й клетке")
    print(f"Жаворонок сидит в {lark_c}-й клетке")

