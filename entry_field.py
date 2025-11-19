import tkinter as tk
import sys
from models import SQLStorage, Ingredient, Potion


class EntryField(tk.Frame):
    def __init__(self, parent, label='', field_type='text', options=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.dataentry = tk.StringVar()
        self.label = label
        self.field_type = field_type
        self.options = options or []
        self.storage = SQLStorage()

        self.title = tk.Label(self, text=label, width=15)
        self.title.grid(row=0, column=0, padx=10, sticky=tk.W)

        # Create different field types based on the field_type parameter
        if field_type == 'password':
            self.field = tk.Entry(self, width=30, textvariable=self.dataentry, show="*")
        elif field_type == 'dropdown':
            self.field = tk.OptionMenu(self, self.dataentry, *self.options)
            self.field.config(width=27)
        elif field_type == 'number':
            self.field = tk.Entry(self, width=30, textvariable=self.dataentry)
            # Add validation for numbers only
            vcmd = (self.register(self.validate_number), '%P')
            self.field.config(validate="key", validatecommand=vcmd)
        elif field_type == 'text_area':
            self.field = tk.Text(self, width=30, height=4)
            # For text areas, we'll handle data differently
            self.dataentry = None
        else:  # default text field
            self.field = tk.Entry(self, width=30, textvariable=self.dataentry)

        self.field.grid(row=0, column=1, padx=15, sticky=(tk.W + tk.E))

    def validate_number(self, value):
        """Validate that the input is a number"""
        if value == "" or value.isdigit():
            return True
        return False

    def reset(self):
        if self.field_type == 'text_area':
            self.field.delete('1.0', tk.END)
        else:
            self.dataentry.set("")

    def get(self):
        if self.field_type == 'text_area':
            return self.field.get('1.0', tk.END).strip()
        else:
            return self.dataentry.get()

    def set(self, value):
        if self.field_type == 'text_area':
            self.field.delete('1.0', tk.END)
            self.field.insert('1.0', value)
        else:
            self.dataentry.set(value)

    def load_ingredients_dropdown(self):
        """Load ingredients from database for dropdown"""
        ingredients = self.storage.get_all_ingredients()
        self.options = [f"{ing.name} (ID: {ing.ingredient_id})" for ing in ingredients]
        if hasattr(self, 'field') and self.field_type == 'dropdown':
            # Update the dropdown menu
            menu = self.field["menu"]
            menu.delete(0, "end")
            for option in self.options:
                menu.add_command(label=option,
                                 command=lambda value=option: self.dataentry.set(value))

    def load_potions_dropdown(self):
        """Load potions from database for dropdown"""
        potions = self.storage.get_all_potions()
        self.options = [f"{pot.name} (ID: {pot.potion_id})" for pot in potions]
        if hasattr(self, 'field') and self.field_type == 'dropdown':
            # Update the dropdown menu
            menu = self.field["menu"]
            menu.delete(0, "end")
            for option in self.options:
                menu.add_command(label=option,
                                 command=lambda value=option: self.dataentry.set(value))


class DatabaseForm(tk.Frame):
    """A reusable form for database operations"""

    def __init__(self, parent, form_type='ingredient', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.form_type = form_type
        self.storage = SQLStorage()
        self.fields = {}
        self.create_form()

    def create_form(self):
        """Create form fields based on form type"""
        if self.form_type == 'ingredient':
            self.fields['name'] = EntryField(self, 'Ingredient Name:', 'text')
            self.fields['price'] = EntryField(self, 'Price:', 'number')
            self.fields['quantity'] = EntryField(self, 'Quantity:', 'number')

        elif self.form_type == 'potion':
            self.fields['name'] = EntryField(self, 'Potion Name:', 'text')
            self.fields['effect'] = EntryField(self, 'Effect:', 'text_area')

        elif self.form_type == 'order':
            self.fields['customer'] = EntryField(self, 'Customer Name:', 'text')
            # These would be populated from database
            self.fields['ingredients'] = EntryField(self, 'Ingredients:', 'dropdown', [])
            self.fields['potions'] = EntryField(self, 'Potions:', 'dropdown', [])

        # Position all fields
        for i, field in enumerate(self.fields.values()):
            field.grid(row=i, column=0, sticky=(tk.W + tk.E), pady=5)

    def save_to_database(self):
        """Save form data to database"""
        try:
            if self.form_type == 'ingredient':
                ingredient = Ingredient(
                    name=self.fields['name'].get(),
                    price=int(self.fields['price'].get()),
                    quantity=int(self.fields['quantity'].get())
                )
                self.storage.save_ingredient(ingredient)
                return f"Ingredient '{ingredient.name}' saved!"

            elif self.form_type == 'potion':
                potion = Potion(
                    name=self.fields['name'].get(),
                    effect=self.fields['effect'].get()
                )
                self.storage.save_potion(potion)
                return f"Potion '{potion.name}' saved!"

        except Exception as e:
            return f"Error saving: {str(e)}"

    def load_from_database(self, record_id):
        """Load data from database into form"""
        try:
            if self.form_type == 'ingredient':
                ingredient = self.storage.get_ingredient(record_id)
                if ingredient:
                    self.fields['name'].set(ingredient.name)
                    self.fields['price'].set(str(ingredient.price))
                    self.fields['quantity'].set(str(ingredient.quantity))

            elif self.form_type == 'potion':
                potion = self.storage.get_potion(record_id)
                if potion:
                    self.fields['name'].set(potion.name)
                    self.fields['effect'].set(potion.effect)

        except Exception as e:
            print(f"Error loading: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        for field in self.fields.values():
            field.reset()

    def refresh_dropdowns(self):
        """Refresh dropdowns with latest data from database"""
        if 'ingredients' in self.fields:
            self.fields['ingredients'].load_ingredients_dropdown()
        if 'potions' in self.fields:
            self.fields['potions'].load_potions_dropdown()