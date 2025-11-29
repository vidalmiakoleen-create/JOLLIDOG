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

# -------------------- ADMIN DB FUNCTIONS --------------------
def fetch_admin_accounts():
    conn = get_db_connection()
    accounts = {}
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM admin_accounts")
        for u, p in cursor.fetchall():
            accounts[u] = p
        cursor.close()
        conn.close()
    return accounts

def add_admin_account(username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO admin_accounts (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
        except:
            conn.rollback()
        cursor.close()
        conn.close()

# -------------------- STOCK DB FUNCTIONS --------------------
def fetch_stock_items():
    conn = get_db_connection()
    items = {}
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity, price FROM stock_items ORDER BY item_name")
        for n, q, p in cursor.fetchall():
            items[n] = {'quantity': q, 'price': p}
        cursor.close()
        conn.close()
    return items

def update_stock_item(item_name, qty):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE stock_items SET quantity=%s WHERE item_name=%s", (qty, item_name))
        conn.commit()
        cursor.close()
        conn.close()

def update_item_price(item_name, price):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE stock_items SET price=%s WHERE item_name=%s", (price, item_name))
        conn.commit()
        cursor.close()
        conn.close()

# -------------------- STOCK INITIALIZATION --------------------
def initialize_stock_items():
    """Initialize stock items with the new product list"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Check if stock_items table is empty
        cursor.execute("SELECT COUNT(*) FROM stock_items")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert new products
            default_items = [
                ('1. Regular Jollidog', 100, 40.00),
                ('2. Medium Jollidog', 100, 50.00),
                ('3. Large Jollidog', 100, 60.00),
                ('4. Cheesy Jollidog', 100, 55.00),
                ('5. Twin Jollidog', 100, 75.00),
                ('6. Spicy Jollidog', 100, 50.00),
                ('6.1 Extra Spicy Jollidog', 100, 55.00),
                ('6.2 Super Spicy Jollidog', 100, 60.00),
                ('7. Long Jollidog', 100, 65.00),
                ('8. Coke', 100, 30.00),
                ('8.1 Coke Zero', 100, 30.00),
                ('8.2 Sprite', 100, 30.00),
                ('8.3 Royal', 100, 30.00),
                ('8.4 Iced Tea', 100, 25.00),
                ('8.5 Iced Coffee', 100, 35.00),
                ('8.6 Bottled Water', 100, 20.00)
            ]
            
            cursor.executemany(
                "INSERT INTO stock_items (item_name, quantity, price) VALUES (%s, %s, %s)",
                default_items
            )
            conn.commit()
        
        cursor.close()
        conn.close()

# -------------------- SMOOTH TRANSITIONS --------------------
def clear_window(win):
    """Clear all widgets from window"""
    for widget in win.winfo_children():
        widget.destroy()

def create_header(win, title):
    """Create consistent header"""
    header_frame = tk.Frame(win, bg="#292929", height=80)
    header_frame.pack(fill=tk.X, padx=20, pady=10)
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=title, 
                          font=("Arial", 20, "bold"), bg="#292929", fg="white")
    title_label.pack(expand=True)
    
    return header_frame

def create_footer(win):
    """Create consistent footer"""
    footer_frame = tk.Frame(win, bg="#FFE66D", height=40)
    footer_frame.pack(fill=tk.X, padx=20, pady=5)
    footer_frame.pack_propagate(False)
    
    footer_label = tk.Label(footer_frame, 
                           text="© 2023 Jollidog Management System. All rights reserved.",
                           font=("Arial", 10), 
                           bg="#FFE66D")
    footer_label.pack(expand=True)
    
    return footer_frame

# -------------------- ADMIN LOGIN PAGE --------------------
def admin_login_page():
    win = tk.Toplevel()
    win.title("Admin Login")
    win.geometry("600x500")
    win.configure(bg="#FFF0B9")
    win.resizable(False, False)
    
    # Center the window
    win.transient(root)
    win.grab_set()
    
    create_header(win, "ADMIN LOGIN")
    
    # Main content
    content_frame = tk.Frame(win, bg="#FFF0B9")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=30)
    
    # Welcome section
    welcome_frame = tk.Frame(content_frame, bg="#FFF0B9")
    welcome_frame.pack(pady=20)
    
    tk.Label(welcome_frame, text="🔐 Admin Authentication", 
             font=("Arial", 16, "bold"), bg="#FFF0B9").pack(pady=5)
    tk.Label(welcome_frame, text="Enter your credentials to access the admin panel",
             font=("Arial", 12), bg="#FFF0B9").pack()
    
    # Login form
    form_frame = tk.Frame(content_frame, bg="#FFF0B9")
    form_frame.pack(pady=30)
    
    # Username
    tk.Label(form_frame, text="Username:", font=("Arial", 12, "bold"), 
             bg="#FFF0B9").grid(row=0, column=0, sticky="e", padx=10, pady=15)
    user_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
    user_entry.grid(row=0, column=1, pady=15, padx=10)
    user_entry.focus()  # Auto-focus on username field
    
    # Password
    tk.Label(form_frame, text="Password:", font=("Arial", 12, "bold"), 
             bg="#FFF0B9").grid(row=1, column=0, sticky="e", padx=10, pady=15)
    pass_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, show="•")
    pass_entry.grid(row=1, column=1, pady=15, padx=10)
    
    # Bind Enter key to login
    def on_enter_key(event):
        login_now()
    
    user_entry.bind('<Return>', on_enter_key)
    pass_entry.bind('<Return>', on_enter_key)
    
    # Login function
    def login_now():
        accounts = fetch_admin_accounts()
        u = user_entry.get().strip()
        p = pass_entry.get().strip()
        
        if not u or not p:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        if u in accounts and accounts[u] == p:
            messagebox.showinfo("Success", "Admin Login Successful!")
            win.destroy()
            admin_stock_page()
        else:
            messagebox.showerror("Error", "Invalid username or password.")
            pass_entry.delete(0, tk.END)
            pass_entry.focus()

    # Buttons frame
    buttons_frame = tk.Frame(content_frame, bg="#FFF0B9")
    buttons_frame.pack(pady=20)
    
    # Login button
    login_btn = tk.Button(buttons_frame, 
                          text="Login", 
                          font=("Arial", 12, "bold"),
                          bg="#292929", 
                          fg="white",
                          width=15,
                          height=1,
                          command=login_now)
    login_btn.pack(pady=10)
    
    # Back button
    back_btn = tk.Button(buttons_frame, 
                         text="Back to Main", 
                         font=("Arial", 12),
                         bg="#666666", 
                         fg="white",
                         width=15,
                         height=1,
                         command=win.destroy)
    back_btn.pack(pady=5)
    
    create_footer(win)

# -------------------- ENHANCED ADMIN STOCK PAGE --------------------
def admin_stock_page():
    win = tk.Toplevel()
    win.title("Stock Management System")
    win.geometry("1200x700")
    win.configure(bg="#FFF0B9")
    
    # Center the window
    win.transient(root)
    win.grab_set()
    
    create_header(win, "STOCK MANAGEMENT SYSTEM")
    
    # Main content area
    main_frame = tk.Frame(win, bg="#FFF0B9")
    main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
    
    # Control buttons frame
    control_frame = tk.Frame(main_frame, bg="#FFF0B9")
    control_frame.pack(fill=tk.X, pady=10)
    
    def refresh_stock():
        nonlocal stock_items
        stock_items = fetch_stock_items()
        update_stock_display()
    
    refresh_btn = tk.Button(control_frame, 
                           text="🔄 Refresh", 
                           font=("Arial", 10, "bold"),
                           bg="#4CAF50", 
                           fg="white",
                           command=refresh_stock)
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    # Stock display frame with scrollbar
    display_frame = tk.Frame(main_frame, bg="#FFF0B9")
    display_frame.pack(expand=True, fill=tk.BOTH)
    
    # Create treeview for better display
    tree_frame = tk.Frame(display_frame, bg="#FFF0B9")
    tree_frame.pack(expand=True, fill=tk.BOTH)
    
    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
    
    # Create treeview
    stock_tree = ttk.Treeview(tree_frame, 
                             columns=("Item", "Quantity", "Price"), 
                             show="headings",
                             yscrollcommand=v_scrollbar.set,
                             xscrollcommand=h_scrollbar.set)
    
    # Configure columns
    stock_tree.heading("Item", text="Menu Item")
    stock_tree.heading("Quantity", text="Stock Quantity")
    stock_tree.heading("Price", text="Price (₱)")
    
    stock_tree.column("Item", width=400, anchor="w")
    stock_tree.column("Quantity", width=150, anchor="center")
    stock_tree.column("Price", width=150, anchor="center")
    
    v_scrollbar.config(command=stock_tree.yview)
    h_scrollbar.config(command=stock_tree.xview)
    
    # Pack treeview and scrollbars
    stock_tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    # Stock control frame
    control_detail_frame = tk.Frame(main_frame, bg="#FFF0B9")
    control_detail_frame.pack(fill=tk.X, pady=10)
    
    # Selected item info
    selected_item = tk.StringVar()
    selected_item.set("No item selected")
    
    info_label = tk.Label(control_detail_frame, 
                         textvariable=selected_item, 
                         font=("Arial", 11, "bold"), 
                         bg="#FFF0B9",
                         fg="#292929")
    info_label.pack(pady=5)
    
    # Quantity control frame
    qty_frame = tk.Frame(control_detail_frame, bg="#FFF0B9")
    qty_frame.pack(pady=10)
    
    def update_selected_item(event):
        selection = stock_tree.selection()
        if selection:
            item = stock_tree.item(selection[0])
            item_name = item['values'][0]
            selected_item.set(f"Selected: {item_name}")
    
    stock_tree.bind('<<TreeviewSelect>>', update_selected_item)
    
    def modify_stock(amount):
        selection = stock_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an item first.")
            return
            
        item = stock_tree.item(selection[0])
        item_name = item['values'][0]
        current_qty = stock_items[item_name]['quantity']
        
        new_qty = current_qty + amount
        if new_qty < 0:
            messagebox.showwarning("Stock Error", "Quantity cannot be negative.")
            return
            
        update_stock_item(item_name, new_qty)
        refresh_stock()
        messagebox.showinfo("Success", f"Updated {item_name}\nNew quantity: {new_qty}")
    
    def bulk_update():
        selection = stock_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select an item first.")
            return
            
        item = stock_tree.item(selection[0])
        item_name = item['values'][0]
        
        # Create bulk update window
        bulk_win = tk.Toplevel(win)
        bulk_win.title("Bulk Update")
        bulk_win.geometry("300x200")
        bulk_win.configure(bg="#FFF0B9")
        bulk_win.transient(win)
        bulk_win.grab_set()
        
        tk.Label(bulk_win, text=f"Update: {item_name}", 
                font=("Arial", 12, "bold"), bg="#FFF0B9").pack(pady=10)
        
        tk.Label(bulk_win, text="New Quantity:", font=("Arial", 10), bg="#FFF0B9").pack()
        qty_entry = tk.Entry(bulk_win, font=("Arial", 12), width=10)
        qty_entry.pack(pady=5)
        qty_entry.focus()
        
        tk.Label(bulk_win, text="New Price:", font=("Arial", 10), bg="#FFF0B9").pack()
        price_entry = tk.Entry(bulk_win, font=("Arial", 12), width=10)
        price_entry.pack(pady=5)
        
        def apply_bulk_update():
            try:
                new_qty = int(qty_entry.get())
                new_price = float(price_entry.get())
                
                if new_qty < 0:
                    messagebox.showwarning("Input Error", "Quantity cannot be negative.")
                    return
                    
                update_stock_item(item_name, new_qty)
                update_item_price(item_name, new_price)
                bulk_win.destroy()
                refresh_stock()
                messagebox.showinfo("Success", f"Updated {item_name}\nQuantity: {new_qty}\nPrice: ₱{new_price:.2f}")
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers.")
        
        tk.Button(bulk_win, text="Apply", bg="#4CAF50", fg="white",
                 command=apply_bulk_update).pack(pady=10)
    
    # Control buttons
    tk.Button(qty_frame, text="➖ Remove 1", font=("Arial", 10),
             bg="#f44336", fg="white", width=12,
             command=lambda: modify_stock(-1)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(qty_frame, text="➕ Add 1", font=("Arial", 10),
             bg="#4CAF50", fg="white", width=12,
             command=lambda: modify_stock(1)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(qty_frame, text="📊 Bulk Update", font=("Arial", 10),
             bg="#2196F3", fg="white", width=12,
             command=bulk_update).pack(side=tk.LEFT, padx=5)
    
    # Bottom buttons
    bottom_frame = tk.Frame(main_frame, bg="#FFF0B9")
    bottom_frame.pack(fill=tk.X, pady=10)
    
    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            win.destroy()
    
    logout_btn = tk.Button(bottom_frame, 
                          text="🚪 Logout", 
                          font=("Arial", 11, "bold"),
                          bg="#666666", 
                          fg="white",
                          width=15,
                          command=logout)
    logout_btn.pack(pady=10)
    
    # Initialize stock data
    stock_items = fetch_stock_items()
    
    def update_stock_display():
        # Clear existing items
        for item in stock_tree.get_children():
            stock_tree.delete(item)
        
        # Add items to treeview
        for item_name, data in sorted(stock_items.items()):
            stock_tree.insert("", "end", values=(
                item_name, 
                data['quantity'], 
                f"₱{data['price']:.2f}"
            ))
    
    update_stock_display()
    create_footer(win)

# -------------------- MAIN WINDOW --------------------
def create_main_window():
    global root
    root = tk.Tk()
    root.title("Jollidog Management System")
    root.geometry("19000x1200")
    root.configure(bg="#FFF0B9")
    root.resizable(False, False)
    
    # Center the window on screen
    root.eval('tk::PlaceWindow . center')
    
    create_header(root, "JOLLIDOG MANAGEMENT SYSTEM")
    
    # Main content
    content_frame = tk.Frame(root, bg="#FFF0B9")
    content_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=40)
    
    # Welcome section
    welcome_frame = tk.Frame(content_frame, bg="#FFF0B9")
    welcome_frame.pack(pady=30)
    
    # Logo/Icon placeholder
    icon_label = tk.Label(welcome_frame, text="🌭", font=("Arial", 48), bg="#FFF0B9")
    icon_label.pack(pady=10)
    
    tk.Label(welcome_frame, 
             text="Welcome to Jollidog Management System",
             font=("Arial", 20, "bold"), 
             bg="#FFF0B9").pack(pady=10)
    
    tk.Label(welcome_frame, 
             text="Streamline your hotdog business operations with our comprehensive management solution",
             font=("Arial", 12), 
             bg="#FFF0B9",
             wraplength=500).pack(pady=10)
    
    # Buttons frame
    buttons_frame = tk.Frame(content_frame, bg="#FFF0B9")
    buttons_frame.pack(pady=40)
    
    # Admin button
    admin_btn = tk.Button(buttons_frame, 
                          text="Admin Login", 
                          font=("Arial", 14, "bold"),
                          bg="#292929", 
                          fg="white",
                          width=20,
                          height=2,
                          command=admin_login_page)
    admin_btn.pack(pady=15)
    
    # Customer ordering system button
    customer_btn = tk.Button(buttons_frame, 
                             text="🛒 Customer Ordering", 
                             font=("Arial", 14, "bold"),
                             bg="#D4AF37", 
                             fg="white",
                             width=20,
                             height=2,
                             command=lambda: messagebox.showinfo("Info", "Customer ordering system would open here"))
    customer_btn.pack(pady=15)
    
    # Exit button
    exit_btn = tk.Button(buttons_frame, 
                         text="❌ Exit System", 
                         font=("Arial", 12),
                         bg="#666666", 
                         fg="white",
                         width=15,
                         height=1,
                         command=root.quit)
    exit_btn.pack(pady=10)
    
    create_footer(root)
    
    return root

# -------------------- APPLICATION START --------------------
if __name__ == "__main__":
    # Initialize database tables if needed
    initialize_stock_items()
    
    # Create and run the main window
    app = create_main_window()
    app.mainloop()