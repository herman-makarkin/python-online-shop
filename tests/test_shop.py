import pytest

from src.classes import (
    Product, Customer, Cart, Order, Shop,
    DigitalProduct, DiscountedProduct,
    CreditCardProcessor, PayPalProcessor
)


# ---------------------------
# Фикстуры для тестов
# ---------------------------

@pytest.fixture
def sample_product():
    """Обычный товар."""
    return Product("Ноутбук", 50000, 10, "p001")


@pytest.fixture
def another_product():
    """Ещё один товар."""
    return Product("Смартфон", 30000, 5, "p002")


@pytest.fixture
def digital_product():
    """Цифровой товар."""
    return DigitalProduct("Электронная книга", 300, 1000, "p003", 5, "http://example.com/download")


@pytest.fixture
def discounted_product():
    """Товар со скидкой."""
    return DiscountedProduct("Книга со скидкой", 500, 20, "p004", 10)  # скидка 10%


@pytest.fixture
def sample_customer():
    """Обычный покупатель."""
    return Customer("Иван Петров", "c001", "ivan@mail.ru")


@pytest.fixture
def another_customer():
    """Другой покупатель."""
    return Customer("Мария Иванова", "c002", "maria@mail.ru")


@pytest.fixture
def cart(sample_customer):
    """Корзина для покупателя."""
    return Cart(sample_customer)


@pytest.fixture
def shop(sample_product, another_product, digital_product, discounted_product, sample_customer, another_customer):
    """Магазин, заполненный товарами и покупателями."""
    shop = Shop()
    shop.add_product(sample_product)
    shop.add_product(another_product)
    shop.add_product(digital_product)
    shop.add_product(discounted_product)
    shop.register_customer(sample_customer)
    shop.register_customer(another_customer)
    return shop


# ---------------------------
# Тесты для класса Product
# ---------------------------

class TestProduct:
    def test_creation(self, sample_product):
        assert sample_product._Product__name == "Ноутбук"
        assert sample_product._Product__price == 50000
        assert sample_product._Product__quantity == 10
        assert sample_product.product_id == "p001"

    def test_price_property(self, sample_product):
        assert sample_product.price == 50000
        sample_product.price = 45000
        assert sample_product._Product__price == 45000
        with pytest.raises(ValueError):
            sample_product.price = -1000

    def test_quantity_property(self, sample_product):
        assert sample_product.quantity == 10
        sample_product.quantity = 5
        assert sample_product._Product__quantity == 5
        with pytest.raises(ValueError):
            sample_product.quantity = -1

    def test_is_available(self, sample_product):
        assert sample_product.is_available(5) is True
        assert sample_product.is_available(10) is True
        assert sample_product.is_available(11) is False

    def test_str(self, sample_product):
        expected = "Ноутбук (p001): 50000 руб., в наличии: 10"
        assert str(sample_product) == expected


# ---------------------------
# Тесты для класса Customer
# ---------------------------

class TestCustomer:
    def test_creation(self, sample_customer):
        assert sample_customer._Customer__name == "Иван Петров"
        assert sample_customer.customer_id == "c001"
        assert sample_customer._Customer__email == "ivan@mail.ru"

    def test_email_property(self, sample_customer):
        assert sample_customer.email == "ivan@mail.ru"
        sample_customer.email = "new@mail.ru"
        assert sample_customer._Customer__email == "new@mail.ru"
        with pytest.raises(ValueError):
            sample_customer.email = "invalid-email"

    def test_str(self, sample_customer):
        assert str(sample_customer) == "Иван Петров (c001), email: ivan@mail.ru"


# ---------------------------
# Тесты для класса Cart
# ---------------------------

