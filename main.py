#CCT211 Assignment 2--Persistent Form
#Comments: The Login image was a image sourced from Google; otherwise, all other visual assets were directly created by our group

from cProfile import label
import tkinter as tk
from tkinter import ttk, messagebox
import models
from models import SQLStorage
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

import init_db
init_db.initialize_database()

#GLOBAL THEME (consistent widget rendering on macOS + Windows)
def configure_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")   # "CLAM" style to ensure its consistent across both OS systems; replaces the default Aqua theme on macOS

    #Configures consistent styling across ALL widgets
    style.configure("TEntry", padding = 4)
    style.configure("TButton", padding = 6)
    style.configure("TLabel", background = "white")
    style.configure("NavButton.TButton", background = "white")

    #NAVIGATION Styling
    style.configure("NavButton.TButton", font = ("Verdana", 10), background = "white") #when unactive
    style.configure("BoldNav.TButton", font = ("Verdana", 10, "bold"), background = "white") #when active

    style.map("Treeview.Heading",background=[],relief=[])
    style.map("Vertical.TScrollbar", background=[], arrowcolor=[])

#the NAVIGATION
class NavigationBar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white", bd = .5, relief = "solid")
        self.controller = controller
        self.nav_buttons = {}

        nav_items = [ #list of NAVIGATION items
            ("Overview", OverviewPage), #Overview / Welcome Chamber
            ("Apothecary", PotionPantryPage), #Inventory / Potion Pantry
            ("Request Scrolls", RequestScrollsPage), #Orders / Request Scrolls
        ]

        #MENU ITEMS (displayed using button widgets to show user activity and sub options were not needed)
        for text, page_class in nav_items:
            navBtn = ttk.Button(
                self,
                text = text,
                style = "NavButton.TButton",
                command = lambda p = page_class: controller.show_frame(p)
            )
            navBtn.pack(side = "left", padx = 18)
            self.nav_buttons[page_class] = navBtn

        #WELCOME MENU item (displayed on the right side of the menu; welcomes whichever user who signed in)
        self.welcome_label = ttk.Label(
            self,
            text = "Welcome!",
            font = ("Verdana", 10, "italic"),
        )
        self.welcome_label.pack(side = "right", padx = 18)

    #UPDATES ACTIVE FRAME (based on user interactions)
    def update_active(self, active_page):
        for page_class, button in self.nav_buttons.items():
            if page_class == active_page:
                button.config(style = "BoldNav.TButton")
            else:
                button.config(style = "NavButton.TButton")

    def refresh_username(self):
        username = self.controller.username
        if username:
            self.welcome_label.config(text = f"Welcome {username.capitalize()}!")
        else:
            self.welcome_label.config(text = "Welcome!")

