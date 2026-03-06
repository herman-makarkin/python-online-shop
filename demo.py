from src.classes import (
    Product,
    Customer,
    Cart,
    Order,
    Shop,
    DigitalProduct,
    DiscountedProduct,
    CreditCardProcessor,
    PayPalProcessor,
)


def main():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ ОНЛАЙН-МАГАЗИНА")
    print("=" * 60)

    shop = Shop()

    print("\n1. ДОБАВЛЕНИЕ ТОВАРОВ")
    print("-" * 40)

    laptop = Product("Ноутбук Gaming Pro", 85000, 10, "p001")
    phone = Product("Смартфон Ultra", 55000, 15, "p002")
    ebook = DigitalProduct(
        "Электронная книга Python",
        1500,
        1000,
        "p003",
        15,
        "https://shop.example.com/download/python-book",
    )
    sale_item = DiscountedProduct("Наушники Premium", 8000, 20, "p004", 25)

    shop.add_product(laptop)
    shop.add_product(phone)
    shop.add_product(ebook)
    shop.add_product(sale_item)

    print(f"Добавлено товаров: {len(shop)}")
    shop.display_products()

    print("\n2. РЕГИСТРАЦИЯ ПОКУПАТЕЛЕЙ")
    print("-" * 40)

    customer1 = Customer("Иван Петров", "c001", "ivan@example.com")
    customer2 = Customer("Мария Сидорова", "c002", "maria@example.com")

    shop.register_customer(customer1)
    shop.register_customer(customer2)

    print(customer1)
    print(customer2)

    print("\n3. ПОИСК ТОВАРОВ")
    print("-" * 40)

    results = shop.find_products_by_name("телефон")
    print(f"Поиск 'телефон': найдено {len(results)} товаров")
    for p in results:
        print(f"  - {p}")

    results = shop.find_products_by_name("python")
    print(f"Поиск 'python': найдено {len(results)} товаров")
    for p in results:
        print(f"  - {p}")

    print("\n4. РАБОТА С КОРЗИНОЙ")
    print("-" * 40)

    cart = shop.get_cart(customer1)
    cart.add_item(laptop, 1)
    cart.add_item(phone, 2)
    cart.add_item(ebook, 1)
    cart.add_item(sale_item, 1)

    print(cart)
    print(f"\nОбщая стоимость: {cart.get_total_price(shop.products)} руб.")

    print("\n5. ОФОРМЛЕНИЕ ЗАКАЗА (без оплаты)")
    print("-" * 40)

    order = shop.create_order(customer1)
    print(order)
    print(f"Статус: {order.status}")

    print("\n6. ИЗМЕНЕНИЕ СТАТУСА ЗАКАЗА")
    print("-" * 40)

    order.update_status("оплачен")
    print(f"После оплаты: {order.status}")

    order.update_status("отправлен")
    print(f"После отправки: {order.status}")

    order.update_status("доставлен")
    print(f"После доставки: {order.status}")

    print("\n7. ЗАКАЗ С ОПЛАТОЙ (вторая корзина)")
    print("-" * 40)

    cart2 = shop.get_cart(customer2)
    cart2.add_item(laptop, 1)
    cart2.add_item(sale_item, 2)

    print(cart2)
    print(f"\nОбщая стоимость: {cart2.get_total_price(shop.products)} руб.")

    print("\nОплата кредитной картой:")
    processor = CreditCardProcessor()
    order2 = shop.create_order(customer2, processor)
    print(order2)

    print("\n8. МАГИЧЕСКИЕ МЕТОДЫ SHOP")
    print("-" * 40)

    print(f"Количество товаров в магазине: {len(shop)}")
    print(f"Товар по индексу 0: {shop[0]}")
    print(f"Товар по id 'p002': {shop['p002']}")

    print("\n9. ДЕМОНСТРАЦИЯ ПОЛИМОРФИЗМА")
    print("-" * 40)

    products = [laptop, phone, ebook, sale_item]
    print("Информация о товарах (разные типы):")
    for p in products:
        available = "Да" if p.is_available(1) else "Нет"
        print(f"  {type(p).__name__}: {p.name} - доступен: {available}")

    print("\n10. ПРОВЕРКА СКИДОК")
    print("-" * 40)

    print(f"Наушники: базовая цена использовалась при создании")
    print(f"Цена со скидкой 25%: {sale_item.price} руб.")
    sale_item.discount_percent = 30
    print(f"Цена со скидкой 30%: {sale_item.price} руб.")

    print("\n11. ЦИФРОВЫЕ ТОВАРЫ")
    print("-" * 40)

    print(f"Электронная книга:")
    print(f"  Размер: {ebook.file_size} МБ")
    print(f"  Ссылка: {ebook.download_link}")
    print(f"  Доступность (10000 шт): {ebook.is_available(10000)}")

    print("\n12. СОХРАНЕНИЕ В JSON")
    print("-" * 40)

    shop.save_to_json("shop_data.json")
    print("Данные сохранены в shop_data.json")

    print("\n13. ЗАГРУЗКА ИЗ JSON")
    print("-" * 40)

    new_shop = Shop()
    new_shop.load_from_json("shop_data.json")
    print(f"Загружено товаров: {len(new_shop)}")
    print(f"Загружено покупателей: {len(new_shop.customers)}")
    print(f"Загружено заказов: {len(new_shop.orders)}")

    print("\n14. ВСЕ ЗАКАЗЫ")
    print("-" * 40)

    for order in shop.orders:
        print(order)

    print("\n15. ОСТАТКИ НА СКЛАДЕ")
    print("-" * 40)

    shop.display_products()

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("Логи сохранены в shop.log")
    print("=" * 60)


if __name__ == "__main__":
    main()
