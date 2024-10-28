import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QLineEdit, QPushButton, QMenu, QAction, QInputDialog, QFileDialog, QSplitter, QGroupBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor
from SettingsManager import SettingsManager
from ChatManager import ChatManager
from APIManager import APIManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ghost Writer")
        self.setGeometry(100, 100, 800, 600)
        self.chat_counter = 0
        self.chats = {}
        self.current_chat = None
        
        # Create API Manager first
        self.api_manager = APIManager()
        
        # Then create Settings Manager
        self.settings_manager = SettingsManager(self)
        self.settings_manager.settings_changed.connect(self.apply_settings)
        
        # Create Chat Manager
        self.chat_manager = ChatManager()
        
        # Create widgets before layout
        self.create_widgets()
        
        # Initialize UI and apply settings
        self.init_ui()
        self.apply_settings(self.settings_manager.settings)
        self.load_chats()

    def create_widgets(self):
        """Create all widgets before layout"""
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # Chat list
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.load_chat)
        
        # Input box (removed fixed height constraint)
        self.input_box = QTextEdit()
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

    def init_ui(self):
        """Initialize the UI layout"""
        # Create menu first
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        
        # Settings action
        settings_action = QAction('Settings', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Import/Export actions
        import_action = QAction('Import Chats', self)
        import_action.triggered.connect(self.import_chats)
        file_menu.addAction(import_action)
        
        export_action = QAction('Export All Chats', self)
        export_action.triggered.connect(self.export_chats)
        file_menu.addAction(export_action)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left side (chat list and buttons)
        left_widget = QWidget()
        left_widget.setMinimumWidth(200)
        left_layout = QVBoxLayout()
        
        # Add chat list
        self.chat_list.setMinimumWidth(180)
        left_layout.addWidget(self.chat_list, stretch=1)
        
        # Add all buttons below chat list
        button_layout = QVBoxLayout()
        
        # Chat management buttons
        new_chat_btn = QPushButton("New Chat")
        new_chat_btn.clicked.connect(self.create_new_chat)
        button_layout.addWidget(new_chat_btn)
        
        delete_chat_btn = QPushButton("Delete Chat")
        delete_chat_btn.clicked.connect(self.delete_chat)
        button_layout.addWidget(delete_chat_btn)
        
        # Settings button
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_button)
        
        left_layout.addLayout(button_layout)
        left_widget.setLayout(left_layout)
        
        # Right side (chat display and input)
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)
        right_layout = QVBoxLayout()
        
        # Create vertical splitter for chat display and input
        right_splitter = QSplitter(Qt.Vertical)
        
        # Add chat display to splitter
        self.chat_display.setMinimumWidth(380)
        self.chat_display.setMinimumHeight(100)  # Minimum height for chat display
        right_splitter.addWidget(self.chat_display)
        
        # Create input container
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        input_container.setMinimumHeight(100)  # Minimum height for container
        
        # Add input box and send button to container
        self.input_box.setMinimumWidth(380)
        self.input_box.setMinimumHeight(50)  # Minimum height for input
        self.input_box.setMaximumHeight(800)  # Significantly increased maximum height
        input_layout.addWidget(self.input_box, stretch=1)  # Add stretch to input box
        input_layout.addWidget(self.send_button)
        
        # Add input container to splitter
        right_splitter.addWidget(input_container)
        
        # Prevent either component from collapsing
        right_splitter.setCollapsible(0, False)  # Prevent chat display from collapsing
        right_splitter.setCollapsible(1, False)  # Prevent input container from collapsing
        
        # Set initial sizes for the right splitter [chat_display, input_container]
        right_splitter.setSizes([400, 150])  # Increased initial size for input container
        
        # Add right splitter to right layout
        right_layout.addWidget(right_splitter)
        right_widget.setLayout(right_layout)
        
        # Add to main layout with horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        
        # Set minimum sizes and prevent collapsing
        main_splitter.setMinimumWidth(600)
        main_splitter.setSizes([200, 400])
        main_splitter.setCollapsible(0, False)  # Prevent left side from collapsing
        main_splitter.setCollapsible(1, False)  # Prevent right side from collapsing
        
        main_layout.addWidget(main_splitter)
        
        # Set up context menu for chat list
        self.chat_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_list.customContextMenuRequested.connect(self.show_chat_context_menu)

    def create_new_chat(self):
        self.chat_counter += 1
        new_chat_name = f"Chat {self.chat_counter}"
        self.chats[new_chat_name] = []
        self.chat_list.addItem(new_chat_name)
        self.chat_list.setCurrentRow(self.chat_list.count() - 1)
        self.load_chat(self.chat_list.currentItem())
        self.save_chats()

    def load_chat(self, item):
        self.current_chat = item.text()
        self.chat_display.clear()
        for message in self.chats[self.current_chat]:
            self.chat_display.append(message)

    def send_message(self):
        if not self.current_chat:
            return
            
        message = self.input_box.toPlainText().strip()
        if message:
            # Add user message
            self.update_chat_content({
                "role": "user",
                "content": message
            })
            
            # Clear input
            self.input_box.clear()
            
            # Get AI response
            response = self.api_manager.generate_response(message)
            
            # Add AI response
            self.update_chat_content({
                "role": "assistant",
                "content": response
            })

    def show_chat_context_menu(self, position):
        """Show context menu for chat list items"""
        menu = QMenu()
        
        # Only show these options if an item is selected
        if self.chat_list.currentItem():
            rename_action = menu.addAction("Rename")
            rename_action.triggered.connect(self.rename_chat)
            
            export_action = menu.addAction("Export Chat")
            export_action.triggered.connect(self.export_current_chat)
            
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self.delete_chat)
        
        menu.exec_(self.chat_list.mapToGlobal(position))

    def rename_chat(self):
        """Rename the selected chat"""
        current_item = self.chat_list.currentItem()
        if current_item:
            old_name = current_item.text()
            new_name, ok = QInputDialog.getText(self, "Rename Chat", 
                                              "Enter new name:", 
                                              text=old_name)
            if ok and new_name and new_name != old_name:
                self.chats[new_name] = self.chats.pop(old_name)
                current_item.setText(new_name)
                self.current_chat = new_name
                self.save_chats()

    def delete_chat(self):
        current_row = self.chat_list.currentRow()
        if current_row != -1:
            chat_name = self.chat_list.takeItem(current_row).text()
            del self.chats[chat_name]
            if self.chat_list.count() == 0:
                self.chat_display.clear()
                self.current_chat = None
            else:
                self.load_chat(self.chat_list.item(0))
            self.save_chats()

    def save_chats(self):
        with open('chats.json', 'w') as f:
            json.dump(self.chats, f)

    def load_chats(self):
        try:
            with open('chats.json', 'r') as f:
                self.chats = json.load(f)
            for chat_name in self.chats:
                self.chat_list.addItem(chat_name)
            if self.chats:
                chat_numbers = [int(name.split()[-1]) for name in self.chats if name.startswith("Chat ")]
                if chat_numbers:
                    self.chat_counter = max(chat_numbers)
                else:
                    self.chat_counter = 0
            if self.chat_list.count() > 0:
                self.chat_list.setCurrentRow(0)
                self.load_chat(self.chat_list.item(0))
        except FileNotFoundError:
            pass

    def import_chats(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Chats", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    imported_chats = json.load(f)
                self.chats.update(imported_chats)
                self.refresh_chat_list()
                self.save_chats()
            except Exception as e:
                print(f"Error importing chats: {e}")

    def export_chats(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Chats", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    json.dump(self.chats, f)
            except Exception as e:
                print(f"Error exporting chats: {e}")

    def refresh_chat_list(self):
        self.chat_list.clear()
        for chat_name in self.chats:
            self.chat_list.addItem(chat_name)
        if self.chats:
            self.chat_counter = max(int(name.split()[-1]) for name in self.chats if name.startswith("Chat "))
        if self.chat_list.count() > 0:
            self.chat_list.setCurrentRow(0)
            self.load_chat(self.chat_list.item(0))

    def export_current_chat(self):
        if not self.current_chat:
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Export Chat", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    json.dump({self.current_chat: self.chats[self.current_chat]}, f)
            except Exception as e:
                print(f"Error exporting chat: {e}")

    def show_settings(self):
        """Show the settings dialog"""
        if hasattr(self, 'settings_manager'):
            self.settings_manager.show()
            self.settings_manager.raise_()
            self.settings_manager.activateWindow()

    def apply_settings(self, settings):
        if hasattr(self, 'chat_display'):
            font = self.chat_display.font()
            font.setPointSize(settings["font_size"])
            self.chat_display.setFont(font)
            self.input_box.setFont(font)

        if settings["dark_mode"]:
            self.set_dark_theme()
        else:
            self.set_light_theme()
        
        self.apply_style()

        # Update API settings
        if hasattr(self, 'api_manager'):
            self.api_manager.model = settings.get("model", "llama2-uncensored")

        # Update ChatManager settings
        if hasattr(self, 'chat_manager'):
            self.chat_manager.auto_save = settings.get("auto_save", False)
            self.chat_manager.save_directory = settings.get("save_directory", "")

    def set_dark_theme(self):
        dark_palette = QPalette()
        # Windows 10 Dark Theme Colors
        dark_palette.setColor(QPalette.Window, QColor(32, 32, 32))  # Main background
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  # Main text
        dark_palette.setColor(QPalette.Base, QColor(45, 45, 45))  # Input field background
        dark_palette.setColor(QPalette.AlternateBase, QColor(39, 39, 39))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))  # Input field text
        dark_palette.setColor(QPalette.Button, QColor(51, 51, 51))  # Button background
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))  # Button text
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(0, 120, 215))  # Windows blue
        dark_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))  # Selection background
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))  # Selection text
        self.setPalette(dark_palette)

    def set_light_theme(self):
        light_palette = QPalette()
        # Windows 10 Light Theme Colors
        light_palette.setColor(QPalette.Window, QColor(255, 255, 255))  # Main background
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Main text
        light_palette.setColor(QPalette.Base, QColor(255, 255, 255))  # Input field background
        light_palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        light_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))  # Input field text
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))  # Button background
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # Button text
        light_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        light_palette.setColor(QPalette.Link, QColor(0, 120, 215))  # Windows blue
        light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))  # Selection background
        light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))  # Selection text
        self.setPalette(light_palette)

    def apply_style(self):
        # Get the current dark mode state from settings
        is_dark = self.settings_manager.settings.get("dark_mode", False)
        
        # Define common button style
        if is_dark:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
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
                }
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #363636;
                }
                QTextEdit, QListWidget {
                    background-color: #363636;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 4px;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #404040;
                }
                QMenu::item:selected {
                    background-color: #404040;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 7px;
                    padding: 0px 5px 0px 5px;
                }
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
                QTextEdit, QListWidget {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
                QMenu {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #cccccc;
                }
                QMenu::item:selected {
                    background-color: #4a90e2;
                    color: white;
                }
            """)

    def update_chat_content(self, message):
        """Update chat content and trigger auto-save"""
        if self.current_chat:
            self.chats[self.current_chat].append(message)
            self.display_chat()
            
            # Auto-save the current chat
            if hasattr(self, 'chat_manager'):
                chat_content = "\n".join([f"{msg['role']}: {msg['content']}" 
                                        for msg in self.chats[self.current_chat]])
                self.chat_manager.save_chat(self.current_chat, chat_content)

    def display_chat(self):
        """Display the current chat in the chat display"""
        if self.current_chat and hasattr(self, 'chat_display'):
            # Clear the display
            self.chat_display.clear()
            
            # Display each message
            for message in self.chats[self.current_chat]:
                role = message.get('role', 'unknown')
                content = message.get('content', '')
                
                # Format based on role
                if role == "user":
                    self.chat_display.append(f"You: {content}")
                elif role == "assistant":
                    self.chat_display.append(f"Assistant: {content}")
                else:
                    self.chat_display.append(f"{role}: {content}")
                
                # Add a newline between messages
                self.chat_display.append("")
            
            # Scroll to the bottom
            scrollbar = self.chat_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
