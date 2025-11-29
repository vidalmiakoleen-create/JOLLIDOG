import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error

# -------------------- DATABASE CONFIG --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "jollidog_system"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror("DB Error", f"Could not connect: {e}")
        return None

# -------------------- DATABASE INITIALIZATION --------------------
def initialize_database():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(100) UNIQUE NOT NULL,
                quantity INT NOT NULL DEFAULT 0,
                price DECIMAL(10,2) NOT NULL DEFAULT 0.00
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM admin_accounts")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admin_accounts (username, password) VALUES (%s, %s)", ("admin", "password123"))
        cursor.execute("SELECT COUNT(*) FROM stock_items")
        if cursor.fetchone()[0] == 0:
            default_items = [
                ("Regular Jollidog", 50, 25.00),
                ("Medium Jollidog", 50, 30.00),
                ("Large Jollidog", 40, 35.00),
                ("Cheesy Jollidog", 30, 40.00),
                ("Twin Jollidog", 20, 50.00),
                ("Spicy Jollidog", 25, 35.00),
                ("Extra Spicy Jollidog", 20, 40.00),
                ("Super Spicy Jollidog", 15, 45.00),
                ("Long Jollidog", 10, 50.00),
                ("Coke", 80, 15.00),
                ("Coke Zero", 70, 15.00),
                ("Sprite", 60, 15.00),
                ("Royal", 50, 15.00),
                ("Ice Tea", 40, 20.00),
                ("Iced Coffee", 30, 25.00)
            ]
            cursor.executemany("INSERT INTO stock_items (item_name, quantity, price) VALUES (%s, %s, %s)", default_items)
        conn.commit()
        cursor.close()
        conn.close()

# -------------------- DATABASE FUNCTIONS --------------------
def fetch_admin_accounts():
    accounts = {}
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM admin_accounts")
        for u, p in cursor.fetchall():
            accounts[u] = p
        cursor.close()
        conn.close()
    return accounts

def fetch_stock_items():
    items = {}
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity, price FROM stock_items")
        for n, q, p in cursor.fetchall():
            items[n] = {'quantity': q, 'price': float(p)}
        cursor.close()
        conn.close()
    return items

def update_stock_item(item_name, qty):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE stock_items SET quantity=%s WHERE item_name=%s", (qty, item_name))
            conn.commit()
        except Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to update stock: {e}")
        finally:
            cursor.close()
            conn.close()

def update_item_price(item_name, price):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE stock_items SET price=%s WHERE item_name=%s", (price, item_name))
            conn.commit()
        except Error as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to update price: {e}")
        finally:
            cursor.close()
            conn.close()

# -------------------- UI HELPERS --------------------
def create_header(window, title):
    frame = tk.Frame(window, bg="#292929", height=80)
    frame.pack(fill="x", padx=10, pady=10)
    frame.pack_propagate(False)
    tk.Label(frame, text=title, font=("Arial", 20, "bold"), bg="#292929", fg="white").pack(expand=True)
    return frame

def create_button(parent, text, command, bg="#292929", fg="white", height=2):
    return tk.Button(parent, text=text, font=("Arial", 12, "bold"), bg=bg, fg=fg, height=height, command=command)

# -------------------- MAIN WINDOW --------------------
def create_main_window():
    root = tk.Tk()
    root.title("Jollidog Management System")
    root.geometry("900x650")
    root.configure(bg="#FFF0B9")
    root.minsize(800, 600)

    create_header(root, "JOLLIDOG MANAGEMENT SYSTEM")
    tk.Label(root, text="Welcome to Jollidog Management System", font=("Arial", 18), bg="#FFF0B9").pack(pady=20)
    tk.Label(root, text="Manage your food business efficiently", font=("Arial", 12), bg="#FFF0B9").pack(pady=10)

    btn_frame = tk.Frame(root, bg="#FFF0B9")
    btn_frame.pack(pady=30)

    def open_admin_login():
        root.destroy()
        admin_login_page()

    create_button(btn_frame, "Admin Login", open_admin_login).pack(pady=10, ipadx=10, ipady=5)
    create_button(btn_frame, "Exit System", root.quit, bg="#666666").pack(pady=5, ipadx=10, ipady=5)

    return root

