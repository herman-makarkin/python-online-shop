class Product:
    def __init__(self, name, price, quantity, product_id):
        self.__name = name
        self.__price = None
        self.__quantity = None
        self.product_id = product_id
        self.price = price
        self.quantity = quantity

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("Цена должна быть положительной")
        self.__price = value

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            raise ValueError("Количество не может быть отрицательным")
        self.__quantity = value

    def is_available(self, needed_quantity):
        return self.__quantity >= needed_quantity

    def __str__(self):
        return f"{self.__name} ({self.product_id}): {self.__price} руб., в наличии: {self.__quantity}"


class Customer:
    def __init__(self, name, customer_id, email):
        self.__name = name
        self.customer_id = customer_id
        self.__email = None
        self.email = email

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if '@' not in value:
            raise ValueError("Email должен содержать символ '@'")
        self.__email = value

    def __str__(self):
        return f"{self.__name} ({self.customer_id}), email: {self.__email}"


class Cart:
    def __init__(self, customer, check_stock=True):
        self.customer = customer
        self.items = {}
        self.__products = {}
        self.__check_stock = check_stock

    def add_item(self, product, quantity):
        product_id = product.product_id
        if self.__check_stock:
            if product_id in self.items:
                total = self.items[product_id] + quantity
                if not product.is_available(total):
                    raise Exception(f"Недостаточно товара {product_id} на складе")
            else:
                if not product.is_available(quantity):
                    raise Exception(f"Недостаточно товара {product_id} на складе")
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity
            self.__products[product_id] = product

    def remove_item(self, product_id):
        if product_id not in self.items:
            raise Exception(f"Товар {product_id} нет в корзине")
        del self.items[product_id]
        if product_id in self.__products:
            del self.__products[product_id]

    def update_quantity(self, product_id, new_quantity):
        if product_id not in self.items:
            raise Exception(f"Товар {product_id} нет в корзине")
        product = self.__products.get(product_id)
        if self.__check_stock and product and not product.is_available(new_quantity):
            raise Exception(f"Недостаточно товара {product_id} на складе")
        self.items[product_id] = new_quantity

    def get_total_price(self, product_catalog):
        total = 0
        for product_id, quantity in self.items.items():
            if product_id not in product_catalog:
                raise Exception(f"Товар {product_id} не найден в каталоге")
            total += product_catalog[product_id].price * quantity
        return total

    def clear(self):
        self.items = {}
        self.__products = {}

    def __str__(self):
        lines = [f"Корзина покупателя {self.customer._Customer__name}:"]
        for product_id, quantity in self.items.items():
            product = self.__products.get(product_id)
            name = product._Product__name if product else product_id
            lines.append(f"  {name}: {quantity} шт.")
        return "\n".join(lines)


class Order:
    VALID_STATUSES = ["новый", "оплачен", "отправлен", "доставлен"]
    STATUS_ORDER = ["новый", "оплачен", "отправлен", "доставлен"]

    def __init__(self, order_id, customer, items, total_price):
        self.order_id = order_id
        self.customer = customer
        self.items = items.copy()
        self.total_price = total_price
        self.status = "новый"

    def update_status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise Exception(f"Недопустимый статус: {new_status}")

        current_index = self.STATUS_ORDER.index(self.status)
        new_index = self.STATUS_ORDER.index(new_status)

        if new_index <= current_index:
            raise Exception(f"Нельзя перейти от статуса '{self.status}' к '{new_status}'")

        self.status = new_status

    def __str__(self):
        return f"Заказ {self.order_id}, покупатель {self.customer._Customer__name}, статус: {self.status}, сумма: {self.total_price} руб."


class Shop:
    def __init__(self):
        self.products = {}
        self.customers = {}
        self.orders = []
        self.carts = {}
        self.__order_counter = 0

    def add_product(self, product):
        self.products[product.product_id] = product

    def register_customer(self, customer):
        self.customers[customer.customer_id] = customer

    def get_cart(self, customer):
        if customer.customer_id not in self.carts:
            self.carts[customer.customer_id] = Cart(customer, check_stock=False)
        return self.carts[customer.customer_id]

    def create_order(self, customer, payment_processor=None):
        cart = self.carts.get(customer.customer_id)
        if not cart or not cart.items:
            raise Exception("Корзина пуста")

        for product_id, quantity in cart.items.items():
            product = self.products[product_id]
            if not product.is_available(quantity):
                raise Exception(f"Недостаточно товара {product_id} на складе")

        total_price = cart.get_total_price(self.products)

        for product_id, quantity in cart.items.items():
            self.products[product_id].quantity -= quantity

        self.__order_counter += 1
        order = Order(f"o{self.__order_counter:03d}", customer, cart.items, total_price)

        if payment_processor:
            payment_processor.process_payment(order, total_price)
            order.status = "оплачен"

        cart.clear()
        self.orders.append(order)
        return order

    def find_products_by_name(self, name):
        result = []
        search_term = name.lower()
        for product in self.products.values():
            if search_term in product._Product__name.lower():
                result.append(product)
        return result

    def display_products(self):
        for product in self.products.values():
            print(product)

    def __len__(self):
        return len(self.products)

    def __getitem__(self, key):
        if isinstance(key, int):
            products_list = list(self.products.values())
            return products_list[key]
        return self.products.get(key)


class DigitalProduct(Product):
    def __init__(self, name, price, quantity, product_id, file_size, download_link):
        super().__init__(name, price, quantity, product_id)
        self.file_size = file_size
        self.download_link = download_link

    def is_available(self, needed_quantity):
        return True

    def __str__(self):
        return f"{self._Product__name} ({self.product_id}): {self._Product__price} руб., в наличии: {self._Product__quantity}, формат: цифровой, размер: {self.file_size} МБ"


class DiscountedProduct(Product):
    def __init__(self, name, price, quantity, product_id, discount_percent):
        super().__init__(name, price, quantity, product_id)
        self.__discount_percent = discount_percent

    @property
    def discount_percent(self):
        return self.__discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        if value < 0 or value > 100:
            raise ValueError("Скидка должна быть от 0 до 100")
        self.__discount_percent = value

    @property
    def price(self):
        base_price = self._Product__price
        discounted = base_price - (base_price * self.__discount_percent / 100)
        return int(discounted)

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("Цена должна быть положительной")
        self._Product__price = value

    def __str__(self):
        return f"{self._Product__name} ({self.product_id}): {self.price} руб. (скидка {self.__discount_percent}%), в наличии: {self._Product__quantity}"


class PaymentProcessor:
    def process_payment(self, order, amount):
        raise NotImplementedError("Метод должен быть переопределен")


class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, order, amount):
        return f"Оплата заказа {order.order_id} на сумму {amount} прошла по кредитной карте."


class PayPalProcessor(PaymentProcessor):
    def process_payment(self, order, amount):
        return f"Оплата заказа {order.order_id} на сумму {amount} прошла через PayPal."
