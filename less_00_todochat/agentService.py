import os
from groq import Groq
from todoService import TodoService
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)
todo = TodoService()


def agent(query):

    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Adding new task to the tasks array",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "task description",
                        }
                    },
                    "required": ["description"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Get al existing tasks",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Updating existing task by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The unique ID of the task to update",
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description text for the task. Leave empty if not changing.",
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Set to true if the task is finished, false otherwise.",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Deleting task from tasks array by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The unique ID of the task to delete",
                        }
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to a TODO list. Use the provided tools to manage tasks.",
        },
        {"role": "user", "content": query},
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "add_task":
                result = todo.add_task(function_args.get("description"))
            elif function_name == "get_tasks":
                result = todo.get_tasks()
            elif function_name == "update_task":
                result = todo.update_task(
                    task_id=function_args.get("task_id"),
                    description=function_args.get("description"),
                    completed=function_args.get("completed"),
                )
            elif function_name == "delete_task":
                result = todo.delete_task(function_args.get("task_id"))
            else:
                result = {"error": "Function not found"}

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result),
                }
            )

        second_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages
        )
        return second_response.choices[0].message.content

    return response_message.content