# Main Application
class CalcifersLedgerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calcifer's Ledger - Magic Record Keeping System")
        self.root.geometry("1400x950")

        #Usernames and Passwords
        self.valid_logins = {
            "howl": "fire123",
            "sophie": "howlcastle",
            "calcifer": "flame!"
        }

        self.username = None
        self.model = models.SQLStorage()  # Single storage instance for entire app

        container = tk.Frame(self.root, bg="white")
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Pass the shared storage to all pages
        for Page in (LoginPage, OverviewPage, PotionPantryPage, RequestScrollsPage):
            frame = Page(parent=container, controller=self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(LoginPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

        #ONLY Updates active nav items when relevant (when the user interacts with them)
        if hasattr(frame, "nav_frame"):
            frame.nav_frame.refresh_username()
            frame.nav_frame.update_active(page_class) #updates active section of the navigation (BOLDS IT)

# Windows in Application
class LoginPage(tk.Frame):
     def __init__(self, parent, controller):
        super().__init__(parent, bg = "")
        self.controller = controller

        #LOGIN frame: Background Image
        bg_path = "Assets/loginBackground.jpg"
        original_bg = Image.open(bg_path)

        window_w, window_h = 1400, 600
        img_w, img_h = original_bg.size

        scale = max(window_w / img_w, window_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized_bg = original_bg.resize((new_w, new_h), Image.Resampling.LANCZOS)

        self.login_bg_img = ImageTk.PhotoImage(resized_bg)

        self.bg_label = tk.Label(self, image=self.login_bg_img)
        self.bg_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=new_w,
            height=new_h
        )
        self.bg_label.lower()   #keeps the background image behind all other widgets

        center_frame = tk.Frame(self.bg_label, bg = "")
        center_frame.place(relx = 0.5, rely = 0.5, anchor = "center")

        #LOGIN TITLE
        title_frame = tk.Frame(center_frame, bg = "white", bd = 2, relief = "solid")
        title_frame.pack(pady = (0, 16))

        ttk.Label( #HEADER TITLE
            title_frame,
            text = "Calcifer’s Ledger",
            font = ("Palatino", 50, "bold"),
        ).pack()

        ttk.Label( #SUBHEADER TITLE
            title_frame,
            text = "Magic Record Keeping System",
            font = ("Verdana", 13),
        ).pack(pady=(0, 8))

        #FORM area (centered within center_frame)
        form_frame = tk.Frame(center_frame, bg = "")
        form_frame.pack()

        #LOGIN ROW
        login_row = tk.Frame(form_frame, bg = "") #the login form row
        login_row.pack(anchor = "center", pady = 6)
        ttk.Label(login_row, text = "Login:", font = ("Verdana", 12)).pack(side = "left", padx = (0, 8))
        #LOGIN ENTRY
        self.login_entry = ttk.Entry(login_row, width = 25)
        self.login_entry.pack(side = "left")

        #PASSWORD ROW
        pass_row = tk.Frame(form_frame, bg = "") #the password form row
        pass_row.pack(anchor = "center", pady = 6)
        ttk.Label(pass_row, text = "Password:", font = ("Verdana", 12)).pack(side = "left", padx = (0, 8))
        #PASS ENTRY
        self.password_entry = ttk.Entry(pass_row, width = 25, show = "*")
        self.password_entry.pack(side = "left")

        #BUTTON
        btn_row = tk.Frame(center_frame, bg = "white")
        btn_row.pack(pady = 14)
        ttk.Button(
            btn_row,
            text = "Login",
            command = self.check_login
        ).pack()

     def check_login(self):
        username = self.login_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        valid_logins = self.controller.valid_logins

        if username in valid_logins and valid_logins[username] == password:
            messagebox.showinfo("Access Granted", f"Welcome, {username.capitalize()}!")

            overview_page = self.controller.frames[OverviewPage]
            self.controller.username = username #Updates the NAVIGATION with the username of whom logged in

            self.controller.show_frame(OverviewPage) #Switches to the overview frame
        else:
            messagebox.showerror("Access Denied", "Invalid login or password.")
            self.password_entry.delete(0, tk.END)

class OverviewPage(tk.Frame): #OVERVIEW (known as the Welcome Chamber in the menu)
    def __init__(self, parent, controller):
        super().__init__(parent, bg = "white")
        self.controller = controller

        #initializes the NAVIGATION BAR in the overview page
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill = "x", pady = 5)

        #Overview: TITLE Frame
        title_frame = tk.Frame(self, bg = "white")
        title_frame.pack(fill = "x", pady = (10, 20))
        ttk.Label(
            title_frame,
            text = "Overview",
            font = ("Palatino", 42, "bold"),
            background = "white",
        ).pack(anchor="w", padx = 30)

        #Overview: Content Area
        content_frame = tk.Frame(self, bg = "white")
        content_frame.pack(fill = "both", expand = True, padx = 30, pady = 10)
        content_frame.grid_columnconfigure(0, weight = 1)  #chart column: for the chart of past popular orders!
        content_frame.grid_columnconfigure(1, weight = 1)  #text column: giving context of the chart!
        content_frame.grid_rowconfigure(0, weight = 1)

        #Overview: Content Area - Left Side (CHART of past popular orders)
        chart_container = tk.Frame(content_frame, bg = "white", bd = 2, relief = "solid")
        chart_container.grid(row = 0, column = 0, sticky = "nsew", padx = (0, 20))
        self.create_popular_orders_chart(chart_container) #generates the Matplotlib chart
        ttk.Label( #chart title for user context
            chart_container,
            text = "Past Popular Orders",
            font = ("Verdana", 11, "italic"),
            background = "white"
        ).pack(side = "bottom", pady = 8)

        #fetching popular orders for the right side content area (specifically for the body_text section):
        self.storage = controller.model
        order_data = self.storage.fetch_total_orders_by_item_type()
        if order_data:
            order_list = [(row["item_name"], int(row["total_ordered"])) for row in order_data] #converts the sqlite3 row into dict for access

            order_list.sort(key=lambda x: x[1], reverse=True) #Sorts the highest to the lowest most popular past orders

            #Extracts the top 3 most popular orders and bottom least popular order
            top_3 = order_list[:3] #top 3 popular order stored in top_3
            least = order_list[-1] if len(order_list) > 0 else ("None", 0) #least popular order stored in least
        else:
            top_3 = [("No data", 0), ("No data", 0), ("No data", 0)]
            least = ("No data", 0)

        #Overview: Content Area - Right Side (Text regarding past popular orders)
        text_container = tk.Frame(content_frame, bg = "white", bd = 2, relief = "solid")
        text_container.grid(row = 0, column = 1, sticky="nsew")
        ttk.Label( #Subheader
            text_container,
            text = "Apothecary Insights",
            font = ("Verdana", 18, "bold"),
            background = "white",
        ).pack(anchor = "nw", padx = 20, pady = (20, 10))
        body_text = ( #Variable for body text (body_text)
            "Welcome to Calcifer's Ledger, your enchanted inventory and order management system. "
            "This magical ledger organizes the apothecary's stock and tracks incoming orders, "
            "ensuring the castle's operations run smoothly and efficiently.\n\n"
            "The chart on the left displays trends in past orders, highlighting the most requested items. "
            "By visualizing these patterns, castle staff can anticipate demand, optimize inventory, "
            "and maintain appropriate stock levels for upcoming requests.\n\n"
            "Current most popular orders:\n"
            f"1. {top_3[0][0]}\n"
            f"2. {top_3[1][0]}\n"
            f"3. {top_3[2][0]}\n\n"
            "Least popular order:\n"
            f"- {least[0]}"
        )
        ttk.Label( #body text area
            text_container,
            text=body_text,
            font=("Verdana", 11),
            wraplength = 400,
            background = "white",
            justify = "left"
        ).pack(anchor = "nw", padx = 20, pady = (0, 20))

    #Overview: chart functions
    def create_popular_orders_chart(self, container):
        matplotlib.use("Agg")
        # Use the shared storage instead of creating a new one
        storage = self.controller.model

        try:
            order_data = storage.fetch_total_orders_by_item_type()
            if order_data:
                
                order_list = [(row["item_name"], int(row["total_ordered"])) for row in order_data] #Converts the data in rows to (name, total) tuples

                order_list.sort(key=lambda x: x[1], reverse=True) #sorts order_list by descending popularity

                order_list = order_list[:10] #keeps the top ten most popular orders
                items = [name for name, total in order_list]
                counts = [total for name, total in order_list]
            else:
                items = ["No data"]
                counts = [0]
        except Exception as e:
            print("Chart DB Error:", e)
            items = ["No data"]
            counts = [0]

        # plots the bar chart!
        fig = Figure(figsize=(8, 4), dpi=100)  # size of chart
        ax = fig.add_subplot(111)
        # draws each bar
        bars = ax.bar(items, counts, color='skyblue')

        # Chart titles
        ax.set_title("Popular Past Orders")
        ax.set_xlabel("Item Name")
        ax.set_ylabel("Total Orders")
        # Chart subtitles: Item Names
        ax.set_xticks(range(len(items)))  # sets the tick positions
        ax.set_xticklabels(items, rotation=45, ha="right", fontsize=6)

        fig.subplots_adjust(bottom=0.3)  # gives space for the tick labels on the x axis

        # Quantity labels for each bar (displays an exact value for the user)
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # centers the text horizontally ontop of the bar
                height / 2,  # places the text (quantity) in the middle of the bar for visual clarity
                str(count),  # count is the value of quantity
                ha="center",
                va="bottom",
                fontsize=7,
                color="white"
            )

        # embeds the chart in Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()  # draws the canvas
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10,
                                    pady=10)  # packs the canvas widget onto the window

class PotionPantryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.nav_frame = NavigationBar(self, controller)
        #self.nav_frame.configure(bg = "black")
        self.nav_frame.pack(fill="x", pady=5)

        # Application models SQLStorage
        self.storage = controller.model
        self.current_ingredient = None
        self.current_potion = None
        self.order_mode = False
        self.selected_ingredients = []
        self.selected_potions = []

        # Main container with three frames
        main_container = tk.Frame(self, bg="black")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Configure grid weights for distribution
        main_container.columnconfigure(0, weight=1)  # Frame 1
        main_container.columnconfigure(1, weight=500)  # Frame 2
        main_container.columnconfigure(2, weight=1)  # Frame 3
        main_container.rowconfigure(0, weight=1)

        # Frame 1 (LHS) - Ingredients
        self.frame1 = tk.Frame(main_container, bg="lemon chiffon", relief="sunken", bd=2)
        self.frame1.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.create_ingredients_frame()

        # Frame 2 (Middle) - Display area
        self.frame2 = tk.Frame(main_container, bg="black", relief="sunken", bd=2)  
        self.frame2.grid(row=0, column=1, sticky="nsew", padx=5)
        self.create_display_frame()

        # Frame 3 (RHS) - Potions and Info
        self.frame3 = tk.Frame(main_container, bg="light blue", relief="sunken", bd=2)
        self.frame3.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        self.create_potions_frame()

        # Load initial data
        self.load_ingredients_menu()
        self.load_potions_menu()

    def create_ingredients_frame(self):
        """Create Frame 1 - Ingredients scrollable menu"""
        # Title
        title_label = tk.Label(self.frame1, text="Ingredients", font=("Verdana", 14, "bold"),bg="lemon chiffon", fg="medium orchid")
        title_label.pack(pady=10)

        # Scrollable frame for ingredient buttons
        button_container = tk.Frame(self.frame1, bg="lemon chiffon")
        button_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Canvas and scrollbar
        self.ingredient_canvas = tk.Canvas(button_container, bg="lemon chiffon", highlightthickness=0)
        scrollbar = ttk.Scrollbar(button_container, orient="vertical", command=self.ingredient_canvas.yview)
        self.ingredient_button_frame = tk.Frame(self.ingredient_canvas, bg="lemon chiffon")
        self.ingredient_button_frame.bind(
            "<Configure>",
            lambda e: self.ingredient_canvas.configure(scrollregion=self.ingredient_canvas.bbox("all"))
        )
        self.ingredient_canvas.create_window((0, 0), window=self.ingredient_button_frame, anchor="nw")
        self.ingredient_canvas.configure(yscrollcommand=scrollbar.set)

        self.ingredient_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_display_frame(self):
        """Create Frame 2 - Display area for images and order creation"""
        self.display_container = tk.Frame(self.frame2, bg="black")
        self.display_container.pack(fill="both", expand=True)

        # Default display
        self.default_label = tk.Label(self.display_container,
                                      text="Select an ingredient or potion to view details\n\n"
                                           "Select an ingredients' QoH to edit it\n\n"
                                           "Select 'Create Order' button to create an order",
                                      font=("Verdana", 12), bg="black", fg="white")
        self.default_label.pack(expand=True)

        # Image display area ===========================================================================================
        # (initially hidden)
        self.image_display_frame = tk.Frame(self.display_container, bg="black")

        # Image label
        self.ingredient_image_label = tk.Label(self.image_display_frame, bg="black")
        self.ingredient_image_label.pack(expand=True, pady=20)

        # Buttons frame (for ingredient details)
        self.buttons_frame = tk.Frame(self.image_display_frame, bg="black")
        self.buttons_frame.pack(pady=20)

        self.price_button = ttk.Button(self.buttons_frame, text="Price: $0.00", width=15)
        self.price_button.pack(side="left", padx=10, pady=10)

        self.qoh_button = ttk.Button(self.buttons_frame, text="QoH: 0", width=15,
                                     command=self.show_qoh_editor)
        self.qoh_button.pack(side="left", padx=10)

        # Potion display area ==========================================================================================
        self.potion_display_frame = tk.Frame(self.display_container, bg="black")
        # Potion image label
        self.potion_image_label = tk.Label(self.potion_display_frame, bg="black")
        self.potion_image_label.pack(pady=0)
        # Potion effect text
        self.potion_effect_text = tk.Text(self.potion_display_frame, wrap="word", width=40, height=5,
                                          font=("Verdana", 10), bg="black", fg="white",
                                          relief="flat", bd=0,
                                          highlightthickness=0)
        self.potion_effect_text.pack(fill="none", expand=0, pady=(0,0), padx=(50,0), side="left")
        self.potion_effect_text.config(state="disabled")

        # Potion Ingredients text area
        self.potion_ingredients_text = tk.Text(self.potion_display_frame, wrap="word", width=40, height=6,
                                          font=("Verdana", 10), bg="black", fg="white",
                                          relief="flat", bd=0,
                                          highlightthickness=0)
        self.potion_ingredients_text.pack(fill="none", expand=0, pady=(0,0), padx=(0,0), side="right")
        self.potion_ingredients_text.config(state="disabled")

        # Order creation area
        self.order_creation_frame = tk.Frame(self.display_container, bg="black")

        order_title = tk.Label(self.order_creation_frame, text="Create New Order",
                               font=("Verdana", 16, "bold"), bg="black", fg="white")
        order_title.pack(pady=10)

        # Customer name input
        customer_frame = tk.Frame(self.order_creation_frame, bg="black")
        customer_frame.pack(fill="x", pady=10)
        tk.Label(customer_frame, text="Customer Name:", font=("Verdana", 11), bg="black", fg="white").pack(side="left")
        self.customer_entry = ttk.Entry(customer_frame, width=25)
        self.customer_entry.pack(side="left", padx=10)

        # Selected ingredients display
        ing_frame = tk.Frame(self.order_creation_frame, bg="black")
        ing_frame.pack(fill="both", expand=True, pady=10)
        tk.Label(ing_frame, text="Selected Ingredients:", font=("Verdana", 11, "bold"), bg="black", fg="white").pack(
            anchor="w")
        self.ingredients_text = tk.Text(ing_frame, wrap="word", width=40, height=6,
                                        font=("Verdana", 9), bg="black", fg="white", relief="sunken", bd=1)
        self.ingredients_text.pack(fill="both", expand=True, pady=5)
        self.ingredients_text.config(state="disabled")

        # Selected potions display
        pot_frame = tk.Frame(self.order_creation_frame, bg="black")
        pot_frame.pack(fill="both", expand=True, pady=10)
        tk.Label(pot_frame, text="Selected Potions:", font=("Verdana", 11, "bold"), bg="black", fg="white").pack(
            anchor="w")
        self.potions_text = tk.Text(pot_frame, wrap="word", width=40, height=6,
                                    font=("Verdana", 9), bg="black", fg="white", relief="sunken", bd=1)
        self.potions_text.pack(fill="both", expand=True, pady=5)
        self.potions_text.config(state="disabled")

        # Order buttons
        order_buttons = tk.Frame(self.order_creation_frame, bg="black")
        order_buttons.pack(pady=20)
        self.create_order_btn = ttk.Button(order_buttons, text="Create Order",
                                           command=self.create_order)
        self.create_order_btn.pack(side="left", padx=10)
        self.cancel_order_btn = ttk.Button(order_buttons, text="Cancel",
                                           command=self.cancel_order_creation)
        self.cancel_order_btn.pack(side="left", padx=10)

    def create_potions_frame(self):
        """Create Frame 3 - Potions scrollable menu and info"""
        # Title
        title_label = tk.Label(self.frame3, text="Potions", font=("Verdana", 14, "bold"),
                               bg="light blue",fg="navy")
        title_label.pack(pady=10)

        # Scrollable frame for potion buttons
        button_container = tk.Frame(self.frame3, bg="light blue")
        button_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Canvas and scrollbar
        self.potion_canvas = tk.Canvas(button_container, bg="light blue", highlightthickness=0)
        scrollbar = ttk.Scrollbar(button_container, orient="vertical", command=self.potion_canvas.yview)
        self.potion_button_frame = tk.Frame(self.potion_canvas, bg="light blue")

        self.potion_button_frame.bind(
            "<Configure>",
            lambda e: self.potion_canvas.configure(scrollregion=self.potion_canvas.bbox("all"))
        )

        self.potion_canvas.create_window((0, 0), window=self.potion_button_frame, anchor="nw")
        self.potion_canvas.configure(yscrollcommand=scrollbar.set)

        self.potion_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create Order button
        create_order_btn = ttk.Button(self.frame3, text="Create Order",
                                      command=self.start_order_creation)
        create_order_btn.pack(side="bottom", anchor="sw", padx=100, pady=10)

    def load_ingredients_menu(self):
        """Load ingredients into Frame 1"""
        for widget in self.ingredient_button_frame.winfo_children():
            widget.destroy()

        try:
            ingredients = self.storage.get_all_ingredients()
            if not ingredients:
                tk.Label(self.ingredient_button_frame, text="No ingredients", bg="light gray").pack(pady=10)
                return

            for ingredient in ingredients:
                btn = ttk.Button(
                    self.ingredient_button_frame,
                    text=ingredient.name,
                    command=lambda ing=ingredient: self.show_ingredient_details(ing)
                )
                btn.pack(fill="x", pady=5, padx=(20,0))

        except Exception as e:
            print(f"Error loading ingredients: {e}")
            tk.Label(self.ingredient_button_frame, text=f"Error: {str(e)}", bg="light gray").pack(pady=10)

    def load_potions_menu(self):
        """Load potions into Frame 3"""
        for widget in self.potion_button_frame.winfo_children():
            widget.destroy()

        try:
            potions = self.storage.get_all_potions()
            if not potions:
                tk.Label(self.potion_button_frame, text="No potions", bg="light blue").pack(pady=10)
                return

            for potion in potions:
                btn = ttk.Button(
                    self.potion_button_frame,
                    text=potion.name,
                    command=lambda pot=potion: self.show_potion_details(pot)
                )
                btn.pack(fill="x", pady=5, padx=(30,0))

        except Exception as e:
            print(f"Error loading potions: {e}")
            tk.Label(self.potion_button_frame, text=f"Error: {str(e)}", bg="light blue").pack(pady=10)

    def show_ingredient_details(self, ingredient):
        """Show ingredient details in Frame 2"""
        if self.order_mode:
            self.toggle_ingredient_selection(ingredient)
            return

        self.current_ingredient = ingredient
        self.hide_all_displays()
        self.image_display_frame.pack(fill="both", expand=True)

        # Load and display image
        image = self.load_ingredient_image(ingredient.ingredient_id)
        if image:
            self.ingredient_image_label.config(image=image)
            self.ingredient_image_label.image = image  # Keep reference
        else:
            self.ingredient_image_label.config(text=f"Ingredient: {ingredient.name}")

        # Update buttons
        self.price_button.config(text=f"Price: ${ingredient.price:.2f}")
        self.qoh_button.config(text=f"QoH: {ingredient.quantity}")
        self.buttons_frame.pack()

    def show_potion_details(self, potion):
        """Show potion details in Frame 2"""
        if self.order_mode:
            self.toggle_potion_selection(potion)
            return

        self.current_potion = potion
        self.hide_all_displays()
        self.potion_display_frame.pack(fill="both", expand=True)

        # Load and display image
        image = self.load_potion_image(potion.potion_id)
        if image:
            self.potion_image_label.config(image=image)
            self.potion_image_label.image = image  # Keep reference
        else:
            self.potion_image_label.config(text=f"Potion: {potion.name}")

        # Update effect text
        self.potion_effect_text.config(state="normal")
        self.potion_effect_text.delete(1.0, tk.END)
        self.potion_effect_text.insert(1.0, potion.effect)
        self.potion_effect_text.config(state="disabled")

        # Update ingredients text
        self.potion_ingredients_text.config(state="normal")
        self.potion_ingredients_text.delete(1.0, tk.END)

        # Get the ingredients for this potion
        ingredients_list = self.storage.get_potion_ingredients(potion.potion_id)

        if ingredients_list:
            ingredients_text = "Ingredients:\n"
            for ingredient in ingredients_list:
                ingredients_text += f"• {ingredient.name}: {getattr(ingredient, 'quantity_in_recipe', 1)} units\n"
        else:
            ingredients_text = "No ingredients listed for this potion."

        self.potion_ingredients_text.insert(1.0, ingredients_text)
        self.potion_ingredients_text.config(state="disabled")

    def hide_all_displays(self):
        """Hide all display frames"""
        self.default_label.pack_forget()
        self.image_display_frame.pack_forget()
        self.potion_display_frame.pack_forget()
        self.order_creation_frame.pack_forget()
        self.buttons_frame.pack_forget()

    def start_order_creation(self):
        """Start order creation mode"""
        self.order_mode = True
        self.selected_ingredients = []
        self.selected_potions = []
        self.hide_all_displays()
        self.order_creation_frame.pack(fill="both", expand=True)
        self.customer_entry.delete(0, tk.END)
        self.update_selection_displays()

    def cancel_order_creation(self):
        """Cancel order creation and return to normal mode"""
        self.order_mode = False
        self.selected_ingredients = []
        self.selected_potions = []
        self.hide_all_displays()
        self.default_label.pack(expand=True)

    def toggle_ingredient_selection(self, ingredient):
        """Toggle ingredient selection in order mode"""
        if ingredient in self.selected_ingredients:
            self.selected_ingredients.remove(ingredient)
        else:
            self.selected_ingredients.append(ingredient)
        self.update_selection_displays()

    def toggle_potion_selection(self, potion):
        """Toggle potion selection in order mode"""
        if potion in self.selected_potions:
            self.selected_potions.remove(potion)
        else:
            self.selected_potions.append(potion)
        self.update_selection_displays()

    def update_selection_displays(self):
        """Update the selection display text boxes"""
        # Update ingredients text
        self.ingredients_text.config(state="normal")
        self.ingredients_text.delete(1.0, tk.END)
        for ing in self.selected_ingredients:
            self.ingredients_text.insert(tk.END, f"• {ing.name}\n")
        self.ingredients_text.config(state="disabled")

        # Update potions text
        self.potions_text.config(state="normal")
        self.potions_text.delete(1.0, tk.END)
        for pot in self.selected_potions:
            self.potions_text.insert(tk.END, f"• {pot.name}\n")
        self.potions_text.config(state="disabled")

    def create_order(self):
        """Create the order from selections"""
        customer_name = self.customer_entry.get().strip()
        if not customer_name:
            messagebox.showerror("Error", "Please enter a customer name.")
            return

        if not self.selected_ingredients and not self.selected_potions:
            messagebox.showerror("Error", "Please select at least one ingredient or potion.")
            return

        try:
            # Create the order in the database
            self.storage.data_access.execute(
                "INSERT INTO Orders (customer_name, order_status) VALUES (?, ?)",
                (customer_name, 0)  # Status 0 = Requested
            )
            order_id = self.storage.data_access.lastrowid

            # Add selected ingredients to Order_Ingredients
            for ingredient in self.selected_ingredients:
                self.storage.data_access.execute(
                    "INSERT INTO Order_Ingredients (order_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                    (order_id, ingredient.ingredient_id, 1)
                )

            # Add selected potions to Order_Potions
            for potion in self.selected_potions:
                self.storage.data_access.execute(
                    "INSERT INTO Order_Potions (order_id, potion_id, quantity) VALUES (?, ?, ?)",
                    (order_id, potion.potion_id, 1)
                )

            self.storage.conn.commit()

            messagebox.showinfo("Success", f"Order #{order_id} created for {customer_name}!")
            self.cancel_order_creation()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create order: {str(e)}")
            print(f"Order creation error: {e}")

    def show_qoh_editor(self):
        """Show QoH editor"""
        if not self.current_ingredient:
            messagebox.showinfo("Info", "Please select an ingredient first.")
            return

        editor = tk.Toplevel(self)
        editor.title(f"Edit Quantity - {self.current_ingredient.name}")
        editor.geometry("300x200")
        editor.transient(self)
        editor.grab_set()

        main_frame = tk.Frame(editor, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text=f"Update quantity for {self.current_ingredient.name}:",
                 font=("Verdana", 10)).pack(pady=(0, 10))

        entry_frame = tk.Frame(main_frame)
        entry_frame.pack(pady=10)

        qoh_var = tk.StringVar(value=str(self.current_ingredient.quantity))
        qoh_entry = ttk.Entry(entry_frame, textvariable=qoh_var, width=10, font=("Verdana", 10))
        qoh_entry.pack(side="left", padx=(0, 10))
        qoh_entry.select_range(0, tk.END)
        qoh_entry.focus()

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        def save_qoh():
            try:
                new_qoh = int(qoh_var.get().strip())
                if new_qoh < 0:
                    messagebox.showerror("Error", "Quantity cannot be negative.", parent=editor)
                    return

                # Update the ingredient
                self.current_ingredient.quantity = new_qoh
                self.storage.save_ingredient(self.current_ingredient)
                self.show_ingredient_details(self.current_ingredient)
                messagebox.showinfo("Success", f"Updated {self.current_ingredient.name} quantity to {new_qoh}",
                                    parent=editor)
                editor.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for quantity.", parent=editor)

        ttk.Button(button_frame, text="Save", command=save_qoh).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=editor.destroy).pack(side="left", padx=5)

    def load_ingredient_image(self, ingredient_id):
        """Load ingredient image using PIL with black background"""
        try:
            image_path = f"Ingredients/I{ingredient_id}.png"
            image = Image.open(image_path)

            # Convert to RGBA if not already to handle transparency
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Create a black background image
            background = Image.new('RGBA', image.size, (0, 0, 0, 255))

            # Composite the image over the black background
            image_with_bg = Image.alpha_composite(background, image)

            # Convert back to RGB for Tkinter compatibility
            image_with_bg = image_with_bg.convert('RGB')

            image_with_bg = image_with_bg.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_with_bg)
            return photo

        except Exception as e:
            print(f"Error loading image for ingredient {ingredient_id}: {e}")
            # Return a black placeholder
            placeholder = Image.new('RGB', (400, 400), (0, 0, 0))
            photo = ImageTk.PhotoImage(placeholder)
            return photo

    def load_potion_image(self, potion_id):
        """Load potion image using PIL with black background"""
        try:
            image_path = f"potions/P{potion_id}.png"
            image = Image.open(image_path)

            # Convert to RGBA if not already to handle transparency
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Create a black background image
            background = Image.new('RGBA', image.size, (0, 0, 0, 255))

            # Composite the image over the black background
            image_with_bg = Image.alpha_composite(background, image)

            # Convert back to RGB for Tkinter compatibility
            image_with_bg = image_with_bg.convert('RGB')

            image_with_bg = image_with_bg.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_with_bg)
            return photo

        except Exception as e:
            print(f"Error loading image for potion {potion_id}: {e}")
            # Return a black placeholder
            placeholder = Image.new('RGB', (400, 400), (0, 0, 0))
            photo = ImageTk.PhotoImage(placeholder)
            return photo

