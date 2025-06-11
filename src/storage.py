import json
import os
from src.task import Task
from datetime import datetime

class Storage:
    """Handles persistent storage of tasks using JSON file"""
    
    def __init__(self, filename="tasks.json"):
        """
        Initialize storage handler.
        
        :param filename: JSON file name (default: tasks.json)
        """
        self.filename = filename
        
    def save_tasks(self, tasks):
        """Serialize tasks to JSON file"""
        if not isinstance(tasks, list):
            raise ValueError("Tasks must be a list")
        try:
            with open(self.filename, 'w') as f:
                task_dicts = []
                for task in tasks:
                    task_dict = task.__dict__.copy()
                    # Convert datetime objects to strings
                    if task_dict['start_time'] and isinstance(task_dict['start_time'], datetime):
                        task_dict['start_time'] = task_dict['start_time'].isoformat()
                    if task_dict['end_time'] and isinstance(task_dict['end_time'], datetime):
                        task_dict['end_time'] = task_dict['end_time'].isoformat()
                    task_dicts.append(task_dict)
                json.dump(task_dicts, f, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    def load_tasks(self):
        """Load tasks from JSON file"""
        if not os.path.exists(self.filename):
            return []
            
        try:
            with open(self.filename) as f:
                task_dicts = json.load(f)
                tasks = []
                for task_dict in task_dicts:
                    # Handle old tasks that don't have the new fields
                    if 'start_time' not in task_dict:
                        task_dict['start_time'] = None
                    if 'end_time' not in task_dict:
                        task_dict['end_time'] = None
                    # Convert string timestamps back to datetime objects
                    if task_dict['start_time'] and isinstance(task_dict['start_time'], str):
                        task_dict['start_time'] = datetime.fromisoformat(task_dict['start_time'])
                    if task_dict['end_time'] and isinstance(task_dict['end_time'], str):
                        task_dict['end_time'] = datetime.fromisoformat(task_dict['end_time'])
                    tasks.append(Task(**task_dict))
                return tasks
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading tasks: {e}")
            return []