# -------------------- ADMIN LOGIN --------------------
def admin_login_page():
    win = tk.Tk()
    win.title("Admin Login")
    win.geometry("800x600")
    win.configure(bg="#FFF0B9")
    win.minsize(700, 500)

    create_header(win, "ADMIN LOGIN")

    # ----- MAIN FRAME -----
    frame = tk.Frame(win, bg="#FFF0B9")
    frame.pack(pady=50)

    # ----- USERNAME -----
    tk.Label(frame, text="Username:", font=("Arial", 12), bg="#FFF0B9")\
        .grid(row=0, column=0, sticky="e", padx=5, pady=5)

    user_entry = tk.Entry(frame, font=("Arial", 12))
    user_entry.grid(row=0, column=1, padx=5, pady=5)

    # ----- PASSWORD -----
    tk.Label(frame, text="Password:", font=("Arial", 12), bg="#FFF0B9")\
        .grid(row=1, column=0, sticky="e", padx=5, pady=5)

    pass_entry = tk.Entry(frame, font=("Arial", 12), show="*")
    pass_entry.grid(row=1, column=1, padx=5, pady=5)

    # ----- PASSWORD TOGGLE -----
    def toggle_password():
        if pass_entry.cget("show") == "*":
            pass_entry.config(show="")
            show_pass_btn.config(text="Hide")
        else:
            pass_entry.config(show="*")
            show_pass_btn.config(text="Show")

    show_pass_btn = tk.Button(
        frame, text="Show", command=toggle_password,
        width=5, font=("Arial", 10)
    )
    show_pass_btn.grid(row=1, column=2, padx=5)

    # ----- LOGIN FUNCTION -----
    def login_now():
        accounts = fetch_admin_accounts()
        u, p = user_entry.get().strip(), pass_entry.get().strip()

        if not u or not p:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if u in accounts and accounts[u] == p:
            messagebox.showinfo("Success", "Admin Login Successful")
            win.destroy()
            admin_stock_page()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    # Press ENTER to login
    user_entry.bind("<Return>", lambda e: login_now())
    pass_entry.bind("<Return>", lambda e: login_now())

    # ----- BUTTONS -----
    create_button(win, "Login", login_now).pack(pady=10, ipadx=10, ipady=5)
    create_button(win, "Exit", win.destroy, bg="#666666").pack(pady=5, ipadx=10, ipady=5)

    user_entry.focus()
    win.mainloop()

