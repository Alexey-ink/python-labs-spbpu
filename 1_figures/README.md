# Изменения в реализации классов `Rectangle` и `Square`

## Что было изменено

### Свойства `width` и `height`
- В классе `Square` сеттеры для `width` и `height` переписаны таким образом, чтобы они вызывали приватный метод `_set_side`. Этот метод устанавливает обе стороны квадрата одновременно.
- Использование `super(Square, type(self))` позволяет обращаться непосредственно к сеттерам в родительском классе `Rectangle`, не нарушая принцип наследования.

### Приватный метод `_set_side`
- Метод `_set_side` синхронизирует ширину и высоту квадрата, гарантируя, что они всегда остаются равными.

## Почему это теперь корректно
- Класс `Square` по-прежнему наследует все свойства и методы класса `Rectangle`.
- Любое изменение ширины или высоты квадрата приводит к корректному изменению обеих сторон, что гарантирует сохранение квадратной формы и делает его поведение совместимым с `Rectangle`.
- Принцип подстановки Барбары Лисков теперь соблюден: класс `Square` можно использовать в любом контексте, где ожидается `Rectangle`, и он будет вести себя корректно.
