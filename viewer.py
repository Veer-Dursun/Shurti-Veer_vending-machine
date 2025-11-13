import os
import sys
import shutil
import django
import requests
import io
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from django.db import models
from django.utils import timezone

# --- Configuration ---
API_BASE_URL = "https://shurti-veer-vending-machine.onrender.com/api/"
USE_API = True  # True = use deployed API; False = use local Django ORM

# --- (Optional) Local Django ORM Setup — only if USE_API = False ---
if not USE_API:
    BASE_DIR = r"C:\Users\User\Desktop\TkinterDBViewer\my_django_project"
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_project.settings")
    django.setup()
    from my_app.models import Student, Product, AmountInserted, ChangeReturn, Order
else:
    # For USE_API = True, no local ORM usage
    Student = Product = AmountInserted = ChangeReturn = Order = None

# --- Table Configurations ---
TABLES = {
    "Student": Student,
    "Product": Product,
    "AmountInserted": AmountInserted,
    "ChangeReturn": ChangeReturn,
    "Order": Order
}

CRUD_TABLES = ["Student", "Product"]

VISIBLE_FIELDS = {
    "Student": ['id', 'name', 'campus', 'join_in'],
    "Product": ['product_id', 'name', 'category', 'qty', 'price', 'image'],
    "AmountInserted": ['student', 'date_time', 'total_amount', 'notes_200', 'notes_100', 'notes_50', 'notes_25', 'coins_20', 'coins_10', 'coins_5', 'coins_1'],
    "ChangeReturn": ['student', 'date_time', 'total_return', 'notes_200', 'notes_100', 'notes_50', 'notes_25', 'coins_20', 'coins_10', 'coins_5', 'coins_1'],
    "Order": ['student', 'product', 'date_time', 'amount_inserted', 'balance', 'total_purchase']
}

