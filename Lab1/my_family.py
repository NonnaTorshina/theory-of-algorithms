#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Создайте списки:
def family():
# моя семья (минимум 3 элемента, есть еще дедушки и бабушки, если что)
    my_family = ['Я','Мама', 'Бабушка', 'Дедушка', 'Сестра']
# список списков приблизителного роста членов вашей семьи
    my_family_height = [
        [my_family[1], 170],
        [my_family[2], 160],
        [my_family[3], 170],
        [my_family[4], 150],
        [my_family[0], 160]
    ]


    height = my_family_height[0][1] + my_family_height[1][1] + my_family_height[2][1] + my_family_height[3][1] + \
         my_family_height[4][1]

    return my_family, my_family_height, height
# Выведите на консоль рост отца в формате
#   Рост отца - ХХ см
# Выведите на консоль общий рост вашей семьи как сумму ростов всех членов
#   Общий рост моей семьи - ХХ см

def demo():
    my_family, my_family_height, height = family()

    print("Рост мамы -", my_family_height[0][1], "см")
    print("Общий рост моей семьи -", height, "см")

