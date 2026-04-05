import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt

# Import the engine we just built!
from backend.scanner import analyze_path, format_size 

class DiskAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disk Space Analyzer")
        self.setGeometry(100, 100, 800, 600)

        # 1. Setup the main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 2. Build the Top Bar
        top_bar = QHBoxLayout()
        self.path_input = QLineEdit()
        # Default to your user folder for safe testing
        self.path_input.setText(os.path.expanduser("~")) 
        
        self.scan_btn = QPushButton("Scan Directory")
        self.scan_btn.clicked.connect(self.run_scan) 

        top_bar.addWidget(self.path_input)
        top_bar.addWidget(self.scan_btn)
        main_layout.addLayout(top_bar)

        # 3. Build the Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Type", "Name", "Size"])
        
        # Make the 'Name' column stretch to fill the window
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

    def run_scan(self):
        target_path = self.path_input.text()
        
        if not os.path.exists(target_path):
            QMessageBox.warning(self, "Error", "That path does not exist!")
            return

        self.scan_btn.setText("Scanning...")
        self.scan_btn.setEnabled(False)
        QApplication.processEvents() # Force UI to update

        # Call the backend engine
        results = analyze_path(target_path)
        
        # Populate the table with our results
        self.table.setRowCount(len(results))
        for row, item in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(item['type']))
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            
            # Create a size item and hide the raw bytes inside it for future sorting
            size_item = QTableWidgetItem(format_size(item['size_bytes']))
            size_item.setData(Qt.ItemDataRole.UserRole, item['size_bytes'])
            self.table.setItem(row, 2, size_item)

        self.scan_btn.setText("Scan Directory")
        self.scan_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiskAnalyzerApp()
    window.show()
    sys.exit(app.exec())