class TestCart:
    def test_creation(self, cart, sample_customer):
        assert cart.customer == sample_customer
        assert cart.items == {}

    def test_add_item_success(self, cart, sample_product):
        cart.add_item(sample_product, 2)
        assert cart.items["p001"] == 2

        # добавление ещё такого же товара
        cart.add_item(sample_product, 1)
        assert cart.items["p001"] == 3

    def test_add_item_insufficient_quantity(self, cart, sample_product):
        with pytest.raises(Exception) as excinfo:
            cart.add_item(sample_product, 11)
        assert "недостаточно" in str(excinfo.value).lower()
        assert "p001" not in cart.items

    def test_remove_item(self, cart, sample_product):
        cart.add_item(sample_product, 2)
        cart.remove_item("p001")
        assert "p001" not in cart.items

    def test_remove_item_not_in_cart(self, cart):
        with pytest.raises(Exception) as excinfo:
            cart.remove_item("p999")
        assert "нет в корзине" in str(excinfo.value).lower()

    def test_update_quantity(self, cart, sample_product):
        cart.add_item(sample_product, 2)
        cart.update_quantity("p001", 5)
        assert cart.items["p001"] == 5

        # обновление на количество больше, чем на складе
        with pytest.raises(Exception) as excinfo:
            cart.update_quantity("p001", 11)
        assert "недостаточно" in str(excinfo.value).lower()
        # количество не должно измениться
        assert cart.items["p001"] == 5

    def test_get_total_price(self, cart, sample_product, another_product, shop):
        cart.add_item(sample_product, 2)   # 50000 * 2 = 100000
        cart.add_item(another_product, 1)  # 30000 * 1 = 30000
        total = cart.get_total_price(shop.products)
        assert total == 130000

    def test_clear(self, cart, sample_product):
        cart.add_item(sample_product, 2)
        cart.clear()
        assert cart.items == {}

    def test_str(self, cart, sample_product):
        cart.add_item(sample_product, 2)
        expected = "Корзина покупателя Иван Петров:\n  Ноутбук: 2 шт."
        assert str(cart) == expected


# ---------------------------
# Тесты для класса Order
# ---------------------------

class TestOrder:
    def test_creation(self, sample_customer):
        items = {"p001": 2, "p002": 1}
        order = Order("o001", sample_customer, items, 130000)
        assert order.order_id == "o001"
        assert order.customer == sample_customer
        assert order.items == items
        assert order.total_price == 130000
        assert order.status == "новый"

    def test_update_status_valid(self, sample_customer):
        order = Order("o001", sample_customer, {}, 0)
        order.update_status("оплачен")
        assert order.status == "оплачен"
        order.update_status("отправлен")
        assert order.status == "отправлен"
        order.update_status("доставлен")
        assert order.status == "доставлен"

    def test_update_status_invalid(self, sample_customer):
        order = Order("o001", sample_customer, {}, 0)
        with pytest.raises(Exception) as excinfo:
            order.update_status("несуществующий")
        assert "недопустимый статус" in str(excinfo.value).lower()

    def test_update_status_transition_invalid(self, sample_customer):
        order = Order("o001", sample_customer, {}, 0)
        order.update_status("доставлен")  # сразу в доставлен
        with pytest.raises(Exception) as excinfo:
            order.update_status("оплачен")  # назад нельзя
        assert "нельзя перейти" in str(excinfo.value).lower()

    def test_str(self, sample_customer):
        order = Order("o001", sample_customer, {"p001": 2}, 100000)
        expected = "Заказ o001, покупатель Иван Петров, статус: новый, сумма: 100000 руб."
        assert str(order) == expected


# ---------------------------
# Тесты для класса Shop
# ---------------------------

class TestShop:
    def test_add_product(self, shop, sample_product):
        assert "p001" in shop.products
        assert shop.products["p001"] == sample_product

    def test_register_customer(self, shop, sample_customer):
        assert "c001" in shop.customers
        assert shop.customers["c001"] == sample_customer

    def test_get_cart_new(self, shop, sample_customer):
        cart = shop.get_cart(sample_customer)
        assert isinstance(cart, Cart)
        assert cart.customer == sample_customer
        assert cart.items == {}
        assert "c001" in shop.carts
        assert shop.carts["c001"] == cart

    def test_get_cart_existing(self, shop, sample_customer):
        cart1 = shop.get_cart(sample_customer)
        cart2 = shop.get_cart(sample_customer)
        assert cart1 is cart2  # один и тот же объект

    def test_find_products_by_name(self, shop):
        result = shop.find_products_by_name("ноут")
        assert len(result) == 1
        assert result[0]._Product__name == "Ноутбук"

        result = shop.find_products_by_name("книга")
        assert len(result) == 2  # обычная со скидкой и цифровая
        names = {p._Product__name for p in result}
        assert "Электронная книга" in names
        assert "Книга со скидкой" in names

        result = shop.find_products_by_name("планшет")
        assert result == []

    def test_display_products(self, shop, capsys):
        shop.display_products()
        captured = capsys.readouterr()
        assert "Ноутбук" in captured.out
        assert "Смартфон" in captured.out
        assert "Электронная книга" in captured.out
        assert "Книга со скидкой" in captured.out

    def test_create_order_success(self, shop, sample_customer, sample_product, another_product):
        cart = shop.get_cart(sample_customer)
        cart.add_item(sample_product, 2)
        cart.add_item(another_product, 1)

        order = shop.create_order(sample_customer)

        assert order.customer == sample_customer
        assert order.items == {"p001": 2, "p002": 1}
        assert order.total_price == 2*50000 + 1*30000

        # Проверка списания со склада
        assert shop.products["p001"].quantity == 8  # было 10
        assert shop.products["p002"].quantity == 4  # было 5

        # Корзина должна очиститься
        assert cart.items == {}

        # Заказ добавлен в список
        assert order in shop.orders

    def test_create_order_insufficient_stock(self, shop, sample_customer, sample_product):
        cart = shop.get_cart(sample_customer)
        cart.add_item(sample_product, 11)  # больше, чем есть

        with pytest.raises(Exception) as excinfo:
            shop.create_order(sample_customer)
        assert "недостаточно товара" in str(excinfo.value).lower()

    def test_create_order_empty_cart(self, shop, sample_customer):
        with pytest.raises(Exception) as excinfo:
            shop.create_order(sample_customer)
        assert "корзина пуста" in str(excinfo.value).lower()


