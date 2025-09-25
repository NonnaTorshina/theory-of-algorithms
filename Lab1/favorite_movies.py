#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Есть строка с перечислением фильмов
def extract_movies():
    my_favorite_movies = 'Терминатор, Пятый элемент, Аватар, Чужие, Назад в будущее'

# Выведите на консоль с помощью индексации строки, последовательно:
#   первый фильм
#   последний
#   второй
#   второй с конца

# Запятая не должна выводиться.  Переопределять my_favorite_movies нельзя
# Использовать .split() или .find()или другие методы строки нельзя - пользуйтесь только срезами,
# как указано в задании!

# TODO здесь ваш код
    first_film = my_favorite_movies[0:10]
    last_film = my_favorite_movies[42:57]
    second_film = my_favorite_movies[12:25]
    second_film_end = my_favorite_movies[35:40]

    return first_film, last_film, second_film, second_film_end

def demo():
    first, last, second, second_end = extract_movies()
    print("Извлечение фильмов из строки:")
    print("Первый фильм:", first)
    print("Последний фильм:", last)
    print("Второй фильм:", second)
    print("Второй фильм с конца:", second_end)

