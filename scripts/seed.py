import os

from app.database import get_connection


def int_setting(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


USERS_COUNT = int_setting("SEED_USERS_COUNT", 1_000_000)
PRODUCTS_COUNT = int_setting("SEED_PRODUCTS_COUNT", 100_000)
ORDERS_COUNT = int_setting("SEED_ORDERS_COUNT", 2_000_000)
ORDER_ITEMS_PER_ORDER_MIN = int_setting("SEED_ORDER_ITEMS_PER_ORDER_MIN", 1)
ORDER_ITEMS_PER_ORDER_MAX = int_setting("SEED_ORDER_ITEMS_PER_ORDER_MAX", 5)
PROGRESS_INTERVAL = int_setting("SEED_PROGRESS_INTERVAL", 100_000)
ORDER_STATUSES = ["pending", "paid", "shipped", "cancelled"]
PAYMENT_METHODS = ["card", "bank_transfer", "wallet"]


def money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def product_price_cents(product_id: int) -> int:
    return 500 + (product_id * 37) % 49_500


def order_item_count(order_id: int) -> int:
    item_range = ORDER_ITEMS_PER_ORDER_MAX - ORDER_ITEMS_PER_ORDER_MIN + 1
    return ORDER_ITEMS_PER_ORDER_MIN + (order_id % item_range)


def total_order_items_count() -> int:
    return sum(order_item_count(order_id) for order_id in range(1, ORDERS_COUNT + 1))


def order_total_cents(order_id: int) -> int:
    total_cents = 0
    for item_index in range(order_item_count(order_id)):
        product_id = 1 + (order_id * 31 + item_index * 17) % PRODUCTS_COUNT
        quantity = 1 + (order_id + item_index) % 5
        total_cents += product_price_cents(product_id) * quantity

    return total_cents


def print_progress(table_name: str, count: int, total: int) -> None:
    if count % PROGRESS_INTERVAL == 0 or count == total:
        print(f"Seeded {count:,}/{total:,} {table_name}...")


async def main() -> None:
    async with get_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                TRUNCATE TABLE transactions, payments, order_items, orders, products, users
                RESTART IDENTITY CASCADE
                """
            )
            await conn.commit()

            async with cursor.copy("COPY users (name, email) FROM STDIN") as copy:
                for user_id in range(1, USERS_COUNT + 1):
                    await copy.write_row((f"User {user_id}", f"user-{user_id}@example.com"))
                    print_progress("users", user_id, USERS_COUNT)
            await conn.commit()

            async with cursor.copy("COPY products (name, description, price) FROM STDIN") as copy:
                for product_id in range(1, PRODUCTS_COUNT + 1):
                    await copy.write_row(
                        (
                            f"Product {product_id}",
                            f"Synthetic product {product_id} for database load testing.",
                            money(product_price_cents(product_id)),
                        )
                    )
                    print_progress("products", product_id, PRODUCTS_COUNT)
            await conn.commit()

            async with cursor.copy("COPY orders (user_id, status, total_amount) FROM STDIN") as copy:
                for order_id in range(1, ORDERS_COUNT + 1):
                    user_id = 1 + (order_id * 13) % USERS_COUNT
                    status = ORDER_STATUSES[order_id % len(ORDER_STATUSES)]

                    await copy.write_row((user_id, status, money(order_total_cents(order_id))))
                    print_progress("orders", order_id, ORDERS_COUNT)
            await conn.commit()

            order_items_count = 0
            total_order_items = total_order_items_count()
            async with cursor.copy(
                "COPY order_items (order_id, product_id, quantity, unit_price) FROM STDIN"
            ) as copy:
                for order_id in range(1, ORDERS_COUNT + 1):
                    for item_index in range(order_item_count(order_id)):
                        product_id = 1 + (order_id * 31 + item_index * 17) % PRODUCTS_COUNT
                        quantity = 1 + (order_id + item_index) % 5
                        await copy.write_row(
                            (order_id, product_id, quantity, money(product_price_cents(product_id)))
                        )
                        order_items_count += 1
                        print_progress("order items", order_items_count, total_order_items)
            await conn.commit()

            async with cursor.copy(
                "COPY payments (order_id, amount, status, payment_method) FROM STDIN"
            ) as copy:
                for order_id in range(1, ORDERS_COUNT + 1):
                    order_status = ORDER_STATUSES[order_id % len(ORDER_STATUSES)]
                    payment_status = "completed" if order_status in {"paid", "shipped"} else "pending"
                    payment_method = PAYMENT_METHODS[order_id % len(PAYMENT_METHODS)]

                    await copy.write_row(
                        (order_id, money(order_total_cents(order_id)), payment_status, payment_method)
                    )
                    print_progress("payments", order_id, ORDERS_COUNT)
            await conn.commit()

            async with cursor.copy(
                "COPY transactions (user_id, order_id, amount, transaction_type, status) FROM STDIN"
            ) as copy:
                for order_id in range(1, ORDERS_COUNT + 1):
                    user_id = 1 + (order_id * 13) % USERS_COUNT
                    order_status = ORDER_STATUSES[order_id % len(ORDER_STATUSES)]
                    transaction_status = "completed" if order_status in {"paid", "shipped"} else "pending"

                    await copy.write_row(
                        (
                            user_id,
                            order_id,
                            money(order_total_cents(order_id)),
                            "purchase",
                            transaction_status,
                        )
                    )
                    print_progress("transactions", order_id, ORDERS_COUNT)

    print(
        f"Seeded {USERS_COUNT} users, {PRODUCTS_COUNT} products, "
        f"and {ORDERS_COUNT} orders."
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


def run() -> None:
    import asyncio

    asyncio.run(main())
