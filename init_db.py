import sqlite3
import csv
import os

def initialize_database():
    """Initialize the database - only run this manually when you want to reset"""
    conn = sqlite3.connect('apothecary_inventory.db')
    cur = conn.cursor()

    # Create tables only if they don't exist
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Apothecary
                (
                    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name VARCHAR (100) UNIQUE NOT NULL,
                    ingredient_price INTEGER NOT NULL,
                    ingredient_qoh INTEGER NOT NULL,
                    CHECK (ingredient_qoh BETWEEN 0 AND 1000)
                    )''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Potions
                (
                    potion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    potion_name VARCHAR (100) UNIQUE NOT NULL,
                    effect_description TEXT NOT NULL
                    )''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Potion_Ingredients
                (
                    potion_id INTEGER,
                    ingredient_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    PRIMARY KEY (potion_id, ingredient_id ),
                    FOREIGN KEY (potion_id) REFERENCES Potions (potion_id),
                    FOREIGN KEY (ingredient_id) REFERENCES Apothecary (ingredient_id)
                    )''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Orders
                (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name VARCHAR (100) NOT NULL,
                    order_status INTEGER NOT NULL, -- 0:requested, 1:ongoing, 2:completed, 3:unable to complete
                    CHECK (order_status BETWEEN 0 AND 4)
                    )''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Order_Ingredients
                (
                    order_id INTEGER,
                    ingredient_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    PRIMARY KEY (order_id,ingredient_id),
                    FOREIGN KEY (order_id) REFERENCES Orders (order_id),
                    FOREIGN KEY (ingredient_id) REFERENCES Apothecary (ingredient_id)
                    )''')

    cur.execute('''
                CREATE TABLE IF NOT EXISTS Order_Potions
                (
                    order_id INTEGER,
                    potion_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    PRIMARY KEY (order_id,potion_id),
                    FOREIGN KEY (order_id) REFERENCES Orders (order_id),
                    FOREIGN KEY (potion_id) REFERENCES Potions (potion_id)
                    )''')

    # Check if database is empty and populate with CSV data
    cur.execute("SELECT COUNT(*) FROM Apothecary")
    if cur.fetchone()[0] == 0:
        print("Populating database with CSV data...")
        populate_from_csv(cur)
    else:
        print("Database already populated. Skipping data insertion.")

    conn.commit()
    conn.close()
    print("Database initialization complete!")

def populate_from_csv(cur):
    """Populate database with data from CSV file"""
    csv_filename = 'InventoryManagement2.csv'

    if not os.path.exists(csv_filename):
        print(f"Error: CSV file '{csv_filename}' not found!")
        return

    # Extract unique ingredients and potions from CSV
    ingredients = set()
    potions = set()
    potion_recipes = {}
    customers = set()
    orders_data = []  # Store order information

    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Skip header row

            for row_num, row in enumerate(reader, start=2):
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

                    # Process BOTH types of orders
                    apothecary_items = ""
                    brewery_items = ""

                    if len(row) > 7 and row[7].strip():
                        apothecary_items = row[7].strip()

                    if len(row) > 8 and row[8].strip():
                        brewery_items = row[8].strip()

                    # Only add if there are actual items (not just "0" status)
                    if (apothecary_items and apothecary_items != "0") or (brewery_items and brewery_items != "0"):
                        orders_data.append({
                            'customer_name': customer_name,
                            'apothecary_items': apothecary_items,
                            'brewery_items': brewery_items
                        })

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
                            (potion_id, ingredient_id, 1)
                        )

        # Insert orders with BOTH types of items
        for order_info in orders_data:
            customer_name = order_info['customer_name']
            apothecary_items = order_info['apothecary_items']
            brewery_items = order_info['brewery_items']

            # Create the order
            cur.execute(
                "INSERT INTO Orders (customer_name, order_status) VALUES (?, ?)",
                (customer_name, 0)  # All orders start as requested (status 0)
            )
            order_id = cur.lastrowid

            # Parse Apothecary items (ingredients) - FIXED: Skip header words
            if apothecary_items and apothecary_items != "0":
                items = []
                if '\n' in apothecary_items:
                    items = [item.strip() for item in apothecary_items.split('\n') if item.strip()]
                else:
                    items = [item.strip() for item in apothecary_items.split(',') if item.strip()]

                for item in items:
                    item = item.strip()
                    # Skip header words that aren't actual ingredients
                    if item.lower() in ['ingredients', 'potions']:
                        continue
                    if item in ingredient_id_map:
                        ingredient_id = ingredient_id_map[item]
                        cur.execute(
                            "INSERT INTO Order_Ingredients (order_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                            (order_id, ingredient_id, 1)
                        )
                    else:
                        print(f"Warning: Unknown ingredient '{item}' in order for customer '{customer_name}'")

            # Parse Brewery items (potions) - FIXED: Skip header words
            if brewery_items and brewery_items != "0":
                items = []
                if '\n' in brewery_items:
                    items = [item.strip() for item in brewery_items.split('\n') if item.strip()]
                else:
                    items = [item.strip() for item in brewery_items.split(',') if item.strip()]

                for item in items:
                    item = item.strip()
                    # Skip header words that aren't actual potions
                    if item.lower() in ['ingredients', 'potions']:
                        continue
                    if item in potion_id_map:
                        potion_id = potion_id_map[item]
                        cur.execute(
                            "INSERT INTO Order_Potions (order_id, potion_id, quantity) VALUES (?, ?, ?)",
                            (order_id, potion_id, 1)
                        )
                    else:
                        print(f"Warning: Unknown potion '{item}' in order for customer '{customer_name}'")

        print(
            f"Added {len(ingredients)} ingredients, {len(potions)} potions, {len(customers)} customers, and {len(orders_data)} orders with items")

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    initialize_database()