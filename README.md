# Ultimate To-Do List Manager

**Professional Task Management System with AI Integration**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

![ToDo CLI Screenshot](todopic.PNG) 

## Overview
A sophisticated task management system that combines traditional to-do list functionality with AI-powered features. This application helps professionals manage tasks efficiently through a CLI interface with voice control capabilities, natural language processing, and productivity insights.

## Key Features

### 🧠 AI-Powered Productivity
- **Auto-Categorisation**: AI assigns categories to new tasks using GPT-3.5
- **Predictive Time Estimates**: Forecasts task completion time based on historical data
- **Habit Analysis**: Identifies productivity patterns using statistical analysis

### 🗣️ Voice Interface
- Voice command recognition for hands-free task management
- Supported commands: 
  - Add tasks ("Add buy milk tomorrow")
  - Complete tasks ("Complete task 3")
  - Check status ("What are my tasks?")

### 📊 Advanced Task Management
- Priority levels (High/Medium/Low) with color-coding
- Custom categories and tags
- Due dates with overdue highlighting
- Detailed productivity statistics and visualisations
- CSV export functionality

### 🔍 Smart Search & NLP
- Natural Language Processing for task creation ("Call client at 3pm tomorrow high priority")
- Advanced search filters:
  - Category/tag filtering
  - Priority-based search
  - Due date ranges

## Technical Implementation

### Architecture
```mermaid
graph TD
    A[CLI Interface] --> B[TodoList Controller]
    B --> C[Task Management]
    B --> D[Storage Handler]
    B --> E[Voice Interface]
    B --> F[AI Assistant]
    F --> G[OpenAI API]
    E --> H[Speech Recognition]
```

## Core Components

1. Task Management Engine (app.py)
    - CRUD operations for tasks
    - Statistical analysis and reporting
    - Predictive time estimation algorithm
2. AI Integration (ai_assistant.py)
    - GPT-3.5 powered suggestions
    - Automatic task categorisation
3. Voice Control (voice_interface.py)
    - Speech-to-text command processing
    - Background listening thread
4. Natural Language Processing (nlp_processor.py)
    - Date/time extraction
    - Priority detection
    - Command parsing
5. Persistent Storage (storage.py)
    - JSON-based task storage
    - Datetime serialisation/deserialisation
  
## Installation
```bash
# Clone repository
git clone https://github.com/706245-hash/Ultimate_To-Do_List_Manager.git

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```
## Usage Example
```text
=== ULTIMATE TO-DO LIST MANAGER ===
1. Add Task
2. View Tasks
3. Edit Task
4. Toggle Complete
5. Delete Task
6. Search/Filter Tasks
7. View Statistics
8. Export to CSV
9. Exit
v. Voice Control

Enter choice: 1
Enter task: Prepare quarterly report due next Monday high priority

✓ Added: Prepare quarterly report
  Due: 2023-12-18
  Priority: high
  Category: Work
  Predicted time: 2h 15m
```
## Technology Stack
- Core Language: Python 3.8+
- Libraries:
    - speech_recognition for voice interface
    - pyttsx3 for text-to-speech
    - dateparser for NLP date handling
    - scikit-learn for predictive analytics
- AI Services: OpenAI GPT-3.5 API
- Data Storage: JSON format with custom serialisation
