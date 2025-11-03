from django.shortcuts import render
import json
from .tsp_solver import solve_tsp_aco
from .tsp_db import save_calculation, get_all_calculations

# Функция представления для решения задачи коммивояжера
def tsp(request):
    if request.method == 'POST':
        try:
            print("=" * 50)
            print("POST запрос получен!")
            print("POST данные:", dict(request.POST))

            # Получаем данные из формы
            vertices_json = request.POST.get('vertices', '[]')
            print(f"Получены вершины JSON: {vertices_json}")
            # Проверка на пустые данные вершин
            if not vertices_json or vertices_json == '[]':
                print("ОШИБКА: vertices пустые!")
                error_result = {
                    'error': 'Не получены данные вершин',
                    'optimal_path': [],
                    'distance': 0,
                    'execution_time': 0
                }
                return render(request, 'main/tsp.html', {'result': error_result})
            # Парсинг JSON данных вершин
            vertices_data = json.loads(vertices_json)
            print(f"Распарсено вершин: {len(vertices_data)}")

            # Преобразуем координаты в нужный формат
            points = [(v['x'], v['y']) for v in vertices_data]
            print(f"Точки: {points}")

            # Получаем параметры алгоритма
            ant_count = int(request.POST.get('ant_count', 10))
            iterations = int(request.POST.get('iterations', 100))
            alpha = float(request.POST.get('alpha', 1.0))
            beta = float(request.POST.get('beta', 2.0))
            evaporation = float(request.POST.get('evaporation', 0.5))
            q = float(request.POST.get('q', 100))

            print(f"Параметры: {ant_count} муравьев, {iterations} итераций")

            # Проверяем алгоритм
            print("Вызываем solve_tsp_aco...")
            result = solve_tsp_aco(
                points,
                ant_count,
                iterations,
                alpha,
                beta,
                evaporation,
                q
            )

            print(f"Алгоритм выполнен успешно!")
            print(f"Результат: {result}")

            # Сохраняем в БД
            parameters = {
                'ant_count': ant_count,
                'iterations': iterations,
                'alpha': alpha,
                'beta': beta,
                'evaporation': evaporation,
                'q': q
            }

            print("Сохраняем в БД...")
            calculation_id = save_calculation(
                vertices=points,
                optimal_path=result['optimal_path'],
                distance=result['distance'],
                execution_time=result['execution_time'],
                parameters=parameters
            )

            print(f"Сохранено в БД с ID: {calculation_id}")
            # Добавляем ID расчета и вершины в результат
            result['calculation_id'] = calculation_id
            result['vertices'] = points

            print("Рендерим шаблон с результатом...")
            return render(request, 'main/tsp.html', {'result': result})

        except Exception as e:
            print(f"ОШИБКА: {str(e)}")
            import traceback
            print(traceback.format_exc())

            error_result = {
                'error': str(e),
                'optimal_path': [],
                'distance': 0,
                'execution_time': 0
            }
            return render(request, 'main/tsp.html', {'result': error_result})
    else:
        # Обработка GET запроса - отображение пустой формы
        print("GET запрос - показываем пустую форму")
        return render(request, 'main/tsp.html')


# Функция представления для отображения истории расчетов
def history(request):
    calculations = get_all_calculations()
    return render(request, 'main/history.html', {'calculations': calculations})

# Функция представления для главной страницы
def index(request):
    return render(request, 'main/index.html')

# Функция представления для страницы алгоритма TSP
def tsp_algorythm(request):
    return render(request, 'main/tsp.html')