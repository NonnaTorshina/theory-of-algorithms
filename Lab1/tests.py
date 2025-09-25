import pytest

from circle import circle_area, check_point, check_point2
from operations import operation_numbers
from favorite_movies import extract_movies
from my_family import family
from zoo import manage_zoo
from songs_list import songs_time
from secret import decrypt
from garden import flowers
from shopping import create_sweets
from store import store_totals
from distance import calculate_distances

# Тесты для circle.py
def test_circle_area():
    expected_area = round(3.1415926 * (42**2), 4)
    assert circle_area(42) == expected_area

def test_check_point_inside():
    assert check_point((23, 34), 42) == True

def test_check_point_outside():
    assert check_point2((30, 30), 42) == False

# Тесты для operations.py
def test_operation_numbers():
    assert operation_numbers() == 25

# Тесты для favorite_movies.py
def test_extract_movies():
    first, last, second, second_end = extract_movies()
    assert first == 'Терминатор'
    assert last == 'Назад в будущее'
    assert second == 'Пятый элемент'
    assert second_end == 'Чужие'

# Тесты для my_family.py
def test_family():
    my_family, my_family_height, height = family()
    assert len(my_family) == 5
    assert height == 170 + 160 + 170 + 150 + 160

# Тесты для zoo.py
def test_manage_zoo():
    zoo, lion_c, lark_c = manage_zoo()
    assert 'bear' in zoo
    assert 'elephant' not in zoo
    assert lion_c == 1
    assert lark_c == 7  # После добавления и удаления

# Тесты для songs_list.py
def test_songs_time():
    minutes, minutes2 = songs_time()
    # Проверим приблизительно, так как значения могут меняться
    assert minutes > 10
    assert minutes2 > 10

# Тесты для secret.py
def test_decrypt():
    message = decrypt()
    expected = "в бане веник дороже денег"
    assert message == expected

# Тесты для garden.py
def test_flowers():
    garden_set, meadow_set, all_flowers, common_flowers, only_garden, only_meadow = flowers()
    assert 'ромашка' in common_flowers
    assert 'роза' in only_garden
    assert 'клевер' in only_meadow

# Тесты для shopping.py
def test_create_sweets():
    sweets = create_sweets()
    assert 'печенье' in sweets
    assert len(sweets['печенье']) == 2

# Тесты для store.py
def test_store_totals():
    Table_quantity, Sofa_quantity, Chair_quantity, Table_cost, Sofa_cost, Chair_cost = store_totals()
    assert Table_quantity == 22 + 32
    assert Chair_quantity == 50 + 12 + 43

# Тесты для distance.py
def test_calculate_distances():
    distances = calculate_distances()
    assert 'Moscow' in distances
    assert 'London' in distances['Moscow']
    assert isinstance(distances['Moscow']['London'], float)