class RequestScrollsPage(tk.Frame):  # ORDERS
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller

        # Initialize the NAVIGATION BAR
        self.nav_frame = NavigationBar(self, controller)
        self.nav_frame.pack(fill="x", pady=5)
        #self.nav_frame.config(bg="black")

        # Create a storage instance
        self.storage = controller.model

        # Main container
        main_container = tk.Frame(self, bg="black")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== LEFT COLUMN - Status Legend =====
        left_container = tk.Frame(main_container, bg="black")
        left_container.pack(side="left", fill="y", padx=(0, 20))

        # Status Legend Frame
        legend_frame = tk.Frame(left_container, bg="thistle3", relief="raised", bd=2)
        legend_frame.pack(fill="y", pady=(10,10), expand=True)

        ttk.Label(
            legend_frame,
            text="Order Status Legend",
            font=("Verdana", 14, "bold"),
            background="thistle3"
        ).pack(pady=10)

        # Status items
        status_items = [
            ("Requested", "New orders waiting to be processed", "light yellow"),
            ("Ongoing", "Orders being prepared", "sky blue"),
            ("Completed", "Successfully fulfilled orders", "light green"),
        ]

        for status, description, color in status_items:
            status_frame = tk.Frame(legend_frame, bg="thistle3")
            status_frame.pack(fill="x", padx=10, pady=5)

            # Color indicator
            color_label = tk.Label(status_frame, bg=color, width=3, height=1)
            color_label.pack(side="left", padx=(0, 10))

            # Status text
            text_frame = tk.Frame(status_frame, bg="thistle3")
            text_frame.pack(side="left", fill="x", expand=True)

            ttk.Label(
                text_frame,
                text=status,
                font=("Verdana", 10, "bold"),
                background="thistle3"
            ).pack(anchor="w")

            ttk.Label(
                text_frame,
                text=description,
                font=("Verdana", 8),
                background="thistle3"
            ).pack(anchor="w")

        # Add Refresh Button to Legend Frame
        refresh_button = ttk.Button(
            legend_frame,
            text="Refresh Orders",
            command=self.refresh_orders
        )
        refresh_button.pack(pady=10, padx=10, fill="x")

        # RIGHT COLUMN - Order Cards
        right_container = tk.Frame(main_container, bg="black")
        right_container.pack(side="right", fill="both", expand=True)

        # Scrollable frame for order cards
        cards_frame = tk.Frame(right_container, bg="black")
        cards_frame.pack(fill="both", expand=True)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(cards_frame, bg="black", highlightthickness=0)
        scrollbar = ttk.Scrollbar(cards_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="black")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load initial data
        self.load_order_cards()

    def load_order_cards(self):
        """Load all orders as cards"""
        try:
            # Clear existing cards
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Get all orders
            orders = self.storage.get_all_orders()

            if not orders:
                # Display no orders message
                no_orders_label = tk.Label(
                    self.scrollable_frame,
                    text="No orders available",
                    font=("Verdana", 16),
                    bg="black",
                    fg="black"
                )
                no_orders_label.pack(expand=True, pady=50)
                return

            # Create cards in rows of 4
            row_frame = None
            for i, order in enumerate(orders):
                if i % 4 == 0:
                    row_frame = tk.Frame(self.scrollable_frame, bg="black")
                    row_frame.pack(fill="x", pady=10)

                self.create_order_card(row_frame, order)

        except Exception as e:
            print(f"Error loading order cards: {e}")
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def create_order_card(self, parent, order):
        """Create a single order card"""
        # Card frame
        card_frame = tk.Frame(parent, bg="white", relief="raised", bd=2, width=250, height=250)
        card_frame.pack(side="left", fill="both", expand=True, padx=10)
        card_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Set background color based on status
        status_colors = {
            0: "light yellow",  # Requested
            1: "sky blue",  # Ongoing
            2: "light green",  # Completed
            3: "light yellow"  # Cannot Complete
        }
        card_frame.config(bg=status_colors.get(order['order_status'], "white"))

        # Order ID
        order_id_label = tk.Label(
            card_frame,
            text=f"Order #{order['order_id']}",
            font=("Verdana", 12, "bold"),
            bg=status_colors.get(order['order_status'], "white"),
            fg="black"
        )
        order_id_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Customer Name
        customer_label = tk.Label(
            card_frame,
            text=f"{order['customer_name']}",
            font=("Verdana", 10, "bold"),
            bg=status_colors.get(order['order_status'], "white"),
            fg="black"
        )
        customer_label.pack(anchor="w", padx=10, pady=2)

        # Status
        status_text = self.get_status_text(order['order_status'])
        status_label = tk.Label(
            card_frame,
            text=f"Status: {status_text}",
            font=("Verdana", 10, "bold"),
            bg=status_colors.get(order['order_status'], "white"),
            fg="black"
        )
        status_label.pack(anchor="w", padx=10, pady=2)

        # Order Items
        items_frame = tk.Frame(card_frame, bg=status_colors.get(order['order_status'], "white"))
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Get order items and identify insufficient ingredients
        order_items = self.get_order_items_detailed(order['order_id'])
        insufficient_items = self.get_insufficient_items(order['order_id'])

        if order_items:
            # Create a text widget
            items_text = tk.Text(
                items_frame,
                wrap="word",
                width=25,
                height=6,
                font=("Verdana", 8),
                bg=status_colors.get(order['order_status'], "white"),
                fg="black",
                relief="flat",
                bd=0,
                highlightthickness=0
            )
            items_text.pack(anchor="w", fill="both", expand=True)

            # Insert items with styling for insufficient ones
            items_text.config(state="normal")
            for item in order_items:
                if item.strip():  # Skip empty lines
                    # Check if this item is insufficient
                    is_insufficient = any(insuff_item in item for insuff_item in insufficient_items)

                    if is_insufficient:
                        # Configure tag for insufficient items
                        items_text.tag_configure("insufficient", foreground="red", font=("Verdana", 8, "bold"))
                        items_text.insert(tk.END, item + "\n", "insufficient")
                    else:
                        items_text.insert(tk.END, item + "\n")

            items_text.config(state="disabled")
        else:
            items_label = tk.Label(
                items_frame,
                text="No items",
                font=("Verdana", 8),
                bg=status_colors.get(order['order_status'], "white"),
                justify="left",
                wraplength=250,
                fg="black"
            )
            items_label.pack(anchor="w")

        # Missing ingredients (for status 3)
        if order['order_status'] == 3:
            missing_ingredients = self.get_missing_ingredients(order['order_id'])
            if missing_ingredients:
                missing_text = f"Missing: {', '.join(missing_ingredients)}"

                missing_label = tk.Label(
                    items_frame,
                    text=missing_text,
                    font=("Verdana", 7, "bold"),
                    bg=status_colors.get(order['order_status'], "white"),
                    fg="red4",
                    justify="left",
                    wraplength=250
                )
                missing_label.pack(anchor="w", pady=(5, 0))

        # Action Button
        button_frame = tk.Frame(card_frame, bg=status_colors.get(order['order_status'], "white"))
        button_frame.pack(fill="x", padx=10, pady=10)

        action_button = self.create_action_button(button_frame, order)
        action_button.pack(fill="x")

    def get_order_items_detailed(self, order_id):
        """Get detailed order items using model methods with quantities"""
        items = []

        # Get ingredients (Apothecary orders)
        try:
            ingredients = self.storage.get_order_ingredients(order_id)
            for ingredient in ingredients:
                qty = getattr(ingredient, 'order_quantity', 1)
                item_text = f"{qty}x {ingredient.name}"
                items.append(item_text)
        except Exception as e:
            print(f"Error getting order ingredients for order {order_id}: {e}")

        items.append("\n")

        # Get potions (Brewery orders)
        try:
            potions = self.storage.get_order_potions(order_id)
            for potion in potions:
                qty = getattr(potion, 'order_quantity', 1)
                item_text = f"{qty}x {potion.name}"
                items.append(item_text)
        except Exception as e:
            print(f"Error getting order potions for order {order_id}: {e}")

        return items

    def get_status_text(self, order_status):
        """Get human-readable status text"""
        status_map = {
            0: "Requested",
            1: "Ongoing",
            2: "Completed",
            3: "Cannot Complete"
        }
        return status_map.get(order_status, "Unknown")

    def get_missing_ingredients(self, order_id):
        """Get list of missing ingredients for an order with quantities needed"""
        missing = []
        try:
            # Check potion ingredients
            potions = self.storage.get_order_potions(order_id)
            for potion in potions:
                ingredients = self.storage.get_potion_ingredients(potion.potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * getattr(potion, 'order_quantity', 1)
                    if ingredient.quantity < required_qty:
                        missing.append(f"{ingredient.name} (need {required_qty})")

            # Check direct ingredient orders
            ingredients = self.storage.get_order_ingredients(order_id)
            for ingredient in ingredients:
                order_qty = getattr(ingredient, 'order_quantity', 1)
                if ingredient.quantity < order_qty:
                    missing.append(f"{ingredient.name} (need {order_qty})")

        except Exception as e:
            print(f"Error getting missing ingredients: {e}")

        return missing

    def create_action_button(self, parent, order):
        """Create appropriate action button based on order status"""
        order_id = order['order_id']
        status = order['order_status']

        if status == 0:  # Requested
            button = ttk.Button(
                parent,
                text="ACCEPT ORDER",
                command=lambda: self.process_order(order_id)
            )
            return button

        elif status == 1:  # Ongoing
            # Check if we can complete
            can_complete = self.check_order_feasibility(order_id)
            if can_complete:
                button = ttk.Button(
                    parent,
                    text="COMPLETE ORDER",
                    command=lambda: self.complete_order(order_id)
                )
                return button
            else:
                button = ttk.Button(
                    parent,
                    text="INSUFFICIENT INGREDIENTS",
                    state="disabled"
                )
                return button

        elif status == 2:  # Completed
            button = ttk.Button(
                parent,
                text="NO ACTION REQUIRED",
                state="disabled"
            )
            return button

        elif status == 3:  # Cannot Complete
            missing_ingredients = self.get_missing_ingredients(order_id)
            if missing_ingredients:
                button_text = f"ORDER MORE {missing_ingredients[0]}"
            else:
                button_text = "INSUFFICIENT INGREDIENTS"

            button = ttk.Button(
                parent,
                text=button_text,
                state="disabled"
            )
            return button

        # Default fallback
        return ttk.Button(parent, text="UNKNOWN STATUS", state="disabled")

    def process_order(self, order_id):
        """Process a requested order (move from status 0 to 1 or 3)"""
        try:
            # Check if we have sufficient ingredients for ALL items in the order
            can_complete = self.check_order_feasibility(order_id)

            # Also check if there are any ingredients directly in the order
            if can_complete:
                # Check direct ingredient orders too
                ingredients = self.storage.get_order_ingredients(order_id)
                for ingredient in ingredients:
                    order_qty = getattr(ingredient, 'order_quantity', 1)
                    if ingredient.quantity < order_qty:
                        can_complete = False
                        break

            # Update order status
            new_status = 1 if can_complete else 3  # Ongoing or Cannot Complete
            self.storage.data_access.execute(
                "UPDATE Orders SET order_status = ? WHERE order_id = ?",
                (new_status, order_id)
            )
            self.storage.conn.commit()

            # If we can complete, update ingredient quantities for both potions and direct ingredients
            if can_complete:
                self.update_ingredient_quantities(order_id)

            # Show confirmation
            status_msg = "Order processed successfully!" if can_complete else "Order processed but cannot be completed due to insufficient ingredients"
            messagebox.showinfo("Order Processed", status_msg)

            # Reload cards
            self.load_order_cards()

        except Exception as e:
            print(f"Error processing order {order_id}: {e}")
            messagebox.showerror("Error", f"Failed to process order: {str(e)}")

    def complete_order(self, order_id):
        """Complete an ongoing order (move from status 1 to 2)"""
        try:
            # Update order status to complete
            self.storage.data_access.execute(
                "UPDATE Orders SET order_status = 2 WHERE order_id = ?",
                (order_id,)
            )
            self.storage.conn.commit()

            messagebox.showinfo("Order Completed", f"Order #{order_id} has been completed!")

            # Reload cards
            self.load_order_cards()

        except Exception as e:
            print(f"Error completing order {order_id}: {e}")
            messagebox.showerror("Error", f"Failed to complete order: {str(e)}")

    def check_order_feasibility(self, order_id):
        """Check if an order can be completed based on available ingredients"""
        try:
            # Check potions in the order
            potions = self.storage.get_order_potions(order_id)
            for potion in potions:
                ingredients = self.storage.get_potion_ingredients(potion.potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * getattr(potion, 'order_quantity', 1)
                    if ingredient.quantity < required_qty:
                        return False

            # Check direct ingredients in the order
            ingredients = self.storage.get_order_ingredients(order_id)
            for ingredient in ingredients:
                order_qty = getattr(ingredient, 'order_quantity', 1)
                if ingredient.quantity < order_qty:
                    return False

            return True

        except Exception as e:
            print(f"Error checking order feasibility: {e}")
            return False

    def update_ingredient_quantities(self, order_id):
        """Update ingredient quantities when an order is processed"""
        try:
            # Update quantities for potion ingredients
            potions = self.storage.get_order_potions(order_id)
            for potion in potions:
                ingredients = self.storage.get_potion_ingredients(potion.potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * getattr(potion, 'order_quantity', 1)
                    new_qty = ingredient.quantity - required_qty
                    if new_qty < 0:
                        new_qty = 0

                    self.storage.data_access.execute(
                        "UPDATE Apothecary SET ingredient_qoh = ? WHERE ingredient_id = ?",
                        (new_qty, ingredient.ingredient_id)
                    )

            # Update quantities for direct ingredient orders
            ingredients = self.storage.get_order_ingredients(order_id)
            for ingredient in ingredients:
                order_qty = getattr(ingredient, 'order_quantity', 1)
                new_qty = ingredient.quantity - order_qty
                if new_qty < 0:
                    new_qty = 0

                self.storage.data_access.execute(
                    "UPDATE Apothecary SET ingredient_qoh = ? WHERE ingredient_id = ?",
                    (new_qty, ingredient.ingredient_id)
                )

            self.storage.conn.commit()

        except Exception as e:
            print(f"Error updating ingredient quantities: {e}")
            self.storage.conn.rollback()

    def get_insufficient_items(self, order_id):
        """Get list of item names that are insufficient for this order"""
        insufficient_items = []
        try:
            # Check potion ingredients
            potions = self.storage.get_order_potions(order_id)
            for potion in potions:
                ingredients = self.storage.get_potion_ingredients(potion.potion_id)
                for ingredient in ingredients:
                    required_qty = getattr(ingredient, 'quantity_in_recipe', 1) * getattr(potion, 'order_quantity', 1)
                    if ingredient.quantity < required_qty:
                        insufficient_items.append(ingredient.name)

            # Check direct ingredient orders
            ingredients = self.storage.get_order_ingredients(order_id)
            for ingredient in ingredients:
                order_qty = getattr(ingredient, 'order_quantity', 1)
                if ingredient.quantity < order_qty:
                    insufficient_items.append(ingredient.name)

        except Exception as e:
            print(f"Error getting insufficient items: {e}")

        return insufficient_items

    def refresh_orders(self):
        """Safe refresh using shared database connection"""
        try:
            # reload the cards - the shared storage should have latest data
            self.load_order_cards()
            messagebox.showinfo("Success", "Orders refreshed with latest data!")
        except Exception as e:
            print(f"Refresh error: {e}")
            # Try to reconnect if there's a connection issue
            try:
                # If the connection was closed, get a new one from controller
                self.storage = self.controller.model
                self.load_order_cards()
                messagebox.showinfo("Success", "Orders refreshed with latest data!")
            except Exception as e2:
                print(f"Reconnect also failed: {e2}")
                messagebox.showerror("Error", "Could not refresh orders. Please try navigating away and back.")

if __name__ == '__main__':
    root = tk.Tk()
    configure_style(root)
    app = CalcifersLedgerApp(root)
    root.mainloop()