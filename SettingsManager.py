import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QCheckBox, QPushButton, QFileDialog, QSpinBox, QComboBox, 
                             QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPalette, QColor
from APIManager import APIManager

class SettingsManager(QWidget):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize default settings
        self.settings = {
            "theme": "light",
            "font_size": 12,
            "auto_save": True,
            "save_directory": "",
            "dark_mode": False,
            "model": "llama2-uncensored"
        }
        
        # Setup window properties
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(400, 500)
        
        # Load settings and initialize UI
        self.load_settings()
        self.setup_ui()
        self.apply_style()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Model Management Section
        layout.addWidget(self.create_model_group())
        
        # Font Settings Section
        layout.addWidget(self.create_font_group())
        
        # Auto Save Section
        layout.addWidget(self.create_save_group())
        
        # Theme Section
        layout.addWidget(self.create_theme_group())
        
        # Buttons Section
        layout.addLayout(self.create_button_layout())
        
        self.setLayout(layout)

    def create_model_group(self):
        group = QGroupBox("Model Management")
        layout = QVBoxLayout()
        
        # Current Model Selection
        current_model_layout = QHBoxLayout()
        current_model_layout.addWidget(QLabel("Current Model:"))
        self.model_input = QComboBox()
        self.refresh_model_list()
        current_model_layout.addWidget(self.model_input)
        layout.addLayout(current_model_layout)
        
        # New Model Installation
        new_model_layout = QHBoxLayout()
        new_model_layout.addWidget(QLabel("Install New Model:"))
        self.new_model_input = QLineEdit()
        new_model_layout.addWidget(self.new_model_input)
        install_button = QPushButton("Install")
        install_button.clicked.connect(self.download_new_model)
        new_model_layout.addWidget(install_button)
        layout.addLayout(new_model_layout)
        
        # Remove Model Button
        remove_button = QPushButton("Remove Selected Model")
        remove_button.clicked.connect(self.remove_selected_model)
        layout.addWidget(remove_button)
        
        group.setLayout(layout)
        return group

    def create_font_group(self):
        group = QGroupBox("Font")
        layout = QVBoxLayout()
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.settings["font_size"])
        font_size_layout.addWidget(self.font_size_spin)
        layout.addLayout(font_size_layout)
        group.setLayout(layout)
        return group

    def create_save_group(self):
        group = QGroupBox("Auto Save")
        layout = QVBoxLayout()
        
        self.auto_save_checkbox = QCheckBox("Enable Auto Save")
        self.auto_save_checkbox.setChecked(self.settings["auto_save"])
        layout.addWidget(self.auto_save_checkbox)
        
        save_dir_layout = QHBoxLayout()
        save_dir_layout.addWidget(QLabel("Save Directory:"))
        self.save_dir_input = QLineEdit(self.settings["save_directory"])
        save_dir_layout.addWidget(self.save_dir_input)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        save_dir_layout.addWidget(browse_button)
        layout.addLayout(save_dir_layout)
        
        group.setLayout(layout)
        return group

    def create_theme_group(self):
        group = QGroupBox("Theme")
        layout = QVBoxLayout()
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.setChecked(self.settings["dark_mode"])
        self.dark_mode_checkbox.stateChanged.connect(self.apply_style)
        layout.addWidget(self.dark_mode_checkbox)
        group.setLayout(layout)
        return group

    def create_button_layout(self):
        layout = QHBoxLayout()
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)
        return layout

    def save_settings(self):
        try:
            self.settings.update({
                "font_size": self.font_size_spin.value(),
                "auto_save": self.auto_save_checkbox.isChecked(),
                "save_directory": self.save_dir_input.text(),
                "dark_mode": self.dark_mode_checkbox.isChecked(),
                "theme": "dark" if self.dark_mode_checkbox.isChecked() else "light",
                "model": self.model_input.currentText()
            })

            with open("settings.json", "w") as f:
                json.dump(self.settings, f)

            if self.parent() and hasattr(self.parent(), 'api_manager'):
                self.parent().api_manager.model = self.settings["model"]

            self.settings_changed.emit(self.settings)
            QMessageBox.information(self, "Success", "Settings saved successfully")
            self.close()
        except Exception as e:
            print(f"Debug - Error saving settings: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")

    def apply_style(self):
        # Get the current dark mode state
        is_dark = self.dark_mode_checkbox.isChecked() if hasattr(self, 'dark_mode_checkbox') else self.settings["dark_mode"]
        
        # Define button styles based on dark mode
        if is_dark:
            button_style = """
                QPushButton {
                    background-color: #404040;  /* Dark gray background */
                    color: #ffffff;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;  /* Slightly lighter on hover */
                }
                QPushButton:pressed {
                    background-color: #363636;  /* Darker when pressed */
                }
                #cancel_button {
                    background-color: #633231;  /* Darker red for cancel */
                }
                #cancel_button:hover {
                    background-color: #804241;  /* Slightly lighter red on hover */
                }
            """
        else:
            button_style = """
                QPushButton {
                    background-color: #4a90e2;
                    color: #ffffff;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
                QPushButton:pressed {
                    background-color: #2a5f9e;
                }
                #cancel_button {
                    background-color: #e74c3c;
                }
                #cancel_button:hover {
                    background-color: #c0392b;
                }
            """
        
        # Rest of the style remains the same
        if is_dark:
            self.setStyleSheet(button_style + """
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMainWindow, QDialog {
                    background-color: #2b2b2b;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #404040;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 7px;
                    padding: 0px 5px 0px 5px;
                    color: #ffffff;
                }
                QLineEdit, QSpinBox, QComboBox {
                    padding: 5px;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    background-color: #363636;
                    color: #ffffff;
                }
                QComboBox QAbstractItemView {
                    background-color: #363636;
                    color: #ffffff;
                    selection-background-color: #4a90e2;
                }
                QLabel {
                    color: #ffffff;
                }
                QCheckBox {
                    spacing: 5px;
                    color: #ffffff;
                }
                QCheckBox::indicator {
                    width: 13px;
                    height: 13px;
                    background-color: #363636;
                    border: 1px solid #404040;
                }
                QCheckBox::indicator:checked {
                    background-color: #4a90e2;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: #4a90e2;
                }
                QComboBox::down-arrow {
                    background-color: #4a90e2;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #4a90e2;
                }
                QMessageBox {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet(button_style + """
                QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QMainWindow, QDialog {
                    background-color: #f0f0f0;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                    color: #333333;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 7px;
                    padding: 0px 5px 0px 5px;
                    color: #333333;
                }
                QLineEdit, QSpinBox, QComboBox {
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    background-color: white;
                    color: #333333;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #333333;
                    selection-background-color: #4a90e2;
                }
                QLabel {
                    color: #333333;
                }
                QCheckBox {
                    spacing: 5px;
                    color: #333333;
                }
                QCheckBox::indicator {
                    width: 13px;
                    height: 13px;
                }
                QMessageBox {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QMessageBox QLabel {
                    color: #333333;
                }
            """)

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                loaded_settings = json.load(f)
                # Only update settings that we currently use
                for key in ["theme", "font_size", "auto_save", "save_directory", "dark_mode", "model"]:
                    if key in loaded_settings:
                        self.settings[key] = loaded_settings[key]
        except FileNotFoundError:
            pass  # Use default settings if file doesn't exist

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if directory:
            self.save_dir_input.setText(directory)

    def refresh_model_list(self):
        """Refresh the list of available models"""
        try:
            # Get API manager
            if self.parent() and hasattr(self.parent(), 'api_manager'):
                api_manager = self.parent().api_manager
            else:
                api_manager = APIManager()

            # Get list of models
            models = api_manager.list_models()
            
            # Clear and repopulate the combo box
            if hasattr(self, 'model_input'):
                self.model_input.clear()
                self.model_input.addItems(models)
                
                # Set current model if it exists
                current_model = self.settings.get("model", "llama2-uncensored")
                index = self.model_input.findText(current_model)
                if index >= 0:
                    self.model_input.setCurrentIndex(index)
                
        except Exception as e:
            print(f"Error refreshing model list: {e}")

    def download_new_model(self):
        """Download a new model"""
        # Get API manager
        if self.parent() and hasattr(self.parent(), 'api_manager'):
            api_manager = self.parent().api_manager
        else:
            api_manager = APIManager()

        model_name = self.new_model_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Error", 
                "Please enter a model name.\n\n"
                "Popular models include:\n"
                "• llama2\n"
                "• codellama\n"
                "• mistral\n"
                "• neural-chat\n"
                "\nVisit: https://ollama.ai/library for more models")
            return

        reply = QMessageBox.question(self, 'Confirm Installation', 
            f'Do you want to install the model "{model_name}"?\n\n'
            'This will download the model which may:\n'
            '• Take several minutes\n'
            '• Use significant bandwidth\n'
            '• Require several GB of storage',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Determine the operating system and open appropriate terminal
                import platform
                import os
                
                system = platform.system().lower()
                command = f"ollama pull {model_name}"
                
                print(f"Operating System: {system}")  # Debug print
                print(f"Command to run: {command}")   # Debug print
                
                if system == "windows":
                    print("Attempting to open Windows CMD")  # Debug print
                    os.system(f'start cmd /K "{command}"')
                elif system == "darwin":
                    print("Attempting to open macOS Terminal")  # Debug print
                    os.system(f'open -a Terminal.app -e "bash -c \'{command}; read -p Press\\ any\\ key\\ to\\ close...\'"')
                elif system == "linux":
                    print("Attempting to open Linux terminal")  # Debug print
                    terminals = ['gnome-terminal', 'konsole', 'xterm']
                    for term in terminals:
                        try:
                            if term == 'gnome-terminal':
                                os.system(f'{term} -- bash -c "{command}; read -p \'Press Enter to close...\'"')
                            else:
                                os.system(f'{term} -e "bash -c \'{command}; read -p \"Press Enter to close...\"\')"')
                            print(f"Successfully opened {term}")  # Debug print
                            break
                        except:
                            print(f"Failed to open {term}")  # Debug print
                            continue
                
                self.new_model_input.clear()
                # Refresh the model list after a short delay
                QTimer.singleShot(1000, self.refresh_model_list)
                
            except Exception as e:
                print(f"Error during download: {str(e)}")  # Debug print
                QMessageBox.warning(self, "Error", 
                    f"Failed to start installation: {str(e)}\n\n"
                    "Make sure:\n"
                    "• Ollama is installed\n"
                    "• You have internet connection")

    def remove_selected_model(self):
        """Remove the currently selected model"""
        # Get API manager
        if self.parent() and hasattr(self.parent(), 'api_manager'):
            api_manager = self.parent().api_manager
        else:
            api_manager = APIManager()

        model_name = self.model_input.currentText()
        if not model_name:
            QMessageBox.warning(self, "Error", "No model selected")
            return

        reply = QMessageBox.question(self, 'Confirm Removal', 
                                   f'Are you sure you want to remove the model "{model_name}"?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = api_manager.remove_model(model_name)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_model_list()
            else:
                QMessageBox.warning(self, "Error", message)
