#!/usr/bin/env python3
import argparse
import json
import random
import string
import sys
import uuid
from datetime import datetime


def random_string(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_email():
    user = "".join(random.choices(string.ascii_lowercase, k=7))
    domain = random.choice(["example.com", "test.com", "mail.com"])
    return f"{user}@{domain}"


def random_date():
    # ISO‐format date
    return datetime.now().strftime("%Y-%m-%d")


def random_shipping_method():
    return random.choice(["standard", "express", "overnight"])


def random_item():
    return {
        "product_sku": random_string(6).upper(),
        "qty_ordered": random.randint(1, 10),
        "price_per_unit": round(random.uniform(5.0, 500.0), 2),
    }


def random_address():
    streets = ["Main St", "Second St", "Third St", "Elm St", "Oak Ave"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Berlin"]
    countries = ["USA", "Canada", "UK", "Germany", "France"]
    return {
        "street_address": f"{random.randint(1, 999)} {random.choice(streets)}",
        "city": random.choice(cities),
        "postal_code": "".join(random.choices(string.digits, k=5)),
        "country": random.choice(countries),
    }


def generate_order():
    return {
        "order_id": str(uuid.uuid4()),
        "order_date": random_date(),
        "customer_email": random_email(),
        "shipping_method": random_shipping_method(),
        "items": [random_item() for _ in range(random.randint(1, 5))],
        "notes": "",
        "shipping_address": random_address(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate N random orders (per given JSON schema) and dump to a file."
    )
    parser.add_argument("N", type=int, help="number of orders to generate")
    parser.add_argument(
        "-o", "--output", required=True, help="path to output JSON file"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=100,
        help="print progress every INTERVAL orders (default: 100)",
    )
    args = parser.parse_args()

    orders = []
    for i in range(args.N):
        orders.append(generate_order())
        # progress every `interval`
        if (i + 1) % args.interval == 0 or (i + 1) == args.N:
            print(f"Generated {i + 1}/{args.N} orders", file=sys.stderr)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
