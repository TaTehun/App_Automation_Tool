import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QSpinBox
)
from basic.connect_devices import connect_devices
from basic.csv_handler import process_csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event
from app_install_info import test_app_install

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
        self.install_attempt_input.setMaximum(50)
        self.install_attempt_input.setValue(3)
        layout.addWidget(self.install_attempt_input)
        
        self.start_button = QPushButton("Start Testing")
        self.start_button.clicked.connect(self.start_testing)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Testing")
        self.stop_button.clicked.connect(self.stop_testing)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
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
        self.stop_testing_event = Event()

    def connect_devices(self):
        self.device_list = connect_devices()
        self.device_label.setText(f"Connected Devices: {', '.join(self.device_list)}")

    def load_csv(self):
        self.package_names, self.app_names, self.df, _, _ = process_csv()
        self.log_output.append("Loaded default CSV file: test1.csv")

    def start_testing(self):
        if not self.device_list or not self.package_names:
            self.log_output.append("Error: Devices not connected or CSV not loaded.")
            return
        
        install_attempt = self.install_attempt_input.value()
        self.stop_testing_event.clear()
        
        self.log_output.append("Starting tests...")
        
        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)
        
        def run_tests():
            with ThreadPoolExecutor() as executor:
                for device in self.device_list:
                    if self.stop_testing_event.is_set():
                        break
                    self.log_output.append(f"Processing device {device}...")
                    self.lock.acquire()
                    executor.submit(test_app_install, device, self.package_names, self.app_names, self.df, install_attempt)
                    self.lock.release()
            self.log_output.append("Testing completed.")
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(True)
        
        threading.Thread(target=run_tests, daemon=True).start()

    def stop_testing(self):
        os._exit(0)
        #self.log_output.append("Testing stopped by user.")
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AppTesterGUI()
    ex.show()
    sys.exit(app.exec_())
