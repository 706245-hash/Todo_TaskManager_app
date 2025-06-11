from datetime import datetime 

class Task:
    """Enhanced task with categories and tags support"""
    
    def __init__(self, description, completed=False, priority="medium", 
                 due_date=None, category="General", tags=None,
                 start_time=None, end_time=None):  # Add these parameters
        """
        Initialize a task with extended attributes
        
        :param tags: List of tags (e.g., ["urgent", "home"])
        :param start_time: When task was started (datetime)
        :param end_time: When task was completed (datetime)
        """
        if priority not in ["low", "medium", "high"]:
            raise ValueError("Priority must be low, medium, or high")
            
        self.description = description
        self.completed = completed
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.tags = tags or []
        self.start_time = start_time  # Initialize these attributes
        self.end_time = end_time

    def start(self):
        self.start_time = datetime.now()
    
    def complete(self):
        self.end_time = datetime.now()

    def __repr__(self):
        return (f"Task(description='{self.description}', completed={self.completed}, "
                f"priority='{self.priority}', due_date='{self.due_date}', "
                f"category='{self.category}', tags={self.tags}, "
                f"start_time={self.start_time}, end_time={self.end_time})")  # Update repr