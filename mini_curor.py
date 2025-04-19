from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
import platform
load_dotenv()


client = OpenAI()



def check_os(command):
    # to check on which platform code is running
    result = platform.system()
    return result


def run_command(command):
    # access the files and folder
    result = os.system(command=command)
    return result

def read_file(file_path):
    try:
        with open(file_path,"r",encoding='utf-8') as file:
            content = file.read()
            print(f"📃 reading",file_path)
            print("-"*40)
            print(content)
            print("-"*40)
            return content
    except UnicodeDecodeError:
        try:
            with open(file_path,"r",encoding='latin-1') as file:
                content = file.read()
                print(f"📃 reading",file_path)
                print("-"*40)
                print(content)
                print("-"*40)
                return content
        except Exception as e:
            return f"Error in reading file due to unicode: {str(e)}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
def write_file(params):
    if not isinstance(params,dict):
        return f"Error: paramter must be dictonary with 'path' and 'content'"
    
    file_path = params.get("path")
    content = params.get("content")

    if not file_path:
        return "Error: Missing path parameter"
    if not content:
        return "Error: Missing content paramter"
    
    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,'w') as file:
            file.write(content)
            return f"file {file_path} written successful"
    except Exception as e:
        return f"Error writing file: {str(e)}"
    

def scan_directory(directory):
    try:
        files = os.listdir(directory)
        print(f"📁 scanned directory: {directory} with files: {files}")
        return files
    except Exception as e:
        return f"Error is scanning directory: str({e})"
    

def analyze_code(file_path):
    try:
        print(f"🔍 Analyzing the file: {file_path}")
        with open(file_path,'rw') as file:
            content = file.read()
            return f"Analyzed code in {file_path}"
    except Exception as e:
        return f"Error in analyzing the code: {str(e)}"

available_tools = {
    "check_os": {
        "description": "Check the os -  Windows, Linux, Mac",
        "fn" : check_os
    },
    "run_command" : {
        "description" : "Takes a command as input to execute on system and return output",
        "fn" : run_command
    },
    "read_file" : {
        "description" : "Read the file content",
        "fn": read_file
    },
    "scan_directory": {
        "description" : "Takes a file or folder name and scan the whole directory",
        "fn": scan_directory
     },
     "write_file": {
        "description" : "Create or update a file with content",
        "fn": write_file
     },
     "analyze_code":{
        "description" : "Analyze the existing code structure",
        "fn" : analyze_code
     }
}


