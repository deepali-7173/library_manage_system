from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

api = FastAPI()

all_todos = [
    {'todo_id': '1', 'todo_name': 'Sports', 'todo_description': 'go to gym'},
    {'todo_id': '2', 'todo_name': 'Read', 'todo_description': 'read 10 pages'},
    {'todo_id': '3', 'todo_name': 'Shop', 'todo_description': 'go for shopping'},
    {'todo_id': '4', 'todo_name': 'Study', 'todo_description': 'study for exams'}
]

class Todo(BaseModel):
    todo_name: str
    todo_description: str

@api.get('/')
def index():
    return {"message": "hello"}

@api.get('/todos/{todo_id}')
def get_todo(todo_id: int):
    for todo in all_todos:
        if int(todo['todo_id']) == todo_id:
            return {"result": todo}
    return {"error": "Todo not found"}

@api.post('/todos')
def create(todo: Todo):
    new_todo_id = str(int(all_todos[-1]['todo_id']) + 1)  
    new_todo = {
        'todo_id': new_todo_id,
        'todo_name': todo.todo_name,
        'todo_description': todo.todo_description
    }
    all_todos.append(new_todo)
    return new_todo

    

