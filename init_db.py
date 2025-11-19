import sqlite3
import csv
import os


def initialize_database():
    conn = sqlite3.connect('apothecary_inventory.db')
    cur = conn.cursor()

    # Create tables
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Apothecary
                (
                    ingredient_id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    ingredient_name
                    VARCHAR
                (
                    100
                ) UNIQUE NOT NULL,
                    ingredient_price INTEGER NOT NULL,
                    ingredient_qoh INTEGER NOT NULL,
                    CHECK
                (
                    ingredient_qoh
                    BETWEEN
                    0
                    AND
                    1000
                )
                    )
                ''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Potions
                (
                    potion_id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    potion_name
                    VARCHAR
                (
                    100
                ) UNIQUE NOT NULL,
                    effect_description TEXT NOT NULL
                    )
                ''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Potion_Ingredients
                (
                    potion_id
                    INTEGER,
                    ingredient_id
                    INTEGER,
                    quantity
                    INTEGER
                    DEFAULT
                    1,
                    PRIMARY
                    KEY
                (
                    potion_id,
                    ingredient_id
                ),
                    FOREIGN KEY
                (
                    potion_id
                ) REFERENCES Potions
                (
                    potion_id
                ),
                    FOREIGN KEY
                (
                    ingredient_id
                ) REFERENCES Apothecary
                (
                    ingredient_id
                )
                    )
                ''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Orders
                (
                    order_id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    customer_name
                    VARCHAR
                (
                    100
                ) NOT NULL,
                    order_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Order_Ingredients
                (
                    order_id
                    INTEGER,
                    ingredient_id
                    INTEGER,
                    quantity
                    INTEGER
                    DEFAULT
                    1,
                    PRIMARY
                    KEY
                (
                    order_id,
                    ingredient_id
                ),
                    FOREIGN KEY
                (
                    order_id
                ) REFERENCES Orders
                (
                    order_id
                ),
                    FOREIGN KEY
                (
                    ingredient_id
                ) REFERENCES Apothecary
                (
                    ingredient_id
                )
                    )
                ''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Order_Potions
                (
                    order_id
                    INTEGER,
                    potion_id
                    INTEGER,
                    quantity
                    INTEGER
                    DEFAULT
                    1,
                    PRIMARY
                    KEY
                (
                    order_id,
                    potion_id
                ),
                    FOREIGN KEY
                (
                    order_id
                ) REFERENCES Orders
                (
                    order_id
                ),
                    FOREIGN KEY
                (
                    potion_id
                ) REFERENCES Potions
                (
                    potion_id
                )
                    )
                ''')

    # Read data from CSV file
    csv_filename = 'InventoryManagement2.csv'

    if not os.path.exists(csv_filename):
        print(f"Error: CSV file '{csv_filename}' not found!")
        print("Please make sure InventoryManagement2.csv is in the same directory as this script.")
        conn.close()
        return

    # Extract unique ingredients and potions from CSV
    ingredients = set()
    potions = set()
    potion_recipes = {}
    customers = set()

    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Skip header row

            for row in reader:
                if len(row) > 0 and row[0].strip():  # Has ingredient data
                    ingredient_name = row[0].strip()
                    try:
                        price = int(row[1]) if row[1].strip() else 0
                        inventory = int(row[2]) if row[2].strip() else 0
                        ingredients.add((ingredient_name, price, inventory))
                    except ValueError:
                        print(f"Warning: Invalid price or inventory for ingredient '{ingredient_name}'")

                if len(row) > 3 and row[3].strip():  # Has potion data
                    potion_name = row[3].strip()
                    effect = row[4].strip() if len(row) > 4 and row[4].strip() else "No effect description"
                    recipe = row[5].strip() if len(row) > 5 and row[5].strip() else ""
                    potions.add((potion_name, effect))

                    # Store recipe ingredients
                    if recipe:
                        recipe_ingredients = [ing.strip() for ing in recipe.split('\n') if ing.strip()]
                        potion_recipes[potion_name] = recipe_ingredients

                if len(row) > 6 and row[6].strip():  # Has customer data
                    customer_name = row[6].strip()
                    customers.add(customer_name)

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        conn.close()
        return

    # Clear existing data and insert new data
    cur.execute("DELETE FROM Potion_Ingredients")
    cur.execute("DELETE FROM Order_Ingredients")
    cur.execute("DELETE FROM Order_Potions")
    cur.execute("DELETE FROM Apothecary")
    cur.execute("DELETE FROM Potions")
    cur.execute("DELETE FROM Orders")

    # Insert ingredients
    ingredient_id_map = {}
    for name, price, qoh in ingredients:
        cur.execute(
            "INSERT INTO Apothecary (ingredient_name, ingredient_price, ingredient_qoh) VALUES (?, ?, ?)",
            (name, price, qoh)
        )
        ingredient_id = cur.lastrowid
        ingredient_id_map[name] = ingredient_id

    # Insert potions
    potion_id_map = {}
    for name, effect in potions:
        cur.execute(
            "INSERT INTO Potions (potion_name, effect_description) VALUES (?, ?)",
            (name, effect)
        )
        potion_id = cur.lastrowid
        potion_id_map[name] = potion_id

    # Insert potion recipes
    for potion_name, recipe_ingredients in potion_recipes.items():
        potion_id = potion_id_map.get(potion_name)
        if potion_id:
            for ing_name in recipe_ingredients:
                ingredient_id = ingredient_id_map.get(ing_name)
                if ingredient_id:
                    cur.execute(
                        "INSERT INTO Potion_Ingredients (potion_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                        (potion_id, ingredient_id, 1)  # Default quantity of 1
                    )

    # Insert customers as orders
    for customer_name in customers:
        cur.execute(
            "INSERT INTO Orders (customer_name) VALUES (?)",
            (customer_name,)
        )

    conn.commit()
    conn.close()

    print("Database initialized successfully with CSV data!")
    print(f"Added {len(ingredients)} ingredients and {len(potions)} potions")
    print(f"Added {len(customers)} customers")
    print(f"Added {len(potion_recipes)} potion recipes")


if __name__ == '__main__':
    initialize_database()
