from functools import wraps

def is_hashable(obj):
    #проверка, является ли тип данных хэшируемым
    try:
        hash(obj) #если тип хэшируемый (можно вычислить хэш)
        return True #возвращаем тру
    except TypeError:#если вызывается ошибка то фолс 
        return False

def make_hashable(obj):
    #рекурсивно преобразовываем в хэшируемый тип
    if isinstance(obj, list):
        return tuple(make_hashable(item) for item in obj)  #списки в кортежи
    elif isinstance(obj, dict):
        return tuple((key, make_hashable(value)) for key, value in sorted(obj.items()))  #словари в кортежи
    elif not is_hashable(obj):
        return str(obj)  #остальные в строки
   
    return obj

def make_cache(max_keys: int):
    #кэширующий декоратор результатов функции
    def decorator(func):
        cache = {} #кэш - словарь с парами ключ-значение

        @wraps(func)
        def wrapper(*args, **kwargs):
            #преобразовываем аргументы функции
            hashable_args = tuple(make_hashable(arg) for arg in args)
            hashable_kwargs = tuple((key, make_hashable(value)) for key, value in sorted(kwargs.items()))
            #ключ словаря - преобразованные аргументы функции
            key = (hashable_args, hashable_kwargs)

            #инициализация словаря для текущей функции
            if func not in cache:
                cache[func] = {}

            #проверяем наличие результата функции в кэше
            if key in cache[func]:
                return cache[func][key]

            #если результата в кэше нет, вызываем функцию и сохраняем результат
            result = func(*args, **kwargs)
            cache[func][key] = result

            #если количество закэшируемых значений для текущей функции
            #больше заданной глубины
            if len(cache[func]) > max_keys:
                #то удаляем самый старый элемент
                #oldest_key = next(iter(cache[func]))
                oldest_key = list(cache[func])[0]

                del cache[func][oldest_key]

            return result

        return wrapper
    return decorator

# Пример использования
@make_cache(max_keys=2) #глубина кэширования = 2
def multiply_matrix(matrix_a: list, matrix_b: list, num: int) -> list:
    #умножение двух матриц
    size = len(matrix_a)
    result = [[0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    print(f"Matrix multiplication number {num}")
    return result


def create_matrix(size: int) -> list:
    
    matrix = []

    print(f"Filling a matrix of size {size} x {size} with numbers:")

    for i in range(size):
        row = list(map(int, input(f"Enter the values for row {i+1} separated by spaces: ").split()))
        matrix.append(row)

    return matrix

@make_cache(max_keys=2)  #глубина кэширования = 2
def sum_of_numbers(x, y):
    print(f"Executing a function with arguments {x}, {y}")
    return x + y

#Тестирование:
def main():
    print(sum_of_numbers(1, 2))  #функция была выполнена, результат кэширован
    print(sum_of_numbers(1, 2))  #функция не была выполнена, результат взят из кэша
    print(sum_of_numbers(2, 3))  #функция была выполнена, результат кэширован
    print(sum_of_numbers(3, 4))  #функция была выполнена, результат кэширован (на этом этапе 1 кэшированный результат очистился, т.к глубина = 2)
    print(sum_of_numbers(1, 2))  #функция была выполнена, результат кэширован (этот результат очистили как самый старый на предыдущем этапе)

    size = int(input("Enter the size of the matrix: "))

    print("Matrix 1:")
    matrix1 = create_matrix(size)

    print("Matrix 2:")
    matrix2 = create_matrix(size)

    res = multiply_matrix(matrix1, matrix2, 1) #функция была выполнена, результат кэширован
    #print("Matrix multiplication result:")
    for row in res:
        print(" ".join(map(str, row)))

    print()

    res = multiply_matrix(matrix2, matrix1, 2) #функция была выполнена, результат кэширован
    #print("Matrix multiplication result:")
    for row in res:
        print(" ".join(map(str, row)))

    print()

    res = multiply_matrix(matrix2, matrix1, 3)  #функция не была выполнена, результат взят из кэша
    #print("Matrix multiplication result:")
    for row in res:
        print(" ".join(map(str, row)))

    print()

    res = multiply_matrix(matrix1, matrix1, 4) #функция была выполнена, результат кэширован (первый стерли)
    #print("Matrix multiplication result:")
    for row in res:
        print(" ".join(map(str, row)))

    print()

    res = multiply_matrix(matrix1, matrix2, 1) #функция была выполнена, результат кэширован (т.к этот результат стерли)
    #print("Matrix multiplication result:")
    for row in res:
        print(" ".join(map(str, row)))

    print()

if __name__ == "__main__":
    main()
