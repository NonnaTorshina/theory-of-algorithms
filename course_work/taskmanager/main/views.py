from django.shortcuts import render
from django.http import HttpResponse
import json
from .tsp_solver import solve_tsp_aco


def tsp_algorithm(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            vertices_json = request.POST.get('vertices', '[]')
            vertices_data = json.loads(vertices_json)

            # Преобразуем координаты в нужный формат
            points = [(v['x'], v['y']) for v in vertices_data]

            # Получаем параметры алгоритма
            ant_count = int(request.POST.get('ant_count', 10))
            iterations = int(request.POST.get('iterations', 100))
            alpha = float(request.POST.get('alpha', 1.0))
            beta = float(request.POST.get('beta', 2.0))
            evaporation = float(request.POST.get('evaporation', 0.5))
            q = float(request.POST.get('q', 100))

            # Вызываем алгоритм
            result = solve_tsp_aco(
                points,
                ant_count,
                iterations,
                alpha,
                beta,
                evaporation,
                q
            )

            return render(request, 'main/tsp.html', {'result': result})

        except Exception as e:
            # Обработка ошибок
            error_result = {
                'error': str(e),
                'optimal_path': [],
                'distance': 0,
                'execution_time': 0
            }
            return render(request, 'main/tsp.html', {'result': error_result})


def index(request):
    return render(request, 'main/index.html')

def tsp_algorythm(request):
    return render(request, 'main/tsp.html')

def history(request):
    return render(request, 'main/history.html')


