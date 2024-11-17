import math

import sys
import io
# вывод в кодировке UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Quaternion({self.w}, {self.x}, {self.y}, {self.z})"
    
    def __eq__(self, other):
        if isinstance(other, Quaternion):
            return (self.w == other.w and
                    self.x == other.x and
                    self.y == other.y and
                    self.z == other.z)
        return False

    # Модуль кватерниона
    def magnitude(self):
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    # Нормализация кватерниона
    def normalize(self):
        mag = self.magnitude()
        return Quaternion(self.w / mag, self.x / mag, self.y / mag, self.z / mag)

    # Сопряжение кватерниона
    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    # Сложение
    def __add__(self, other):
        return Quaternion(
            self.w + other.w,
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    # Вычитание
    def __sub__(self, other):
        return Quaternion(
            self.w - other.w,
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    # Умножение
    def __mul__(self, other):
        if isinstance(other, Quaternion):
            w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
            y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
            z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
            return Quaternion(w, x, y, z)
        elif isinstance(other, (int, float)):  # Умножение на скаляр
            return Quaternion(self.w * other, self.x * other, self.y * other, self.z * other)

    # Деление на скаляр
    def __truediv__(self, scalar):
        return Quaternion(self.w / scalar, self.x / scalar, self.y / scalar, self.z / scalar)

    # Поворот вектора через кватернион
    def rotate_vector(self, vector):
        vector_quat = Quaternion(0, *vector)
        rotated = self * vector_quat * self.conjugate()
        return (rotated.x, rotated.y, rotated.z)

    # Создание кватерниона поворота
    @staticmethod
    def from_axis_angle(axis, angle):
        half_angle = angle / 2
        sin_half_angle = math.sin(half_angle)
        return Quaternion(
            math.cos(half_angle),
            axis[0] * sin_half_angle,
            axis[1] * sin_half_angle,
            axis[2] * sin_half_angle
        )

def test_quaternion_operations():

    q1 = Quaternion(1, 2, 3, 4)
    q2 = Quaternion(5, 6, 7, 8)

    # Сложение
    print(f"Тест сложения: {q1} + {q2}")
    q_add = q1 + q2
    print(f"Ожидается: Quaternion(6, 8, 10, 12)")
    print(f"Результат: {q_add}")
    assert q_add == Quaternion(6, 8, 10, 12), f"Не удалось: {q_add}"
    print("Тест сложения пройден.\n")

    # Вычитание
    print(f"Тест вычитания: {q1} - {q2}")
    q_sub = q1 - q2
    print(f"Ожидается: Quaternion(-4, -4, -4, -4)")
    print(f"Результат: {q_sub}")
    assert q_sub == Quaternion(-4, -4, -4, -4), f"Не удалось: {q_sub}"
    print("Тест вычитания пройден.\n")

    # Умножение
    print(f"Тест умножения: {q1} * {q2}")
    q_mul = q1 * q2
    print(f"Ожидается: Quaternion(-60, 12, 30, 24)")
    print(f"Результат: {q_mul}")
    assert q_mul == Quaternion(-60, 12, 30, 24), f"Не удалось: {q_mul}"
    print("Тест умножения пройден.\n")

    # Умножение на скаляр
    print(f"Тест умножения на скаляр: {q1} * 2")
    q_scalar_mul = q1 * 2
    print(f"Ожидается: Quaternion(2, 4, 6, 8)")
    print(f"Результат: {q_scalar_mul}")
    assert q_scalar_mul == Quaternion(2, 4, 6, 8), f"Не удалось: {q_scalar_mul}"
    print("Тест умножения на скаляр пройден.\n")

    # Деление на скаляр
    print(f"Тест деления на скаляр: {q1} / 2")
    q_scalar_div = q1 / 2
    print(f"Ожидается: Quaternion(0.5, 1, 1.5, 2)")
    print(f"Результат: {q_scalar_div}")
    assert q_scalar_div == Quaternion(0.5, 1, 1.5, 2), f"Не удалось: {q_scalar_div}"
    print("Тест деления на скаляр пройден.\n")

    # Нормализация
    print(f"Тест нормализации: {q1}")
    q_norm = q1.normalize()
    print(f"Ожидается: Quaternion с магниутой 1 (фактически: {q_norm.magnitude()})")
    print(f"Результат: {q_norm}")
    assert math.isclose(q_norm.magnitude(), 1), f"Не удалось: {q_norm}"
    print("Тест нормализации пройден.\n")

    # Сопряжение
    print(f"Тест сопряжения: {q1}")
    q_conjugate = q1.conjugate()
    print(f"Ожидается: Quaternion(1, -2, -3, -4)")
    print(f"Результат: {q_conjugate}")
    assert q_conjugate == Quaternion(1, -2, -3, -4), f"Не удалось: {q_conjugate}"
    print("Тест сопряжения пройден.\n")

    print("Все тесты операций пройдены.")

def test_quaternion_rotation():
    # Поворот вектора
    axis = (0, 0, 1)
    angle = math.radians(90)
    rotation_quat = Quaternion.from_axis_angle(axis, angle)
    print(f"Тест поворота: поворачиваем вектор (1, 0, 0) на 90 градусов вокруг оси {axis}")
    print(f"Кватернион поворота: {rotation_quat}")

    # Вектор для поворота
    vector = (1, 0, 0)

    # Ожидаемый результат: поворот на 90 градусов вокруг оси Z
    rotated_vector = rotation_quat.rotate_vector(vector)
    print(f"Ожидается: (0, 1, 0)")
    print(f"Результат: {rotated_vector}")

    # Вектор (1, 0, 0) после поворота на 90 градусов должен стать (0, 1, 0)
    assert math.isclose(rotated_vector[0], 0) and math.isclose(rotated_vector[1], 1), f"Не удалось: {rotated_vector}"
    print("Тест поворота кватернионом пройден.\n")

def main():
    print("Запуск тестов для операций с кватернионами и поворота...\n")
    test_quaternion_operations()
    test_quaternion_rotation()
    print("Все тесты пройдены успешно.")

if __name__ == "__main__":
    main()