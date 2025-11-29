import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import sys
import os

def close_all():
    sys.exit()

# -------------------- DATABASE CONNECTION --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "jollidog_system"
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect: {e}")
        return None

# -------------------- STOCK FUNCTIONS --------------------
def fetch_menu_items():
    """Fetch all available menu items with prices from stock_items"""
    conn = get_db_connection()
    menu_items = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, price FROM stock_items WHERE quantity > 0 ORDER BY item_name")
        for name, price in cursor.fetchall():
            menu_items.append((name, float(price)))
        cursor.close()
        conn.close()
    return menu_items

def deduct_stock(item_name, qty):
    """ Deduct stock from DB. Returns True if successful, False if not enough stock. """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE stock_items SET quantity = quantity - %s WHERE item_name = %s AND quantity >= %s",
            (qty, item_name, qty)
        )
        conn.commit()
        success = cursor.rowcount > 0
        cursor.close()
        conn.close()
        return success
    return False

def restore_stock(item_name, qty):
    """ Restore stock if the user cancels an order. """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE stock_items SET quantity = quantity + %s WHERE item_name = %s",
            (qty, item_name)
        )
        conn.commit()
        cursor.close()
        conn.close()

# -------------------- ORDER LIST DB FUNCTIONS --------------------
def add_order_to_db(username, item_name, quantity, price):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO order_list (username, item_name, quantity, price) VALUES (%s, %s, %s, %s)",
                (username, item_name, quantity, price)
            )
            conn.commit()
        except mysql.connector.Error as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Could not add order: {e}")
        finally:
            cursor.close()
            conn.close()

# -------------------- LINKED LIST CLASSES --------------------
class Order:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.next = None
        self.prev = None

class OrderList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.total = 0.0

    def add_order(self, name, price, quantity):
        new_order = Order(name, price, quantity)
        new_order.prev = self.tail
        if not self.head:
            self.head = self.tail = new_order
        else:
            self.tail.next = new_order
            self.tail = new_order
        self.total += price * quantity

    def cancel_order(self, index):
        temp = self.head
        count = 1
        while temp and count < index:
            temp = temp.next
            count += 1
        if not temp:
            return None
        self.total -= temp.price * temp.quantity
        removed_item = (temp.name, temp.quantity)
        if temp.prev:
            temp.prev.next = temp.next
        if temp.next:
            temp.next.prev = temp.prev
        if temp == self.head:
            self.head = temp.next
        if temp == self.tail:
            self.tail = temp.prev
        return removed_item

    def get_orders(self):
        items = []
        temp = self.head
        while temp:
            items.append((temp.name, temp.quantity, temp.price * temp.quantity))
            temp = temp.next
        return items

    def clear(self):
        self.head = None
        self.tail = None
        self.total = 0.0

# -------------------- MENU REFERENCE --------------------
FOODS = [
    "Regular Jollidog",
    "Medium Jollidog",
    "Large Jollidog",
    "Cheesy Jollidog",
    "Twin Jollidog",
    "Spicy Jollidog",
    "Extra Spicy Jollidog",
    "Super Spicy Jollidog",
    "Long Jollidog"
]

DRINKS = [
    "Coke",
    "Coke Zero",
    "Sprite",
    "Royal",
    "Ice Tea",
    "Iced Coffee"
]

