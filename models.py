import sqlite3

class SQLStorage():
    ''' Represents a persistence layer for the Potion Shop using SQLite
    '''
    FILENAME = "Howls_DB.db"  # Changed to match your new database

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
            "SELECT * FROM ApothecaryInventoryTable WHERE Item_Id = ?;", (ingredient_id,))
        row = self.data_access.fetchone()
        if row:
            return Ingredient(row[1], row[2], row[3], row[0])  # Name, Price, Qoh, Id
        return None

    def get_all_ingredients(self):
        ''' return all ingredients stored in the database
        '''
        self.data_access.execute("SELECT * FROM ApothecaryInventoryTable;")
        ingredients = []
        for row in self.data_access:
            ingredients.append(Ingredient(row[1], row[2], row[3], row[0]))  # Name, Price, Qoh, Id
        return ingredients

    def save_ingredient(self, ingredient):
        ''' add or update an ingredient
        '''
        if ingredient.ingredient_id == 0:
            self.data_access.execute(
                "INSERT INTO ApothecaryInventoryTable(Item_Name, Item_Price, Item_Qoh) VALUES (?, ?, ?)",
                (ingredient.name, ingredient.price, ingredient.quantity))
            ingredient.ingredient_id = self.data_access.lastrowid
        else:
            self.data_access.execute(
                "UPDATE ApothecaryInventoryTable SET Item_Name=?, Item_Price=?, Item_Qoh=? WHERE Item_Id=?",
                (ingredient.name, ingredient.price, ingredient.quantity, ingredient.ingredient_id))
        self.conn.commit()

    def delete_ingredient(self, ingredient_id):
        ''' delete an ingredient by id
        '''
        self.data_access.execute(
            "DELETE FROM ApothecaryInventoryTable WHERE Item_Id=?",
            (int(ingredient_id),))
        self.conn.commit()

    # ===== POTIONS METHODS =====
    def get_potion(self, potion_id):
        ''' return a single potion identified by potion_id
        '''
        self.data_access.execute(
            "SELECT * FROM PotionsPantryTable WHERE Item_Id=?;", (potion_id,))
        row = self.data_access.fetchone()
        if row:
            return Potion(row[1], row[2], row[0])  # Name, Effect, Id
        return None

    def get_all_potions(self):
        ''' return all potions stored in the database
        '''
        self.data_access.execute("SELECT * FROM PotionsPantryTable;")
        potions = []
        for row in self.data_access:
            potions.append(Potion(row[1], row[2], row[0]))  # Name, Effect, Id
        return potions

    def save_potion(self, potion):
        ''' add or update a potion
        '''
        if potion.potion_id == 0:
            self.data_access.execute(
                "INSERT INTO PotionsPantryTable(Item_Name, Item_Description, Item_Recipe) VALUES (?, ?, ?)",
                (potion.name, potion.effect, ""))  # Empty recipe for new potions
            potion.potion_id = self.data_access.lastrowid
        else:
            self.data_access.execute(
                "UPDATE PotionsPantryTable SET Item_Name=?, Item_Description=? WHERE Item_Id=?",
                (potion.name, potion.effect, potion.potion_id))
        self.conn.commit()

    def delete_potion(self, potion_id):
        ''' delete a potion by id
        '''
        self.data_access.execute(
            "DELETE FROM PotionsPantryTable WHERE Item_Id=?",
            (int(potion_id),))
        self.conn.commit()

    # ===== ORDERS METHODS =====
    def get_all_orders(self):
        ''' return all orders
        '''
        self.data_access.execute("SELECT * FROM RequestLedgerTable;")
        orders = []
        for row in self.data_access:
            orders.append({
                'order_id': row[0], 
                'customer_name': row[1], 
                'apothecary_order': row[2],
                'potion_order': row[3],
                'status': row[4]
            })
        return orders

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity
        '''
        if self.data_access:
            self.conn.commit()
            self.data_access.close()
            self.conn.close()


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