# -------------------- ADMIN STOCK PAGE --------------------
def admin_stock_page():
    win = tk.Tk()
    win.title("Stock Management System")
    win.geometry("1200x700")
    win.configure(bg="#FFF0B9")
    win.minsize(1000, 600)

    create_header(win, "STOCK MANAGEMENT SYSTEM")
    stock_items = fetch_stock_items()

    food_items = [
        "Regular Jollidog", "Medium Jollidog", "Large Jollidog",
        "Cheesy Jollidog", "Twin Jollidog", "Spicy Jollidog",
        "Extra Spicy Jollidog", "Super Spicy Jollidog", "Long Jollidog"
    ]
    drink_items = [
        "Coke", "Coke Zero", "Sprite", "Royal",
        "Ice Tea", "Iced Coffee"
    ]
    display_order = food_items + drink_items

    columns = ("Item", "Quantity", "Price")
    stock_tree = ttk.Treeview(win, columns=columns, show="headings")
    for col in columns:
        stock_tree.heading(col, text=col)
        stock_tree.column(col, width=300, anchor="center")
    stock_tree.pack(fill="both", expand=True, pady=20)

    def update_stock_display():
        stock_tree.delete(*stock_tree.get_children())
        for name in display_order:
            data = stock_items.get(name, {'quantity': 0, 'price': 0.00})
            stock_tree.insert("", "end", values=(name, data['quantity'], f"₱{data['price']:.2f}"))
    update_stock_display()

    selected_var = tk.StringVar(value="No item selected")
    tk.Label(win, textvariable=selected_var, bg="#FFF0B9").pack(pady=5)

    def on_select(event):
        sel = stock_tree.selection()
        if sel:
            item_name = stock_tree.item(sel[0])['values'][0]
            selected_var.set(f"Selected: {item_name}")
        else:
            selected_var.set("No item selected")
    stock_tree.bind("<<TreeviewSelect>>", on_select)

    ctrl_frame = tk.Frame(win, bg="#FFF0B9")
    ctrl_frame.pack(pady=10)

    def modify_stock(amount):
        sel = stock_tree.selection()
        if not sel:
            messagebox.showwarning("Error", "Select an item first.")
            return
        name = stock_tree.item(sel[0])['values'][0]
        qty = stock_items.get(name, {'quantity': 0})['quantity'] + amount
        if qty < 0:
            messagebox.showwarning("Error", "Quantity cannot be negative.")
            return
        update_stock_item(name, qty)
        stock_items[name] = {'quantity': qty, 'price': stock_items.get(name, {'price': 0.00})['price']}
        update_stock_display()

    def bulk_update():
        sel = stock_tree.selection()
        if not sel:
            messagebox.showwarning("Error", "Select an item first.")
            return
        name = stock_tree.item(sel[0])['values'][0]
        current_qty = stock_items.get(name, {'quantity': 0})['quantity']
        current_price = stock_items.get(name, {'price': 0.00})['price']

        bulk_win = tk.Toplevel(win)
        bulk_win.title("Bulk Update")
        bulk_win.geometry("350x250")
        bulk_win.configure(bg="#FFF0B9")
        bulk_win.transient(win)
        bulk_win.grab_set()

        tk.Label(bulk_win, text=f"Update: {name}", bg="#FFF0B9").pack(pady=10)
        tk.Label(bulk_win, text="New Quantity:", bg="#FFF0B9").pack()
        qty_entry = tk.Entry(bulk_win)
        qty_entry.insert(0, str(current_qty))
        qty_entry.pack(pady=5)
        tk.Label(bulk_win, text="New Price:", bg="#FFF0B9").pack()
        price_entry = tk.Entry(bulk_win)
        price_entry.insert(0, str(current_price))
        price_entry.pack(pady=5)

        def apply_update():
            try:
                new_qty = int(qty_entry.get())
                new_price = float(price_entry.get())
                if new_qty < 0 or new_price < 0:
                    messagebox.showwarning("Error", "Quantity and Price must be non-negative.")
                    return
                update_stock_item(name, new_qty)
                update_item_price(name, new_price)
                stock_items[name] = {'quantity': new_qty, 'price': new_price}
                update_stock_display()
                bulk_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers.")

        tk.Button(bulk_win, text="Apply", bg="#4CAF50", fg="white", command=apply_update).pack(pady=10)

    create_button(ctrl_frame, "➖ Remove 1", lambda: modify_stock(-1), bg="#292929").pack(side="left", padx=5)
    create_button(ctrl_frame, "➕ Add 1", lambda: modify_stock(1), bg="#292929").pack(side="left", padx=5)
    create_button(ctrl_frame, "📊 Bulk Update", bulk_update, bg="#292929").pack(side="left", padx=5)

    # -------------------- Back to Main Button --------------------
    def back_to_main():
        win.destroy()
        main_root = create_main_window()
        main_root.mainloop()

    create_button(win, "Back to Main", back_to_main, bg="#555555").pack(pady=10, ipadx=10, ipady=5)

    win.mainloop()


# -------------------- RUN APPLICATION --------------------
if __name__ == "__main__":
    initialize_database()
    root = create_main_window()
    root.mainloop()
