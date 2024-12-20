## Класс для работы с кватернионами

Этот проект реализует класс `Quaternion`, предназначенный для работы с кватернионами. Класс включает базовые арифметические операции с кватернионами, а также функциональность для поворота векторов в 3D-пространстве.

---

### Описание методов:

- **`__init__(self, w, x, y, z)`** - Инициализирует кватернион с компонентами \(w, x, y, z\).

- **`__repr__(self)`** - Возвращает строковое представление кватерниона в формате `Quaternion(w, x, y, z)`.

- **`magnitude(self)`** - Вычисляет и возвращает модуль (длину) кватерниона.

- **`normalize(self)`** - Нормализует кватернион, делая его модуль равным 1.

- **`conjugate(self)`** - Возвращает сопряжённый кватернион (меняются знаки векторных частей \(x, y, z\)).

- **`__add__(self, other)`** - Выполняет сложение двух кватернионов.

- **`__sub__(self, other)`** - Выполняет вычитание двух кватернионов.

- **`__mul__(self, other)`** - Выполняет умножение двух кватернионов или умножение кватерниона на скаляр.

- **`__truediv__(self, scalar)`** - Делит кватернион на скаляр.

- **`rotate_vector(self, vector)`** - Поворачивает вектор с использованием кватерниона. Вектор должен быть задан как кортеж из трех элементов \( (x, y, z) \).

- **`from_axis_angle(axis, angle)`** - Создаёт кватернион для поворота вокруг оси `axis` на угол `angle` (в радианах).