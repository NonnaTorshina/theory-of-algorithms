from distance import demo as distance_demo
from circle import demo as circle_demo
from operations import demo as operations_demo
from favorite_movies import demo as favorite_movies_demo
from my_family import demo as my_family_demo
from zoo import demo as zoo_demo
from songs_list import demo as songs_list_demo
from secret import demo as secret_demo
from garden import demo as garden_demo
from shopping import demo as shopping_demo
from store import demo as store_demo


def main():
    print("---------Лабораторная работа номер 1------------")

    modules = [
        (" 1. Distance ", distance_demo),
        (" 2. Circle ", circle_demo),
        (" 3. Operations  ", operations_demo),
        (" 4. Favourite movies ", favorite_movies_demo),
        (" 5. My family ", my_family_demo),
        (" 6. Zoo ", zoo_demo),
        (" 7. Songs list", songs_list_demo),
        (" 8. Secret ", secret_demo),
        (" 9. Garden ", garden_demo),
        (" 10. Shopping ", shopping_demo),
        (" 11. Store ", store_demo)

    ]
    for title, demo_func in modules:
        print(title)
        print("-" * 40)
        demo_func()
        print()

if __name__ == "__main__":
    main()
