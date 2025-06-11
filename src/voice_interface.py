import re
from src.nlp_processor import NLPProcessor
import speech_recognition as sr
import pyttsx3
import threading
import time

class VoiceAssistant:
    """Voice-controlled task management"""
    
    def __init__(self, todo_list):
        self.todo_list = todo_list
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.nlp = NLPProcessor()
        self.active = False
        self.listening_thread = None
        
    def listen(self):
        """Continuously listen for voice commands"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Voice assistant activated. Say 'exit' to stop.")
                
                while self.active:
                    try:
                        print("Listening... (say 'exit' to stop)")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                        command = self.recognizer.recognize_google(audio)
                        print(f"Command: {command}")
                        
                        # Process command immediately
                        self.process_command(command)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                        self.speak("I didn't understand that, please try again")
                        continue
                    except Exception as e:
                        print(f"Voice error: {e}")
                        self.speak("Sorry, I encountered an error")
                        time.sleep(1)
                        continue
                        
        except Exception as e:
            print(f"Fatal voice error: {e}")
            self.active = False
    
    def process_command(self, command):
        """Execute voice commands"""
        command = command.lower()
        
        try:
            if "add" in command:
                task_text = command.replace("add", "").strip()
                details = self.nlp.parse_command(task_text)
                self.todo_list.add_task(
                    details["description"],
                    due_date=details["due_date"],
                    priority=details["priority"]
                )
                self.speak(f"Added task: {details['description']}")
                
            elif any(word in command for word in ["complete", "done", "finish"]):
                match = re.search(r'\d+', command)
                if match:
                    task_id = int(match.group())
                    self.todo_list.mark_completed(task_id)
                    task_desc = self.todo_list.tasks[task_id].description
                    self.speak(f"Completed task: {task_desc}")
                else:
                    self.speak("Please specify a task number")
                    
            elif "what" in command and "tasks" in command:
                pending = [t for t in self.todo_list.tasks if not t.completed]
                if pending:
                    self.speak(f"You have {len(pending)} pending tasks")
                else:
                    self.speak("No pending tasks! Great job!")
                    
            elif any(word in command for word in ["exit", "stop", "quit"]):
                self.speak("Goodbye!")
                self.active = False  # This will break the loop in listen()
                
            else:
                self.speak("I didn't understand that command")
                
        except Exception as e:
            self.speak(f"Error: {str(e)}")
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
    
    def start(self):
        """Start voice assistant in background thread"""
        if not self.active:
            self.active = True
            self.listening_thread = threading.Thread(target=self.listen, daemon=True)
            self.listening_thread.start()
    
    def stop(self):
        """Stop voice assistant"""
        self.active = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1)