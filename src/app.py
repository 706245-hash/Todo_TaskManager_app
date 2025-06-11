from src.task import Task
from src.storage import Storage
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression

class TodoList:
    """Main application controller for to-do list operations"""
    
    def __init__(self):
        self.storage = Storage()
        self.tasks = self.storage.load_tasks()
    
    def add_task(self, description, **kwargs):
        """Add new task to the list"""
        if not description.strip():
            raise ValueError("Task description cannot be empty")
        self.tasks.append(Task(description, **kwargs))
        self.save()
    
    def edit_task(self, task_id, description=None, category=None, completed=None, priority=None, tags=None, due_date=None):
        """Modify existing task attributes"""
        try:
            task = self.tasks[task_id]
            if description:
                task.description = description
            if completed is not None:
                task.completed = completed
            if category:
                task.category = category
            if priority:
                task.priority = priority
            if tags:
                task.tags = tags
            if due_date:
                task.due_date = due_date
            self.save()
            return task
        except IndexError:
            raise IndexError("Invalid task ID")
    
    def view_tasks(self, filter_completed=None, sort_by="priority"):
        """
        Get tasks with filtering and sorting
        
        :param filter_completed: None (all), True (completed), False (pending)
        :param sort_by: 'priority', 'due_date', or 'added'
        :return: Filtered and sorted list of tasks
        """
        # Filtering
        tasks = self.tasks if filter_completed is None else \
                [t for t in self.tasks if t.completed == filter_completed]
        
        # Sorting
        if sort_by == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            tasks.sort(key=lambda t: priority_order[t.priority])
        elif sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date or "9999-12-31")  # Put undated last
        # Default is added order (no sort needed)
        
        return tasks
    def mark_completed(self, task_id, completed=True):
        """Update task completion status"""
        try:
            self.tasks[task_id].completed = completed
            self.save()
        except IndexError:
            raise IndexError("Invalid task ID")
    
    def delete_task(self, task_id):
        """Remove task from list"""
        try:
            self.tasks.pop(task_id)
            self.save()
        except IndexError:
            raise IndexError("Invalid task ID")
    
    def save(self):
        """Persist current state to storage"""
        self.storage.save_tasks(self.tasks)
    
    def search_tasks(self, search_term="", category=None, tags=None, 
                    priority=None, due_within=None):
        """
        Search tasks with multiple criteria
        
        :param search_term: Text to search in description
        :param category: Filter by category
        :param tags: List of tags to match (any)
        :param priority: Filter by priority
        :param due_within: Days until due (e.g., 7 for tasks due within a week)
        :return: Filtered list of tasks
        """
        results = self.tasks
        
        # Apply filters
        if search_term:
            search_term = search_term.lower()
            results = [t for t in results if search_term in t.description.lower()]
        
        if category:
            results = [t for t in results if t.category == category]
            
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]
            
        if priority:
            results = [t for t in results if t.priority == priority]
            
        if due_within is not None:
            today = datetime.today().date()
            end_date = today + timedelta(days=due_within)
            results = [
                t for t in results 
                if t.due_date and 
                today <= datetime.strptime(t.due_date, "%Y-%m-%d").date() <= end_date
            ]
            
        return results
    
    def get_stats(self):
        """Calculate productivity statistics"""
        stats = {
            "total": len(self.tasks),
            "completed": sum(1 for t in self.tasks if t.completed),
            "by_priority": defaultdict(int),
            "by_category": defaultdict(int),
            "overdue": 0
        }
        
        today = datetime.today().date()
        
        for task in self.tasks:
            stats["by_priority"][task.priority] += 1
            
            if task.category:
                stats["by_category"][task.category] += 1
                
            if task.due_date and not task.completed:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due_date < today:
                    stats["overdue"] += 1
        
        # Calculate completion percentage
        stats["completion_pct"] = (
            (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        )
        
        return stats
    
    def export_csv(self, filename="tasks_export.csv"):
        """Export tasks to CSV file"""
        import csv
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["Description", "Completed", "Priority", 
                            "Due Date", "Category", "Tags"])
            
            # Write tasks
            for task in self.tasks:
                writer.writerow([
                    task.description,
                    "Yes" if task.completed else "No",
                    task.priority,
                    task.due_date or "",
                    task.category,
                    ", ".join(task.tags)
                ])
        return filename
    
    def predict_completion_time(self, task_id):
        """Predict time to complete a task based on history"""
        # Get similar tasks from history
        task = self.tasks[task_id]
        similar_tasks = [t for t in self.tasks 
                         if t.category == task.category 
                         and t.priority == task.priority 
                         and t.completed]
        
        if not similar_tasks:
            return "Insufficient data for prediction"
        
        # Collect actual durations if available
        durations = []
        for t in similar_tasks:
            if t.start_time and t.end_time:
                duration = (t.end_time - t.start_time).total_seconds() / 60
                durations.append(duration)
        
        # If we have actual durations, use them
        if durations:
            avg_minutes = sum(durations) / len(durations)
        else:
            # Fallback to priority-based estimation
            avg_minutes = {"high": 30, "medium": 60, "low": 120}[task.priority]
        
        hours, minutes = divmod(int(avg_minutes), 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes} minutes"
    
    def get_task_duration(self, task):
        """Calculate task duration"""
        return {"high": 30, "medium": 60, "low": 120}[task.priority]
    
    def analyze_habits(self):
        """Identify recurring patterns in task completion"""
        from collections import defaultdict
        import statistics
        
        # Group tasks by category and day of week
        category_patterns = defaultdict(lambda: defaultdict(int))
        day_patterns = defaultdict(int)
        
        for task in self.tasks:
            if task.completed and task.due_date:
                day = datetime.strptime(task.due_date, "%Y-%m-%d").strftime("%A")
                day_patterns[day] += 1
                category_patterns[task.category][day] += 1
        
        # Find peak productivity days
        peak_day = max(day_patterns, key=day_patterns.get) if day_patterns else "No data"
        
        # Find best categories
        category_report = {}
        for category, days in category_patterns.items():
            if len(days) >= 3:  # Need enough data
                completion_rate = sum(days.values()) / len(self.tasks)
                consistency = statistics.stdev(list(days.values())) if len(days) > 1 else 0
                category_report[category] = {
                    "completion_rate": completion_rate,
                    "consistency": consistency,
                    "peak_day": max(days, key=days.get)
                }
        
        return {
            "peak_day": peak_day,
            "categories": category_report
        }