# ---------------------------
# Тесты для наследования и полиморфизма
# ---------------------------

class TestInheritance:
    def test_digital_product_creation(self, digital_product):
        assert digital_product._Product__name == "Электронная книга"
        assert digital_product.file_size == 5
        assert digital_product.download_link == "http://example.com/download"
        # Проверяем is_available
        assert digital_product.is_available(100) is True   # всегда True, если количество большое
        # Можно проверить, если задать quantity = 0, но цифровой товар всё равно доступен?
        # По логике, цифровой товар не кончается, но можно ограничить количество лицензий.
        # В простейшем случае считаем, что всегда доступен.

    def test_digital_product_str(self, digital_product):
        expected = "Электронная книга (p003): 300 руб., в наличии: 1000, формат: цифровой, размер: 5 МБ"
        assert str(digital_product) == expected

    def test_discounted_product_creation(self, discounted_product):
        assert discounted_product._Product__name == "Книга со скидкой"
        assert discounted_product._DiscountedProduct__discount_percent == 10
        assert discounted_product.price == 450  # 500 - 10% = 450

    def test_discounted_product_price_property(self, discounted_product):
        # цена со скидкой
        assert discounted_product.price == 450
        # меняем цену без скидки
        discounted_product._Product__price = 600  # прямой доступ для теста
        assert discounted_product.price == 540  # 600 - 10%
        # меняем процент скидки
        discounted_product.discount_percent = 20
        assert discounted_product.price == 480

    def test_discounted_product_str(self, discounted_product):
        expected = "Книга со скидкой (p004): 450 руб. (скидка 10%), в наличии: 20"
        assert str(discounted_product) == expected

    def test_payment_processors(self, sample_customer):
        order = Order("o001", sample_customer, {"p001": 2}, 100000)

        cc_processor = CreditCardProcessor()
        result = cc_processor.process_payment(order, 100000)
        assert result == f"Оплата заказа {order.order_id} на сумму 100000 прошла по кредитной карте."

        pp_processor = PayPalProcessor()
        result = pp_processor.process_payment(order, 100000)
        assert "PayPal" in result

    def test_shop_create_order_with_payment(self, shop, sample_customer, sample_product):
        cart = shop.get_cart(sample_customer)
        cart.add_item(sample_product, 1)
        processor = CreditCardProcessor()
        order = shop.create_order(sample_customer, processor)
        # проверяем, что заказ создан и оплата прошла (можно по статусу)
        assert order.status == "оплачен"  # если процессор меняет статус


# ---------------------------
# Дополнительные тесты для граничных случаев
# ---------------------------

class TestEdgeCases:
    def test_cart_get_total_price_with_missing_product(self, cart, shop):
        cart.add_item(Product("Тест", 100, 1, "p999"), 1)  # товара нет в каталоге магазина
        with pytest.raises(Exception) as excinfo:
            cart.get_total_price(shop.products)
        assert "не найден" in str(excinfo.value).lower()

    def test_order_status_flow(self, sample_customer):
        order = Order("o001", sample_customer, {}, 0)
        order.update_status("оплачен")
        order.update_status("отправлен")
        order.update_status("доставлен")
        # попытка изменить после доставки
        with pytest.raises(Exception):
            order.update_status("оплачен")
