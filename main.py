import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QMenu,
                             QAbstractItemView) 
from PyQt6.QtCore import Qt

from backend.scanner import analyze_path, format_size 

# Custom Cell Blueprint for accurate Math Sorting
class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        my_bytes = self.data(Qt.ItemDataRole.UserRole)
        other_bytes = other.data(Qt.ItemDataRole.UserRole)
        return my_bytes < other_bytes


class DiskAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disk Space Analyzer")
        self.setGeometry(100, 100, 800, 600)

        # 1. Setup Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 2. Build Top Bar
        top_bar = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser("~")) 
        
        # --- NEW: Up Level Button ---
        self.up_btn = QPushButton("⬆ Up Level")
        self.up_btn.clicked.connect(self.go_up_level)
        
        self.scan_btn = QPushButton("Scan Directory")
        self.scan_btn.clicked.connect(self.run_scan) 

        top_bar.addWidget(self.path_input)
        top_bar.addWidget(self.up_btn) # Added to the layout
        top_bar.addWidget(self.scan_btn)
        main_layout.addLayout(top_bar)

        # 3. Build the Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Type", "Name", "Size"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        
        # 1. Select entire rows instead of individual cells
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # 2. Remove the ugly dotted focus box that appears when you click
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        # --------------------------------
        
        # 1. Select entire rows instead of individual cells
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # 2. Remove the ugly dotted focus box around the table
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        
        # --- NEW: 3. Use CSS to remove the tiny orange line inside the cell ---
        self.table.setStyleSheet("QTableWidget::item:focus { outline: none; }")
        # --------------------------------

        # Enable features
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(self.navigate_folder)

        main_layout.addWidget(self.table)

    # --- NEW: Go Up Level Logic ---
    def go_up_level(self):
        """Moves up one directory level and rescans."""
        current_path = self.path_input.text()
        
        # os.path.dirname takes "C:\Users\Name" and returns "C:\Users"
        parent_dir = os.path.dirname(current_path) 
        
        # Make sure the parent directory actually exists before trying to scan it
        if os.path.exists(parent_dir):
            self.path_input.setText(parent_dir)
            self.run_scan()

    def run_scan(self):
        target_path = self.path_input.text()
        
        if not os.path.exists(target_path):
            QMessageBox.warning(self, "Error", "That path does not exist!")
            return

        self.scan_btn.setText("Scanning...")
        self.scan_btn.setEnabled(False)
        self.up_btn.setEnabled(False) # Disable the up button while scanning
        
        self.table.setSortingEnabled(False) 
        QApplication.processEvents() 

        results = analyze_path(target_path)
        
        self.table.setRowCount(len(results))
        for row, item in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(item['type']))
            
            name_item = QTableWidgetItem(item['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, item['path'])
            self.table.setItem(row, 1, name_item)
            
            size_item = NumericTableWidgetItem(format_size(item['size_bytes']))
            size_item.setData(Qt.ItemDataRole.UserRole, item['size_bytes'])
            self.table.setItem(row, 2, size_item)

        self.table.setSortingEnabled(True)
        self.scan_btn.setText("Scan Directory")
        self.scan_btn.setEnabled(True)
        self.up_btn.setEnabled(True)

    def show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0: return 

        menu = QMenu()
        open_action = menu.addAction("Open Location in Windows")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == open_action:
            target_path = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            if os.path.isfile(target_path):
                target_path = os.path.dirname(target_path)
            os.startfile(target_path)

    def navigate_folder(self, row, column):
        item_type = self.table.item(row, 0).text()
        
        if item_type == "Folder":
            target_path = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            self.path_input.setText(target_path)
            self.run_scan()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiskAnalyzerApp()
    window.show()
    sys.exit(app.exec())