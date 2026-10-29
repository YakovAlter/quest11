import pytest

class Order:
    def __init__(self, id, items):
        self.id = id
        self.items = items

    def total(self):
        return sum(item['price'] * item['quantity'] for item in self.items)

    def most_expensive(self):
        return max(self.items, key=lambda x: x['price'])

    def apply_discount(self, percent):
        if not 0 <= percent <= 100:
            raise ValueError("Invalid discount")
        for item in self.items:
            item['price'] -= item['price'] * (percent / 100)

    def __repr__(self):
        return f"<Order {self.id}: {len(self.items)} items>"

# --- ФІКСТУРИ ---

@pytest.fixture
def empty_order():
    return Order(1, [])

@pytest.fixture
def normal_order():
    return Order(2, [
        {'name': 'Apple', 'price': 10.0, 'quantity': 2},
        {'name': 'Banana', 'price': 5.5, 'quantity': 1},
        {'name': 'Cherry', 'price': 20.0, 'quantity': 3}
    ])

# --- ТЕСТИ ---

def test_total_empty(empty_order):
    assert empty_order.total() == 0

def test_total_normal(normal_order):
    # 10*2 + 5.5*1 + 20*3 = 85.5
    assert normal_order.total() == pytest.approx(85.5)

def test_most_expensive_empty(empty_order):
    # Вбудована функція max() на порожньому списку викидає ValueError
    with pytest.raises(ValueError):
        empty_order.most_expensive()

def test_most_expensive_normal(normal_order):
    item = normal_order.most_expensive()
    assert item['name'] == 'Cherry'

@pytest.mark.parametrize("percent, expected_prices", [
    (0, [10.0, 5.5, 20.0]),      # Нижня межа (валідна)
    (10, [9.0, 4.95, 18.0]),     # Звичайний випадок
    (100, [0.0, 0.0, 0.0])       # Верхня межа (валідна)
])
def test_apply_discount_valid_changes_all_items(normal_order, percent, expected_prices):
    normal_order.apply_discount(percent)
    prices = [item['price'] for item in normal_order.items]
    # Завжди використовуємо approx для порівняння float
    assert prices == pytest.approx(expected_prices)

@pytest.mark.parametrize("percent", [
    -5,          # Невалідний від'ємний
    -0.01,       # Крок за нижньою межею
    100.01,      # Крок за верхньою межею
    150          # Невалідний завеликий
])
def test_apply_discount_invalid_raises_error(normal_order, percent):
    with pytest.raises(ValueError, match="Invalid discount"):
        normal_order.apply_discount(percent)
    
    # Перевіряємо, що у разі помилки стан не змінився
    prices = [item['price'] for item in normal_order.items]
    assert prices == pytest.approx([10.0, 5.5, 20.0])

def test_repr(normal_order, empty_order):
    assert repr(normal_order) == "<Order 2: 3 items>"
    assert repr(empty_order) == "<Order 1: 0 items>"