import sqlite3

class SQLStorage():
    ''' Represents a persistence layer for the Potion Shop using SQLite
    '''
    FILENAME = "apothecary_inventory.db"

    def __init__(self):
        ''' initiate access to the data persistence layer
        '''
        self.conn = sqlite3.connect(self.FILENAME)
        self.data_access = self.conn.cursor()

    # ===== APOTHECARY (INGREDIENTS) METHODS =====
    def get_ingredient(self, ingredient_id):
        ''' return a single ingredient identified by ingredient_id
        '''
        self.data_access.execute(
            "SELECT * FROM Apothecary WHERE ingredient_id = ?;", (ingredient_id,))
        row = self.data_access.fetchone()
        if row:
            return Ingredient(row[1], row[2], row[3], row[0])
        return None

    def get_all_ingredients(self):
        ''' return all ingredients stored in the database
        '''
        self.data_access.execute("SELECT * FROM Apothecary;")
        ingredients = []
        for row in self.data_access:
            ingredients.append(Ingredient(row[1], row[2], row[3], row[0]))
        return ingredients

    def save_ingredient(self, ingredient):
        ''' add or update an ingredient
        '''
        if ingredient.ingredient_id == 0:
            self.data_access.execute(
                "INSERT INTO Apothecary(ingredient_name, ingredient_price, ingredient_qoh) VALUES (?, ?, ?)",
                (ingredient.name, ingredient.price, ingredient.quantity))
            ingredient.ingredient_id = self.data_access.lastrowid
        else:
            self.data_access.execute(
                "UPDATE Apothecary SET ingredient_name=?, ingredient_price=?, ingredient_qoh=? WHERE ingredient_id=?",
                (ingredient.name, ingredient.price, ingredient.quantity, ingredient.ingredient_id))
        self.conn.commit()

    def delete_ingredient(self, ingredient_id):
        ''' delete an ingredient by id
        '''
        self.data_access.execute(
            "DELETE FROM Apothecary WHERE ingredient_id=?",
            (int(ingredient_id),))
        self.conn.commit()

    # ===== POTIONS METHODS =====
    def get_potion(self, potion_id):
        ''' return a single potion identified by potion_id
        '''
        self.data_access.execute(
            "SELECT * FROM Potions WHERE potion_id=?;", (potion_id,))
        row = self.data_access.fetchone()
        if row:
            return Potion(row[1], row[2], row[0])
        return None

    def get_all_potions(self):
        ''' return all potions stored in the database
        '''
        self.data_access.execute("SELECT * FROM Potions;")
        potions = []
        for row in self.data_access:
            potions.append(Potion(row[1], row[2], row[0]))
        return potions

    def save_potion(self, potion):
        ''' add or update a potion
        '''
        if potion.potion_id == 0:
            self.data_access.execute(
                "INSERT INTO Potions(potion_name, effect_description) VALUES (?, ?)",
                (potion.name, potion.effect))
            potion.potion_id = self.data_access.lastrowid
        else:
            self.data_access.execute(
                "UPDATE Potions SET potion_name=?, effect_description=? WHERE potion_id=?",
                (potion.name, potion.effect, potion.potion_id))
        self.conn.commit()

    def delete_potion(self, potion_id):
        ''' delete a potion by id
        '''
        self.data_access.execute(
            "DELETE FROM Potions WHERE potion_id=?",
            (int(potion_id),))
        self.conn.commit()

    # ===== ORDERS METHODS =====
    def get_all_orders(self):
        ''' return all orders
        '''
        self.data_access.execute("SELECT * FROM Orders;")
        orders = []
        for row in self.data_access:
            orders.append({'order_id': row[0], 'customer_name': row[1], 'order_date': row[2]})
        return orders

    def fetch_total_orders_by_item_type(self):
        """Will fetch the total ordered quantity per item from the Orders table"""
        try:
            self.data_access.execute("""
                SELECT item_name, SUM(quantity_req) AS total_ordered
                FROM Orders
                GROUP BY item_name
                ORDER BY total_ordered DESC
            """)
            rows = self.data_access.fetchall()
            # Convert to list of dictionaries for compatibility
            return [{'item_name': row[0], 'total_ordered': row[1]} for row in rows]
        except Exception as e:
            print(f"Error fetching order data: {e}")
            return []

    def update_ingredient(self, ingredient):
        """Update an existing ingredient"""
        self.data_access.execute(
            "UPDATE Apothecary SET ingredient_name=?, ingredient_price=?, ingredient_qoh=? WHERE ingredient_id=?",
            (ingredient.name, ingredient.price, ingredient.quantity, ingredient.ingredient_id)
        )
        self.conn.commit()

    def close(self):
        """Close the database connection"""
        if self.data_access:
            self.conn.commit()
            self.data_access.close()
        if self.conn:
            self.conn.close()

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity
        '''
        self.close()


class Ingredient():
    def __init__(self, name="", price=0, quantity=0, ingredient_id=0):
        self.ingredient_id = ingredient_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f'Ingredient#{self.ingredient_id}: {self.name}, Price: {self.price}, Qty: {self.quantity}'


class Potion():
    def __init__(self, name="", effect="", potion_id=0):
        self.potion_id = potion_id
        self.name = name
        self.effect = effect

    def __str__(self):
        return f'Potion#{self.potion_id}: {self.name}, Effect: {self.effect}'