import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSpinBox, QMessageBox
)
from PyQt5.QtCore import QMetaObject, Qt
from basic.connect_devices import connect_devices
from basic.csv_handler import process_csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from test_script import test_app_install  # Assuming your function is in test_script.py

class AppTesterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.device_label = QLabel("Connected Devices: None")
        layout.addWidget(self.device_label)

        self.connect_button = QPushButton("Connect Devices")
        self.connect_button.clicked.connect(self.connect_devices)
        layout.addWidget(self.connect_button)

        self.load_csv_button = QPushButton("Load CSV File")
        self.load_csv_button.clicked.connect(self.load_csv)
        layout.addWidget(self.load_csv_button)

        self.install_attempt_label = QLabel("Installation Attempts:")
        layout.addWidget(self.install_attempt_label)
        
        self.install_attempt_input = QSpinBox()
        self.install_attempt_input.setMinimum(1)
        self.install_attempt_input.setMaximum(10)
        self.install_attempt_input.setValue(3)
        layout.addWidget(self.install_attempt_input)
        
        self.start_button = QPushButton("Start Testing")
        self.start_button.clicked.connect(self.start_testing)
        layout.addWidget(self.start_button)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
        self.setWindowTitle("App Installation Tester")
        self.setGeometry(300, 300, 500, 400)
        
        self.device_list = []
        self.package_names = []
        self.app_names = []
        self.df = None
        self.lock = Lock()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def connect_devices(self):
        try:
            self.device_list = connect_devices()
            self.device_label.setText(f"Connected Devices: {', '.join(self.device_list)}")
        except Exception as e:
            self.show_error(str(e))

    def load_csv(self):
        try:
            self.package_names, self.app_names, self.df, _, _ = process_csv()
            QMetaObject.invokeMethod(self.log_output, "append", Qt.QueuedConnection, "Loaded default CSV file: test1.csv")
        except Exception as e:
            self.show_error(str(e))

    def start_testing(self):
        if not self.device_list or not self.package_names:
            QMetaObject.invokeMethod(self.log_output, "append", Qt.QueuedConnection, "Error: Devices not connected or CSV not loaded.")
            return
        
        install_attempt = self.install_attempt_input.value()
        
        QMetaObject.invokeMethod(self.log_output, "append", Qt.QueuedConnection, "Starting tests...")
        
        def run_tests():
            try:
                with ThreadPoolExecutor() as executor:
                    for device in self.device_list:
                        QMetaObject.invokeMethod(self.log_output, "append", Qt.QueuedConnection, (f"Processing device {device}...",))
                        self.lock.acquire()
                        executor.submit(test_app_install, device, self.package_names, self.app_names, self.df, install_attempt)
                        self.lock.release()
                QMetaObject.invokeMethod(self.log_output, "append", Qt.QueuedConnection, "Testing completed.")
            except Exception as e:
                self.show_error(str(e))
        
        threading.Thread(target=run_tests, daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AppTesterGUI()
    ex.show()
    sys.exit(app.exec_())