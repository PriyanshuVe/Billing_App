from dotenv import load_dotenv 
import os  # Import os to use environment variables
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem
)
import mysql.connector

# Load environment variables from the .env file
load_dotenv()

# === Database Layer ===
class Database:
    def __init__(self):
        # Retrieve database credentials from the environment variables
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),  # Default to localhost if not set
            user=os.getenv("DB_USER", "root"),  # Default to root if not set
            password=os.getenv("DB_PASSWORD", ""),  # Default to empty if not set
            database=os.getenv("DB_NAME", "billing_app")  # Default to billing_app if not set
        )

    def insert_customer(self, name, address, contact):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO customers (name, address, contact_info) VALUES (%s, %s, %s)",
            (name, address, contact)
        )
        self.connection.commit()
        customer_id = cursor.lastrowid
        cursor.close()
        return customer_id

    def insert_bill(self, customer_id, date, total):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO bills (customer_id, date, total_amount) VALUES (%s, %s, %s)",
            (customer_id, date, total)
        )
        self.connection.commit()
        bill_id = cursor.lastrowid
        cursor.close()
        return bill_id

    def insert_bill_item(self, bill_id, item_name, quantity, price):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO bill_items (bill_id, item_name, quantity, price) VALUES (%s, %s, %s, %s)",
            (bill_id, item_name, quantity, price)
        )
        self.connection.commit()
        cursor.close()

    def get_customers(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, address, contact_info FROM customers")
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_bills(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT bills.id, customers.name, bills.date, bills.total_amount
            FROM bills
            JOIN customers ON bills.customer_id = customers.id
        """)
        data = cursor.fetchall()
        cursor.close()
        return data


# === GUI Layer ===
class BillingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Billing Application")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # Input Fields
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.contact_input = QLineEdit()

        layout.addWidget(QLabel("Customer Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)
        layout.addWidget(QLabel("Contact Info:"))
        layout.addWidget(self.contact_input)

        self.save_customer_btn = QPushButton("Save Customer")
        self.save_customer_btn.clicked.connect(self.save_customer)
        layout.addWidget(self.save_customer_btn)

        # Load Customers Button
        self.load_customers_btn = QPushButton("Load Customers")
        self.load_customers_btn.clicked.connect(self.load_customers)
        layout.addWidget(self.load_customers_btn)

        self.customer_table = QTableWidget()
        layout.addWidget(self.customer_table)

        # Load Bills Button
        self.load_bills_btn = QPushButton("Load Bills")
        self.load_bills_btn.clicked.connect(self.load_bills)
        layout.addWidget(self.load_bills_btn)

        self.bill_table = QTableWidget()
        layout.addWidget(self.bill_table)

        main_widget.setLayout(layout)

    def save_customer(self):
        name = self.name_input.text()
        address = self.address_input.text()
        contact = self.contact_input.text()
        if name and address and contact:
            customer_id = self.db.insert_customer(name, address, contact)
            QMessageBox.information(self, "Success", f"Customer saved with ID: {customer_id}")
            self.name_input.clear()
            self.address_input.clear()
            self.contact_input.clear()
        else:
            QMessageBox.warning(self, "Input Error", "All fields must be filled!")

    def load_customers(self):
        data = self.db.get_customers()
        self.customer_table.setRowCount(len(data))
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Address", "Contact"])
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.customer_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def load_bills(self):
        data = self.db.get_bills()
        self.bill_table.setRowCount(len(data))
        self.bill_table.setColumnCount(4)
        self.bill_table.setHorizontalHeaderLabels(["Bill ID", "Customer", "Date", "Total"])
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.bill_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())