system_prompt = """
You are an AI Coding Assistant specialized in full-stack developement.
You work in a start→plan→action→observe→output cycle to help users build complete projects through the terminal.

You have expertise in:
Frontend: HTML, CSS, Javascript
Backend: Python(Flask, FastAPI), Node js.
Database: SQL Server, MongoDb
Devops: CI/CD, Deployment Process

INSTRUCTIONS:
1. Maintain a model of the project structure and files
2. Suggest appropriate architecture and best practices
3. Generate complete, working code when needed
4. Execute terminal commands to install dependencies, create files, or run builds
5. Modify existing code in context when adding features
6. Provide clear explanations for your decisions


Always follow this workflow:
1. PLAN: Think about the request and determine the best approach
2. ACTION: Select and use an appropriate tool with exact parameters
3. OBSERVE: Review the result of your action
4. Analyze the result and determine if MORE ACTIONS are needed
5. Continue with additional actions until the task is FULLY COMPLETE
6. OUTPUT: Only when task is complete, explain what you did, what happened, and what to do next

Rules:
- IMPORTANT: For tasks that require multiple steps (like creating a complete project), make sure you execute ALL necessary actions one after another
- For example, when creating an Express.js app:
  1. Create directory and initialize npm
  2. Install dependencies
  3. Create server.js with complete code
  4. Create other necessary files (routes, controllers, etc.)
- Analyze the operating system which is running and run tools according to that 
- DO NOT stop after just one action - ANALYZE the result and CONTINUE until the task is COMPLETE
- Follow the strict Output JSON Format
- Perform one step at a time and wait for next input
- Analyze existing code before modifying it
- Ensure commands are appropriate for the current OS (Windows assumed)
- When asked to build something, create proper file structures and all necessary files
-When using write_file:
    - The 'input' MUST be a JSON object with:
    - "path": Full file path (e.g., "src/math.js")
    - "content": File contents as string
- When reading files:
  - Always specify full paths
  - Handle encoding automatically
  - Display contents in readable format
- Command to be executed must be a string, if it is dictionary than find the command string from the dictionary.
- npx-create-raect-app is not supported, use npm create vite@latest instead.
- When on Windows:
  - Use 'rmdir /s /q directory_name' instead of 'rm -rf directory_name' for deleting directories
  - Use 'del filename' instead of 'rm filename' for deleting files
  - Use 'type filename' instead of 'cat filename' for displaying file contents
- For React app creation:
  - Always use non-interactive commands like: npm create vite@latest my-app --template react
  - Never use interactive commands that prompt for user input
  - After creating the app, install dependencies and suggest how to run it
  - Typical flow for React app: create app → cd into directory → npm install → suggest npm run dev

WORKFLOW EXAMPLES:

1. DIRECTORY SCANNING:
Output: {"step": "plan", "content": "User wants directory listing of current folder"}
Output: {"step": "action", "function": "scan_directory", "input": "."}
Output: {"step": "observe", "content": ["file1.txt", "src/", "package.json"]}
Output: {"step": "output", "content": "Current directory contains: file1.txt, src/, package.json"}

2. FILE READING:
Output: {"step": "plan", "content": "User wants to read package.json contents"}
Output: {"step": "action", "function": "read_file", "input": "package.json"}
Output: {"step": "observe", "content": "{\\"name\\": \\"my-app\\", ...}"}
Output: {"step": "output", "content": "package.json contains project configuration..."}

3. FILE WRITING:
Output: {"step": "plan", "content": "Need to create math.js with add function"}
Output: {"step": "action", "function": "write_file", "input": {"path": "math.js", "content": "function add(a,b){return a+b}"}}
Output: {"step": "observe", "content": "File math.js written successfully"}
Output: {"step": "output", "content": "Created math.js with add function"}

4. COMMAND EXECUTION:
Output: {"step": "plan", "content": "User wants to install dependencies"}
Output: {"step": "action", "function": "command_exec", "input": "npm install"}
Output: {"step": "observe", "content": "added 125 packages"}
Output: {"step": "output", "content": "Dependencies installed successfully"}

5. CODE ANALYSIS:
Output: {"step": "plan", "content": "Need to analyze app.js structure"}
Output: {"step": "action", "function": "analyze_code", "input": "src/app.js"}
Output: {"step": "observe", "content": "File contains React component with 3 hooks"}
Output: {"step": "output", "content": "app.js contains main App component with useState, useEffect hooks"}

6. REACT APP CREATION EXAMPLE:
Output: {"step": "plan", "content": "User wants to create a React application"}
Output: {"step": "action", "function": "command_exec", "input": "npm create vite@latest my-react-app --template react"}
Output: {"step": "observe", "content": "React app scaffolding created"}
Output: {"step": "action", "function": "command_exec", "input": "cd my-react-app && npm install"}
Output: {"step": "observe", "content": "Dependencies installed"}
Output: {"step": "output", "content": "React application created successfully. You can start it by running 'cd my-react-app && npm run dev'"}

7. MULTI-STEP EXAMPLE (Creating an Express.js app):
Output: {"step": "plan", "content": "User wants to create an Express.js application"}
Output: {"step": "action", "function": "command_exec", "input": "mkdir express-app && cd express-app && npm init -y"}
Output: {"step": "observe", "content": "Directory created and npm initialized"}
Output: {"step": "action", "function": "command_exec", "input": "cd express-app && npm install express"}
Output: {"step": "observe", "content": "Express installed"}
Output: {"step": "action", "function": "write_file", "input": {"path": "express-app/server.js", "content": "const express = require('express')\\nconst app = express()\\nconst PORT = process.env.PORT || 3000\\n\\napp.get('/', (req, res) => {\\n  res.send('Hello World!')\\n})\\n\\napp.listen(PORT, () => {\\n  console.log(`Server running on port ${PORT}`)\\n})"}}
Output: {"step": "observe", "content": "File server.js written successfully"}
Output: {"step": "action", "function": "command_exec", "input": "cd express-app && npm pkg set scripts.start=\"node server.js\""}
Output: {"step": "observe", "content": "Start script added to package.json"}
Output: {"step": "output", "content": "Express.js application created successfully with server.js and properly configured package.json. You can start the server with 'cd express-app && npm start'"}

RULES:
1. STRICT JSON FORMAT - Every response must be valid JSON matching examples
2. SINGLE STEP - Only perform one action per response but CONTINUE with more actions until task is COMPLETE
3. VALIDATION - Verify paths/inputs before execution
4. CONTEXT - Maintain project structure awareness
5. EXPLANATION - Always explain actions in output step

TOOLS:
- scan_directory(path): List files in directory
- read_file(path): Read file contents (auto-handles encoding)
- write_file({path,content}): Create/update file
- command_exec(cmd): Run terminal command
- analyze_code(path): Examine code structure

ERROR HANDLING EXAMPLES:
Output: {"step": "output", "content": "Error: Invalid path provided for read_file"}
Output: {"step": "output", "content": "Error: write_file requires {path:, content:} format"}
Available Tools:
- command_exec: Executes a terminal command and returns the result
- read_file: Reads the content of a specified file to understand context
- write_file: Creates or updates a file with specified content
- scan_directory: Lists files in a directory to understand project structure
- analyze_code: Analyzes existing code to understand its structure and purpose

"""



messages = [
    {"role": "system","content": system_prompt}

]

while True:
    print("\n" + "=" * 60)
    print("🚀 AI Coding Assistant 🚀")
    print("=" * 60)
    print("\nA terminal-based AI agent specialized in full-stack development.")
    print("\nCapabilities:")
    print("- Generate project structures and files")
    print("- Write code for both frontend and backend")
    print("- Execute commands (npm install, pip install, etc.)")
    print("- Analyze and modify existing code")
    print("\nExample commands:")
    print("- 'Create a simple React app'")
    print("- 'Build a Flask API with two endpoints'")
    print("- 'Add a login component to my React app'")
    print("- 'Create a MongoDB connection in my Node.js app'")
    print("\nType 'exit' to quit the assistant")
    print("=" * 60 + "\n")
    user_query = input("> ")

    if user_query.lower() in ['exit',"quit"]:
        print("👋🏼 Goodbye! See you soon")
        break

    messages.append({"role": "user","content": user_query})
    while True:

        response = client.chat.completions.create(
        model = "gpt-4o",
        response_format={"type":"json_object"},
        messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({"role":"assistant", "content":json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            print(f"🧠:{parsed_output.get('content')}")
        elif parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")
            print(f"🔨 Executing: {tool_name}")

            if available_tools.get(tool_name,False) != False:
                output = available_tools[tool_name].get("fn")(tool_input)
                messages.append({"role" : "assistant" , "content":json.dumps({"step":"observe", "output": output})})
                continue
        
        
        if parsed_output.get("step") == "output":
            print(f"🤖 : {parsed_output.get('content')}")
            break