# --- Media directory (for local mode) ---
if not USE_API:
    MEDIA_DIR = os.path.join(BASE_DIR, "products", "products")
    os.makedirs(MEDIA_DIR, exist_ok=True)

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Vending Machine Database")
        self.root.geometry("1200x600")

        # Ribbon
        self.ribbon = Frame(root, bg='darkblue', height=50)
        self.ribbon.pack(side=TOP, fill=X)
        Label(self.ribbon, text="Vending Machine Database", bg='darkblue', fg='white', font=("Arial", 16)).pack(pady=10)

        self.refresh_btn = Button(self.ribbon, text="Refresh", command=self.load_table)
        self.refresh_btn.pack(side=LEFT, padx=5, pady=5)

        self.table_var = StringVar()
        self.table_var.set("Select Table")
        self.table_menu = ttk.OptionMenu(self.ribbon, self.table_var, "Select Table", *TABLES.keys(), command=self.on_table_change)
        self.table_menu.pack(side=LEFT, padx=5, pady=5)

        self.table_label = Label(self.ribbon, text="", bg='darkblue', fg="white", font=("Arial", 16, "bold"))
        self.table_label.place(relx=0.5, rely=0.7, anchor=CENTER)

        # Treeview frame
        self.tree_frame = Frame(root)
        self.tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.tree = None
        self.v_scrollbar = None
        self.h_scrollbar = None

        # CRUD frame
        self.crud_frame = Frame(root)
        self.crud_frame.pack(pady=8)
        self.add_btn = Button(self.crud_frame, text="Add", command=self.add_record)
        self.edit_btn = Button(self.crud_frame, text="Edit", command=self.edit_record)
        self.delete_btn = Button(self.crud_frame, text="Delete", command=self.delete_record)

    def on_table_change(self, value):
        self.load_table()

    def load_table(self):
        table_name = self.table_var.get()
        if table_name not in TABLES:
            return
        self.table_label.config(text=f"{table_name}")
        model = TABLES[table_name]

        # destroy old treeview & scrollbars
        if self.tree:
            self.tree.destroy()
        if self.v_scrollbar:
            self.v_scrollbar.destroy()
        if self.h_scrollbar:
            self.h_scrollbar.destroy()

        columns = VISIBLE_FIELDS[table_name]
        self.v_scrollbar = Scrollbar(self.tree_frame, orient=VERTICAL)
        self.h_scrollbar = Scrollbar(self.tree_frame, orient=HORIZONTAL)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        self.v_scrollbar.config(command=self.tree.yview)
        self.h_scrollbar.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=CENTER)

        # Load data
        if USE_API:
            api_endpoint = table_name.lower() + "s"  # pluralized
            url = f"{API_BASE_URL}{api_endpoint}/"
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                data_list = resp.json()
                for obj in data_list:
                    values = [obj.get(field, "") for field in columns]
                    self.tree.insert("", "end", values=values)
            except Exception as e:
                messagebox.showerror("API Error", f"Failed to fetch {table_name} data:\n{e}")
        else:
            for obj in model.objects.all():
                values = []
                for field in columns:
                    val = getattr(obj, field)
                    if isinstance(val, models.Model):
                        val = str(val)
                    elif isinstance(val, timezone.datetime):
                        val = timezone.localtime(val).strftime("%Y-%m-%d %H:%M:%S")
                    elif field == "image" and val:
                        val = os.path.basename(str(val))
                    values.append(val)
                self.tree.insert("", "end", values=values)

        # Show/hide CRUD buttons
        if table_name in CRUD_TABLES:
            self.add_btn.pack(side=LEFT, padx=10)
            self.edit_btn.pack(side=LEFT, padx=10)
            self.delete_btn.pack(side=LEFT, padx=10)
        else:
            self.add_btn.pack_forget()
            self.edit_btn.pack_forget()
            self.delete_btn.pack_forget()

    def add_record(self):
        table_name = self.table_var.get()
        if table_name == "Student":
            self.add_student()
        elif table_name == "Product":
            self.add_product()

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a record to edit")
            return
        table_name = self.table_var.get()
        item = self.tree.item(selected[0])
        record_values = item['values']
        if table_name == "Student":
            self.edit_student(record_values)
        elif table_name == "Product":
            self.edit_product(record_values)

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a record to delete")
            return
        table_name = self.table_var.get()
        record_values = self.tree.item(selected[0])['values']
        record_id = record_values[0]

        if USE_API:
            api_endpoint = table_name.lower() + "s"
            url = f"{API_BASE_URL}{api_endpoint}/{record_id}/"
            try:
                resp = requests.delete(url)
                if resp.status_code in (200, 204):
                    messagebox.showinfo("Deleted", "Record deleted successfully")
                    self.load_table()
                else:
                    messagebox.showerror("Error", f"Delete failed: {resp.status_code} {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            model = TABLES[table_name]
            if table_name == "Student":
                obj = model.objects.get(pk=record_id)
            else:
                obj = model.objects.get(product_id=str(record_id))
            obj.delete()
            self.load_table()

    # --- Student CRUD ---
    def add_student(self):
        top = Toplevel(self.root)
        top.title("Add Student")

        Label(top, text="ID").grid(row=0, column=0)
        id_entry = Entry(top); id_entry.grid(row=0, column=1)

        Label(top, text="Name").grid(row=1, column=0)
        name_entry = Entry(top); name_entry.grid(row=1, column=1)

        Label(top, text="Campus").grid(row=2, column=0)
        campus_var = StringVar(value="Ebene")
        ttk.OptionMenu(top, campus_var, "Ebene", "Ebene", "Reduit").grid(row=2, column=1)

        def save():
            data = {
                "id": id_entry.get(),
                "name": name_entry.get(),
                "campus": campus_var.get(),
                "join_in": timezone.now().isoformat()
            }
            try:
                if USE_API:
                    resp = requests.post(f"{API_BASE_URL}students/", json=data)
                    resp.raise_for_status()
                else:
                    Student.objects.create(**data)
                top.destroy()
                self.load_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(top, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=5)

    def edit_student(self, record_values):
        top = Toplevel(self.root)
        top.title("Edit Student")

        student_id = record_values[0]
        if USE_API:
            try:
                resp = requests.get(f"{API_BASE_URL}students/{student_id}/")
                resp.raise_for_status()
                student = resp.json()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            student = Student.objects.get(pk=student_id)

        Label(top, text="ID").grid(row=0, column=0)
        id_entry = Entry(top); id_entry.grid(row=0, column=1)
        id_entry.insert(0, student["id"] if USE_API else student.id)
        id_entry.config(state='readonly')

        Label(top, text="Name").grid(row=1, column=0)
        name_entry = Entry(top); name_entry.grid(row=1, column=1)
        name_entry.insert(0, student["name"] if USE_API else student.name)

        Label(top, text="Campus").grid(row=2, column=0)
        campus_var = StringVar(value=student["campus"] if USE_API else student.campus)
        ttk.OptionMenu(top, campus_var, campus_var.get(), "Ebene", "Reduit").grid(row=2, column=1)

        def save():
            data = {
                "name": name_entry.get(),
                "campus": campus_var.get()
            }
            try:
                if USE_API:
                    resp = requests.put(f"{API_BASE_URL}students/{student_id}/", json=data)
                    resp.raise_for_status()
                else:
                    obj = Student.objects.get(pk=student_id)
                    obj.name = data["name"]
                    obj.campus = data["campus"]
                    obj.save()
                top.destroy()
                self.load_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(top, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=5)

    # --- Product CRUD ---
    def add_product(self):
        top = Toplevel(self.root)
        top.title("Add Product")

        Label(top, text="Product ID").grid(row=0, column=0)
        pid_entry = Entry(top); pid_entry.grid(row=0, column=1)

        Label(top, text="Name").grid(row=1, column=0)
        name_entry = Entry(top); name_entry.grid(row=1, column=1)

        Label(top, text="Qty").grid(row=2, column=0)
        qty_entry = Entry(top); qty_entry.grid(row=2, column=1)

        Label(top, text="Price").grid(row=3, column=0)
        price_entry = Entry(top); price_entry.grid(row=3, column=1)

        Label(top, text="Category").grid(row=4, column=0)
        cat_var = StringVar(value="Cake")
        ttk.OptionMenu(top, cat_var, "Cake", "Cake", "Soft Drink").grid(row=4, column=1)

        Label(top, text="Image").grid(row=5, column=0)
        image_var = StringVar()
        Entry(top, textvariable=image_var, state='readonly').grid(row=5, column=1)
        Button(top, text="Browse", command=lambda: image_var.set(filedialog.askopenfilename())).grid(row=5, column=2)

        def save():
            try:
                src = image_var.get()
                if src and not USE_API:
                    dest = os.path.join(MEDIA_DIR, os.path.basename(src))
                    shutil.copy(src, dest)
                    img_path = f"products/{os.path.basename(src)}"
                else:
                    img_path = os.path.basename(src) if src else None

                data = {
                    "product_id": pid_entry.get(),
                    "name": name_entry.get(),
                    "qty": int(qty_entry.get()),
                    "price": float(price_entry.get()),
                    "category": cat_var.get(),
                    "image": img_path
                }

                if USE_API:
                    resp = requests.post(f"{API_BASE_URL}products/", json=data)
                    resp.raise_for_status()
                else:
                    Product.objects.create(**data)

                top.destroy()
                self.load_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(top, text="Save", command=save).grid(row=6, column=0, columnspan=3, pady=5)

    def edit_product(self, record_values):
        top = Toplevel(self.root)
        top.title("Edit Product")

        product_id = record_values[0]
        if USE_API:
            try:
                resp = requests.get(f"{API_BASE_URL}products/{product_id}/")
                resp.raise_for_status()
                product = resp.json()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            product = Product.objects.get(product_id=product_id)

        Label(top, text="Product ID").grid(row=0, column=0)
        pid_entry = Entry(top); pid_entry.grid(row=0, column=1)
        pid_entry.insert(0, product["product_id"] if USE_API else product.product_id)
        pid_entry.config(state='readonly')

        Label(top, text="Name").grid(row=1, column=0)
        name_entry = Entry(top); name_entry.grid(row=1, column=1)
        name_entry.insert(0, product["name"] if USE_API else product.name)

        Label(top, text="Qty").grid(row=2, column=0)
        qty_entry = Entry(top); qty_entry.grid(row=2, column=1)
        qty_entry.insert(0, product["qty"] if USE_API else product.qty)

        Label(top, text="Price").grid(row=3, column=0)
        price_entry = Entry(top); price_entry.grid(row=3, column=1)
        price_entry.insert(0, product["price"] if USE_API else product.price)

        Label(top, text="Category").grid(row=4, column=0)
        cat_var = StringVar(value=product["category"] if USE_API else product.category)
        ttk.OptionMenu(top, cat_var, cat_var.get(), "Cake", "Soft Drink").grid(row=4, column=1)

        Label(top, text="Image").grid(row=5, column=0)
        image_var = StringVar(value=product.get("image") if USE_API else (product.image.path if product.image else ""))
        Entry(top, textvariable=image_var, state='readonly').grid(row=5, column=1)
        Button(top, text="Browse", command=lambda: image_var.set(filedialog.askopenfilename())).grid(row=5, column=2)

        def save():
            try:
                src = image_var.get()
                if USE_API:
                    img_path = src if src.startswith("products/") else os.path.basename(src) if src else None
                else:
                    if src:
                        dest = os.path.join(MEDIA_DIR, os.path.basename(src))
                        shutil.copy(src, dest)
                        img_path = f"products/{os.path.basename(src)}"
                    else:
                        img_path = product.get("image") if USE_API else (product.image if product.image else None)

                data = {
                    "name": name_entry.get(),
                    "qty": int(qty_entry.get()),
                    "price": float(price_entry.get()),
                    "category": cat_var.get(),
                    "image": img_path
                }

                if USE_API:
                    resp = requests.put(f"{API_BASE_URL}products/{product_id}/", json=data)
                    resp.raise_for_status()
                else:
                    obj = Product.objects.get(product_id=product_id)
                    obj.name = data["name"]
                    obj.qty = data["qty"]
                    obj.price = data["price"]
                    obj.category = data["category"]
                    obj.image = img_path
                    obj.save()

                top.destroy()
                self.load_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(top, text="Save", command=save).grid(row=6, column=0, columnspan=3, pady=5)


# --- Main ---
if __name__ == "__main__":
    root = Tk()
    app = DatabaseViewer(root)
    root.mainloop()
