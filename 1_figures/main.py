class Shape:
    """Геометрические фигуры"""
    def __init__(self, x=0, y=0, name='геометрическая фигура'):
        self._x = x
        self._y = y
        self.name = name

    def __repr__(self):
        return f"{self.name} по координатам ({self._x}, {self._y})"


class Rectangle(Shape):
    """Прямоугольники"""
    def __init__(self, width, height, x=0, y=0):
        super().__init__(x, y, name='прямоугольник')
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def __repr__(self):
        base_repr = super().__repr__()
        return (f"{base_repr}, со сторонами {self.width} и {self.height},"
                f" с площадью {self.area()} и периметром {self.perimeter()}")


class Square(Rectangle):
    """Квадраты"""
    def __init__(self, side, x=0, y=0):
        super().__init__(side, side, x, y)
        self.name = 'квадрат'

    @property
    def width(self):
        return super().width

    @width.setter
    def width(self, value):
        self._set_side(value)

    @property
    def height(self):
        return super().height

    @height.setter
    def height(self, value):
        self._set_side(value)

    def _set_side(self, value):
        super(Square, type(self)).width.fset(self, value)
        super(Square, type(self)).height.fset(self, value)

    def __repr__(self):
        assert self.width == self.height
        return f"<square side={self.width}> по координатам ({self._x}, {self._y})"
