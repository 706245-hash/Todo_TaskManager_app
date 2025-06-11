from src.ai_assistant import AIAssistant
from src.nlp_processor import NLPProcessor
from src.voice_interface import VoiceAssistant
from datetime import datetime
from .app import TodoList
import threading

class TodoCLI:
    """Enhanced CLI with colors, task editing, and better display"""
    
    # ANSI color codes
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    
    PRIORITY_COLORS = {
        "high": "red",
        "medium": "yellow",
        "low": "green"
    }
    
    def __init__(self):
        self.todo = TodoList()
        self.ai_assistant = AIAssistant()
        self.nlp_processor = NLPProcessor()
        self.voice_interface = VoiceAssistant(self.todo)
        self.commands = {
            "1": ("Add Task", self.add_task),
            "2": ("View Tasks", self.view_tasks),
            "3": ("Edit Task", self.edit_task),
            "4": ("Toggle Complete", self.toggle_completed),
            "5": ("Delete Task", self.delete_task),
            "6": ("Search/Filter Tasks", self.search_tasks),
            "7": ("View Statistics", self.show_stats),
            "8": ("Export to CSV", self.export_tasks),
            "9": ("Exit", self.exit_app)
        }
        self.commands["0"] = ("AI Assistant", self.ai_assistant_mode) #under construction
        self.commands["v"] = ("Voice Control", self.toggle_voice) #under construction
        self.voice_active = False
        self.voice_lock = threading.Lock()

    
    def color_text(self, text, color):
        """Apply color to text if supported"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}" if self.COLORS else text

    def display_menu(self):
        """Show enhanced main menu"""
        with self.voice_lock:
            voice_status = "ON" if self.voice_active else "OFF"
        title = f" TO-DO LIST MANAGER (Voice: {voice_status}) "
        print("\n" + "="*10 + self.color_text(title, "blue") + "="*10)
        for key, (label, _) in self.commands.items():
            print(f"{key}. {label}")
        print("="*40)
    
    def add_task(self):
        """Enhanced task adding with NLP"""
        description = input("Enter task: ").strip()
        
        # Try natural language processing
        if " " in description and any(word in description.lower() for word in ["tomorrow", "today", "at", "on", "next"]):
            try:
                details = self.nlp_processor.parse_command(description)
                description = details["description"]
                due_date = details["due_date"]
                priority = details["priority"]
                
                # Auto-categorize with AI
                category = self.ai_assistant.auto_categorize(description)
                
                self.todo.add_task(
                    description, 
                    due_date=due_date,
                    priority=priority,
                    category=category
                )
                
                # Show prediction
                prediction = self.todo.predict_completion_time(len(self.todo.tasks)-1)
                
                print(self.color_text(f"✓ Added: {description}", "green"))
                print(self.color_text(f"  Due: {due_date or 'No deadline'}", "blue"))
                print(self.color_text(f"  Priority: {priority}", "yellow"))
                print(self.color_text(f"  Category: {category}", "cyan"))
                print(self.color_text(f"  Predicted time: {prediction}", "magenta"))
                return
            except Exception as e:
                print(self.color_text(f"NLP failed: {e}", "red"))

        #manual input
        description = input("Enter task description: ").strip()
        if not description:
            print(self.color_text("Error: Description cannot be empty!", "red"))
            return
            
        category = input("Category [optional]: ").strip() or "General"
        tags_input = input("Tags (comma separated) [optional]: ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        priority = self.get_priority()
        due_date = self.get_due_date()
        
        self.todo.add_task(
            description, 
            priority=priority, 
            due_date=due_date,
            category=category,
            tags=tags
        )
        print(self.color_text(f"✓ Added: {description}", "green"))
    
    def get_priority(self):
        """Prompt for priority level"""
        while True:
            priority = input("Priority [high/medium/low] (default=medium): ").strip().lower()
            if not priority:
                return "medium"
            if priority in ["high", "medium", "low"]:
                return priority
            print(self.color_text("Invalid priority! Choose high, medium, or low", "red"))
    
    def get_due_date(self):
        """Prompt for due date with validation"""
        while True:
            date_str = input("Due date (YYYY-MM-DD) [optional]: ").strip()
            if not date_str:
                return None
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                print(self.color_text("Invalid date format! Use YYYY-MM-DD", "red"))

    def search_tasks(self):
        """Advanced task search interface"""
        print("\n" + self.color_text("=== SEARCH TASKS ===", "blue"))
        
        # Get search criteria
        search_term = input("Search term [optional]: ").strip()
        category = input("Category [optional]: ").strip() or None
        tags_input = input("Tags (comma separated) [optional]: ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else None
        
        priority = None
        if input("Filter by priority? (y/n): ").lower() == "y":
            priority = self.get_priority()
            
        due_within = None
        if input("Show tasks due within days? (enter number or skip): ").strip():
            try:
                due_within = int(input("Due within how many days? "))
            except ValueError:
                print(self.color_text("Invalid number!", "red"))
                return
        
        # Perform search
        results = self.todo.search_tasks(
            search_term=search_term,
            category=category,
            tags=tags,
            priority=priority,
            due_within=due_within
        )
        
        # Display results
        if not results:
            print(self.color_text("\nNo tasks match your criteria", "yellow"))
            return
            
        print(self.color_text(f"\nFound {len(results)} tasks:", "green"))
        for i, task in enumerate(results):
            status = "✓" if task.completed else "◻"
            print(f"{i}. [{status}] {task.description} ({task.category})")
            if task.tags:
                tags_display = ", ".join(task.tags)
                print(f"   Tags: {tags_display}")
            if task.due_date:
                print(f"   Due: {task.due_date}")
    
    def view_tasks(self):
        """Display tasks with all attributes"""
        tasks = self.todo.view_tasks(sort_by="due_date")
        
        if not tasks:
            print(self.color_text("No tasks found!", "yellow"))
            return
            
        print("\n" + self.color_text("YOUR TASKS:", "blue"))
        print("-" * 70)
        print(f"{'ID':<3} | {'Status':<6} | {'Priority':<8} | {'Due':<12} | {'Category':<15} | Description")
        print("-" * 70)
        
        for i, task in enumerate(tasks):
            # Status indicator
            status = self.color_text("✓ DONE", "green") if task.completed else self.color_text("TODO", "red")
            
            # Priority with color coding
            priority_color = self.PRIORITY_COLORS.get(task.priority, "reset")
            priority_display = self.color_text(task.priority.upper(), priority_color)
            
            # Due date with warning for overdue
            due_display = task.due_date or "-"
            if task.due_date and not task.completed:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due_date < datetime.now().date():
                    due_display = self.color_text(task.due_date + "!", "red")
            
            # Category
            category_display = task.category[:15] + "..." if len(task.category) > 15 else task.category
            
            print(f"{i:<3} | {status:<6} | {priority_display:<8} | {due_display:<12} | {category_display:<15} | {task.description}")
            
            # Show tags if they exist
            if task.tags:
                tags_display = ", ".join(task.tags)
                print(f"   Tags: {tags_display}")
    
    def show_stats(self):
        """Display productivity statistics"""
        stats = self.todo.get_stats()
        
        print("\n" + self.color_text("=== PRODUCTIVITY STATISTICS ===", "blue"))
        print(f"Total tasks: {stats['total']}")
        print(f"Completed: {stats['completed']} ({stats['completion_pct']:.1f}%)")
        print(f"Overdue: {stats['overdue']}")
        
        # Priority distribution
        print("\n" + self.color_text("Priority Distribution:", "yellow"))
        for priority, count in stats["by_priority"].items():
            pct = (count / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"- {priority.capitalize()}: {count} ({pct:.1f}%)")
        
        # Category distribution
        if stats["by_category"]:
            print("\n" + self.color_text("Category Distribution:", "yellow"))
            for category, count in stats["by_category"].items():
                pct = (count / stats["total"] * 100) if stats["total"] > 0 else 0
                print(f"- {category}: {count} ({pct:.1f}%)")
        
        # Progress bar visualization
        if stats["total"] > 0:
            bar_length = 30
            completed_bar = "█" * int(bar_length * stats["completion_pct"] / 100)
            remaining_bar = " " * (bar_length - len(completed_bar))
            print("\n" + self.color_text("Progress:", "green"))
            print(f"[{completed_bar}{remaining_bar}] {stats['completion_pct']:.1f}%")

        # Habit analysis
        habits = self.todo.analyze_habits()
        print("\n" + self.color_text("HABIT ANALYSIS:", "magenta"))
        print(f"Your most productive day: {habits['peak_day']}")
        
        if habits['categories']:
            print("\nCategory Performance:")
            for category, data in habits['categories'].items():
                print(f"- {category}:")
                print(f"  Completion: {data['completion_rate']*100:.1f}%")
                print(f"  Peak day: {data['peak_day']}")

    def edit_task(self):
        """Edit task with extended attributes"""
        self.view_tasks()
        if not self.todo.tasks:
            return
            
        try:
            task_id = int(input("Enter task ID to edit: "))
            task = self.todo.tasks[task_id]
            
            # Edit description
            new_desc = input(f"New description [{task.description}]: ").strip()
            new_desc = new_desc if new_desc else task.description
            
            # Edit category
            new_category = input(f"New category [{task.category}]: ").strip()
            new_category = new_category if new_category else task.category
            
            # Edit tags
            current_tags = ", ".join(task.tags)
            new_tags_input = input(f"New tags (comma separated) [{current_tags}]: ").strip()
            new_tags = [tag.strip() for tag in new_tags_input.split(",")] if new_tags_input else task.tags
            
            # Edit priority
            print(f"Current priority: {task.priority}")
            new_priority = self.get_priority()
            
            # Edit due date
            print(f"Current due date: {task.due_date or 'None'}")
            new_due_date = self.get_due_date()
            
            # Apply changes
            self.todo.edit_task(
                task_id,
                description=new_desc,
                priority=new_priority,
                due_date=new_due_date,
                category=new_category,
                tags=new_tags
            )
            print(self.color_text("✓ Task updated successfully!", "green"))
            
        except (ValueError, IndexError):
            print(self.color_text("Invalid task ID!", "red"))
    
    def toggle_completed(self):
        """Toggle task completion status"""
        self.view_tasks()
        if not self.todo.tasks:
            return
            
        try:
            task_id = int(input("Enter task ID to toggle: "))
            task = self.todo.tasks[task_id]
            new_status = not task.completed
            self.todo.edit_task(task_id, completed=new_status)
            status = "completed" if new_status else "marked as incomplete"
            print(self.color_text(f"✓ Task {status}!", "green"))
        except (ValueError, IndexError):
            print(self.color_text("Invalid task ID!", "red"))

    def export_tasks(self):
        """Export tasks to CSV file"""
        filename = input("Enter filename [tasks_export.csv]: ").strip() or "tasks_export.csv"
        if not filename.endswith(".csv"):
            filename += ".csv"
            
        try:
            export_path = self.todo.export_csv(filename)
            print(self.color_text(f"✓ Exported {len(self.todo.tasks)} tasks to {export_path}", "green"))
        except Exception as e:
            print(self.color_text(f"Export failed: {str(e)}", "red"))

    def ai_assistant_mode(self):
        """Interactive AI assistant session"""
        print("Under Construction for now")
        # print(self.color_text("\n=== AI PRODUCTIVITY ASSISTANT ===", "magenta"))
        # print("Ask me anything about your tasks or productivity!")
        # print("Type 'exit' to return to main menu\n")
        
        # while True:
        #    query = input("You: ").strip()
        #    if query.lower() == "exit":
        #        return
                
         #   response = self.ai_assistant.get_suggestions(self.todo.tasks, query)
        #    print(self.color_text(f"\nAssistant: {response}\n", "cyan"))

    def toggle_voice(self):
        """Enable/disable voice control with thread safety"""
        print("Under Construction for now")
        #with self.voice_lock:
        #    if not self.voice_active:
        #        try:
        #            self.voice_interface.start()
        #            self.voice_active = True
        #            print(self.color_text("Voice control activated! Try saying 'Add a task'", "green"))
        #            print(self.color_text("Supported commands: 'Add [task]', 'Complete [task number]', 'What are my tasks?', 'Exit'", "blue"))
        #        except Exception as e:
        #            print(self.color_text(f"Failed to activate voice: {str(e)}", "red"))
        #            self.voice_active = False
        #    else:
        #        try:
        #            self.voice_interface.stop()
        #            self.voice_active = False
        #            print(self.color_text("Voice control deactivated", "yellow"))
        #        except Exception as e:
        #            print(self.color_text(f"Failed to deactivate voice: {str(e)}", "red"))
        #            self.voice_active = True
    
    def delete_task(self):
        """Handle task deletion"""
        self.view_tasks()
        try:
            task_id = int(input("Enter task number to delete: "))
            self.todo.delete_task(task_id)
            print("Task deleted!")
        except (ValueError, IndexError):
            print("Invalid task number!")
    
    def exit_app(self):
        """Exit the application"""
        print("Goodbye!")
        exit()
    
    def run(self):
        """Main application loop ( enhanced error handling )"""
        while True:
            try:
                self.display_menu()
                choice = input("Enter choice: ").strip()
                
                if choice in self.commands:
                    _, command = self.commands[choice]
                    command()
                else:
                    print(self.color_text("Invalid choice. Please enter a valid option.", "red"))
                    
            except KeyboardInterrupt:
                print("\n" + self.color_text("Operation cancelled by user", "yellow"))
            except Exception as e:
                print(self.color_text(f"Error: {str(e)}", "red"))
                # Ensure voice state is reset on critical errors
                with self.voice_lock:
                    if self.voice_active:
                        self.voice_interface.active = False
                        self.voice_active = False