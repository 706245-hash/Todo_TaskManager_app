import os
import openai
from dotenv import load_dotenv

class AIAssistant:
    """GPT-powered task intelligence"""
    
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Fixed security vulnerability
        self.prompt = """
        You are an expert productivity assistant. The user has a to-do list with these tasks:
        {tasks}
        
        Your job is to provide helpful suggestions based on the current list and the user's request.
        """
    
    def get_suggestions(self, tasks, query):
        """Get AI suggestions for task management"""
        try:
            task_list = "\n".join([f"- {t.description} ({'done' if t.completed else 'pending'})" for t in tasks])
            full_prompt = self.prompt.format(tasks=task_list) + f"\nUser request: {query}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful productivity assistant."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=150
            )
            
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"AI service unavailable: {str(e)}"
    
    def auto_categorize(self, task_description):
        """Automatically categorize tasks using AI"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a task categorization assistant. Suggest ONE category for this task."},
                    {"role": "user", "content": f"Task: {task_description}\nCategory:"}
                ],
                max_tokens=20,
                temperature=0.3
            )
            return response.choices[0].message['content'].strip()
        except:
            return "General"