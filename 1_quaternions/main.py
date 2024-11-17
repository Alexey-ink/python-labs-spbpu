import math

class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Quaternion({self.w}, {self.x}, {self.y}, {self.z})"

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
