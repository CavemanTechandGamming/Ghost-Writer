import os

class ChatManager:
    def __init__(self):
        self.auto_save = False
        self.save_directory = ""
        self.current_chat = None
        
    def set_auto_save(self, enabled: bool, directory: str = ""):
        """Configure auto-save settings"""
        self.auto_save = enabled
        self.save_directory = directory
        
    def save_chat(self, chat_id: str, content: str):
        """Save chat content"""
        if self.auto_save and self.save_directory:
            try:
                # Create save directory if it doesn't exist
                os.makedirs(self.save_directory, exist_ok=True)
                
                # Save chat to file
                file_path = os.path.join(self.save_directory, f"chat_{chat_id}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
                print(f"Auto-saved chat to: {file_path}")
            except Exception as e:
                print(f"Error auto-saving chat: {e}")

