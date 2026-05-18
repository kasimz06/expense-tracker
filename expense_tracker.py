import sys, json, os
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)

DATA_FILE = os.path.expanduser("~/.simple_expense_data.json")
CATEGORIES = ["Food", "Transport", "Shopping", "Utilities", "Housing", "Entertainment", "Other"]
MONTHS = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
YEARS = [str(y) for y in range(datetime.now().year - 20, datetime.now().year + 11)]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2)

class SimpleTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expenses = load_data()
        self.setWindowTitle("Expense Tracker")
        self.resize(750, 550)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top Section: Dropdowns and Totals
        filter_layout = QHBoxLayout()
        
        self.year_filter = QComboBox()
        self.year_filter.addItems(YEARS)
        self.year_filter.setCurrentText(str(datetime.now().year))
        self.year_filter.currentIndexChanged.connect(self.refresh)
        
        self.month_filter = QComboBox()
        self.month_filter.addItems(MONTHS)
        self.month_filter.setCurrentIndex(datetime.now().month - 1)
        self.month_filter.currentIndexChanged.connect(self.refresh)
        
        self.month_total_label = QLabel()
        self.month_total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: black;")
        
        self.year_total_label = QLabel()
        self.year_total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: black; margin-left: 15px;")
        
        filter_layout.addWidget(QLabel("Year:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("Month:"))
        filter_layout.addWidget(self.month_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.month_total_label)
        filter_layout.addWidget(self.year_total_label)
        main_layout.addLayout(filter_layout)

        # Input Fields Form
        form_layout = QHBoxLayout()
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description")
        self.desc_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.category_box = QComboBox()
        self.category_box.addItems(CATEGORIES)
        self.category_box.setLineEdit(QLineEdit())
        self.category_box.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.category_box.lineEdit().setReadOnly(True)
        
        add_button = QPushButton("Add Expense")
        add_button.clicked.connect(self.add_expense)
        
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.category_box)
        form_layout.addWidget(add_button)
        main_layout.addLayout(form_layout)

        # Table Section
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Category", "Amount"])
        
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.table)

        # Delete Action
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_expense)
        main_layout.addWidget(delete_button)

        self.refresh()

    def add_expense(self):
        desc = self.desc_input.text()
        amount_text = self.amount_input.text()
        category = self.category_box.currentText()
        
        # FIX: Get the year and month from your dropdown selectors instead of forcing today's date
        selected_year = self.year_filter.currentText()
        selected_month_num = self.month_filter.currentIndex() + 1
        current_day = datetime.now().strftime("%d") # Keeps the current day number
        
        date_str = f"{selected_year}-{selected_month_num:02d}-{current_day}"

        if not desc or not amount_text: return

        try:
            self.expenses.append({
                "date": date_str,
                "description": desc,
                "category": category,
                "amount": float(amount_text)
            })
            save_data(self.expenses)
            self.desc_input.clear()
            self.amount_input.clear()
            self.refresh()
        except ValueError:
            pass

    def delete_expense(self):
        current_row = self.table.currentRow()
        if current_row < 0: return

        original_idx = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        self.expenses.pop(original_idx)
        save_data(self.expenses)
        self.refresh()

    def refresh(self):
        selected_year = self.year_filter.currentText()
        selected_month_num = self.month_filter.currentIndex() + 1
        
        year_prefix = f"{selected_year}-"
        month_prefix = f"{selected_year}-{selected_month_num:02d}"
        
        monthly_total = 0.0
        yearly_total = 0.0
        self.table.setRowCount(0)
        
        for idx, exp in enumerate(self.expenses):
            if exp["date"].startswith(year_prefix):
                yearly_total += exp["amount"]
                
                if exp["date"].startswith(month_prefix):
                    monthly_total += exp["amount"]
                    
                    row_idx = self.table.rowCount()
                    self.table.insertRow(row_idx)
                    
                    date_item = QTableWidgetItem(exp["date"])
                    date_item.setData(Qt.ItemDataRole.UserRole, idx)
                    date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    desc_item = QTableWidgetItem(exp["description"])
                    desc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    cat_item = QTableWidgetItem(exp["category"])
                    cat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    amount_item = QTableWidgetItem(f"${exp['amount']:.2f}")
                    amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    
                    self.table.setItem(row_idx, 0, date_item)
                    self.table.setItem(row_idx, 1, desc_item)
                    self.table.setItem(row_idx, 2, cat_item)
                    self.table.setItem(row_idx, 3, amount_item)
                    
        self.month_total_label.setText(f"Month Total: ${monthly_total:.2f}")
        self.year_total_label.setText(f"Year Total: ${yearly_total:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTracker()
    window.show()
    sys.exit(app.exec())