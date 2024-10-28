import requests
import json
import subprocess
from typing import List, Tuple, Optional

class APIManager:
    def __init__(self):
        self.base_url = "http://localhost:11434/api"
        self._model = "llama2-uncensored"  # Use private variable
        self._available_models: List[str] = []
        self.refresh_models()  # Load available models on init

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str):
        if value in self._available_models or not self._available_models:
            self._model = value
        else:
            print(f"Warning: Model {value} not found in available models")
            # Keep current model if new one isn't available

    def refresh_models(self) -> None:
        """Refresh the list of available models"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
            self._available_models = []
            for line in result.stdout.split('\n')[1:]:  # Skip header line
                if line.strip():
                    model_name = line.split()[0].split(':')[0]  # Get name without version
                    self._available_models.append(model_name)
        except subprocess.CalledProcessError as e:
            print(f"Error running ollama list: {e}")
        except Exception as e:
            print(f"Error refreshing models: {e}")

    def list_models(self) -> List[str]:
        """Get list of installed models"""
        if not self._available_models:
            self.refresh_models()
        return self._available_models

    def download_model(self, model_name: str) -> Tuple[bool, str]:
        """Download a new model using Ollama"""
        try:
            process = subprocess.Popen(
                ['ollama', 'pull', model_name], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            self.refresh_models()  # Refresh model list after download
            return True, "Model download started"
        except Exception as e:
            return False, f"Error downloading model: {e}"

    def remove_model(self, model_name: str) -> Tuple[bool, str]:
        """Remove a model using Ollama"""
        try:
            if model_name == self._model:
                return False, "Cannot remove currently active model"
                
            result = subprocess.run(
                ['ollama', 'rm', model_name], 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.refresh_models()  # Refresh model list after removal
            return True, "Model removed successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Error removing model: {e.stderr}"
        except Exception as e:
            return False, f"Error removing model: {e}"

    def generate_response(self, prompt: str) -> str:
        """Generate a response using the current model"""
        try:
            if not self._model:
                return "Error: No model selected"

            print(f"Using model: {self._model}")  # Debug print
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            elif response.status_code == 404:
                self.refresh_models()  # Refresh models list on 404
                return f"Error: Model '{self._model}' not found. Please check available models in settings."
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Please make sure Ollama is running."
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Please try again."
        except Exception as e:
            return f"Error: {str(e)}"