# -------------------- GUI --------------------
class JollidogGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        root.title("Jollidog Ordering System")
        root.geometry("1920x1080")
        root.configure(bg="#292929")

        self.order_list = OrderList()
        self.menu_items = fetch_menu_items()

        self.create_widgets()
        self.refresh_menu()
        self.refresh_list()

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#292929")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left frame for menu
        menu_frame = tk.Frame(main_frame, bg="#292929")
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(menu_frame, text="Jollidog Menu", font=("Arial", 30, "bold"), 
                bg="#292929", fg="white").pack(pady=(0,10))
        
        # Menu list with scrollbar
        list_frame = tk.Frame(menu_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.menu_list = tk.Listbox(list_frame, bg="#FFFFFF", height=20, width=50, font=("Arial", 20))
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.menu_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.menu_list.yview)
        
        self.menu_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Refresh button
        refresh_btn = tk.Button(menu_frame, text="Refresh Menu", font=("Arial", 15), 
                                command=self.refresh_menu, bg="#3A3A3A", fg="white")
        refresh_btn.pack(pady=5)

        # Quantity and Add Order
        qty_frame = tk.Frame(menu_frame, bg="#3A3A3A")
        qty_frame.pack(pady=10)
        tk.Label(qty_frame, text="Quantity:", bg="#3A3A3A", fg="white", font=("Arial", 22)).pack(side=tk.LEFT)
        self.qty_entry = tk.Spinbox(qty_frame, from_=1, to=1000, width=8, font=("Arial", 20))
        self.qty_entry.pack(side=tk.LEFT, padx=10)
        add_btn = tk.Button(menu_frame, text="Add Order", fg="white", bg="black", font=("Arial", 18), command=self.add_order)
        add_btn.pack(pady=10)

        # Right frame for orders
        receipt_frame = tk.Frame(main_frame, bg="#969696", relief=tk.RAISED, bd=2)
        receipt_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20,0))

        tk.Label(receipt_frame, text="Current Orders", bg="#969696", font=("Arial", 30, "bold")).pack(pady=10)
        
        # Treeview
        tree_frame = tk.Frame(receipt_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        self.tree = ttk.Treeview(tree_frame, columns=("name", "qty", "total"), show="headings", height=12)
        self.tree.heading("name", text="Order Name")
        self.tree.heading("qty", text="Quantity")
        self.tree.heading("total", text="Total Price")
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        btn_frame = tk.Frame(receipt_frame, bg="#969696")
        btn_frame.pack(pady=10)
        cancel_btn = tk.Button(btn_frame, text="Cancel Selected", font=("Arial", 15), command=self.cancel_order, bg="#3A3A3A", fg="white")
        cancel_btn.pack(side=tk.LEFT, padx=5)
        print_btn = tk.Button(btn_frame, text="View Receipt", font=("Arial", 15), command=self.print_receipt, bg="#3A3A3A", fg="white")
        print_btn.pack(side=tk.LEFT, padx=5)
        back_btn = tk.Button(btn_frame, text="Back to Main", font=("Arial", 15), command=self.back_to_main, bg="#3A3A3A", fg="white")
        back_btn.pack(side=tk.LEFT, padx=5)

        self.total_label = tk.Label(receipt_frame, text="Total: ₱0.00", font=("Arial", 20, "bold"), bg="#969696")
        self.total_label.pack(pady=10)

    def refresh_menu(self):
        """Refresh the menu items and display without category labels"""
        self.menu_list.delete(0, tk.END)
        self.menu_items = fetch_menu_items()
        
        if not self.menu_items:
            self.menu_list.insert(tk.END, "No items available in stock")
            return

        # Sort: foods first, then drinks
        sorted_items = []
        for food in FOODS:
            for name, price in self.menu_items:
                if name == food:
                    sorted_items.append((name, price))
        for drink in DRINKS:
            for name, price in self.menu_items:
                if name == drink:
                    sorted_items.append((name, price))
        self.menu_items = sorted_items

        # Insert items with color
        for idx, (name, price) in enumerate(self.menu_items):
            self.menu_list.insert(tk.END, f"{name} - ₱{price:.2f}")
            if name in FOODS:
                self.menu_list.itemconfig(idx, fg="black")
            elif name in DRINKS:
                self.menu_list.itemconfig(idx, fg="black")

    def refresh_list(self):
        """Refresh the order list Treeview"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        orders = self.order_list.get_orders()
        for category in [FOODS, DRINKS]:
            for name, qty, total in orders:
                if name in category:
                    self.tree.insert("", tk.END, values=(name, qty, f"₱{total:.2f}"))

        self.total_label.config(text=f"Total: ₱{self.order_list.total:.2f}")

    def add_order(self):
        selection = self.menu_list.curselection()
        if not selection:
            messagebox.showwarning("Error", "Please select an item.")
            return
        index = selection[0]
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                messagebox.showwarning("Error", "Quantity must be at least 1.")
                return
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid quantity.")
            return

        if not self.menu_items:
            messagebox.showwarning("Error", "No items available.")
            return
            
        name, price = self.menu_items[index]
        if not deduct_stock(name, qty):
            messagebox.showerror("Out of Stock", f"Not enough stock for {name}!")
            return

        self.order_list.add_order(name, price, qty)
        self.refresh_list()
        add_order_to_db(self.username, name, qty, price)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")
        self.refresh_menu()

    def cancel_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select an item to cancel.")
            return
        index = self.tree.index(selected[0]) + 1
        removed_item = self.order_list.cancel_order(index)
        if removed_item:
            name, qty = removed_item
            restore_stock(name, qty)
            self.refresh_menu()
        self.refresh_list()

    def print_receipt(self):
        orders = self.order_list.get_orders()
        if not orders:
            messagebox.showinfo("Receipt", "No items ordered.")
            return

        receipt_win = tk.Toplevel(self.root)
        receipt_win.title("Receipt")
        receipt_win.geometry("400x500")
        receipt_win.configure(bg="white")

        receipt_text = tk.Text(receipt_win, width=45, height=25, font=("Courier", 10))
        receipt_text.pack(pady=10, padx=10)

        receipt = " " * 10 + "JOLLIDOG RECEIPT\n"
        receipt += "=" * 50 + "\n"
        receipt += f"Customer: {self.username}\n"
        receipt += "=" * 50 + "\n"
        for name, qty, total in orders:
            receipt += f"{name:<25} Qty: {qty:>2} ₱{total:>7.2f}\n"
        receipt += "=" * 50 + "\n"
        receipt += f"{'TOTAL:':<30} ₱{self.order_list.total:>7.2f}\n"
        receipt += "=" * 50 + "\n"
        receipt += " " * 8 + "Thank you for ordering!\n"
        receipt += " " * 5 + "Please come again!\n"

        receipt_text.insert(tk.END, receipt)
        receipt_text.config(state="disabled")
        self.order_list.clear()
        self.refresh_list()
        tk.Button(receipt_win, text="Close", width=15, command=receipt_win.destroy, 
                 bg="#3A3A3A", fg="white").pack(pady=10)

    def back_to_main(self):
        """Return to the main login window"""
        self.root.destroy()
        os.system("python jollidog_login.py")

# -------------------- LAUNCH --------------------
def ordering_system(username):
    root = tk.Tk()
    app = JollidogGUI(root, username)
    root.mainloop()

if __name__ == "__main__":
    ordering_system("customer123")
