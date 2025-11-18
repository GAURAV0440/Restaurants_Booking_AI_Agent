import json
from agent import tools

def execute_tool(tool_name, arguments):

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON argument format: {str(e)}"}
        except Exception as e:
            return {"error": f"Argument parsing error: {str(e)}"}
    
    if not isinstance(arguments, dict):
        return {"error": "Arguments must be a dictionary/object"}

    try:
        func = getattr(tools, tool_name)
    except AttributeError:
        return {"error": f"Tool '{tool_name}' not found in available tools"}

    try:
        result = func(**arguments)
        if result is None:
            return {"error": "Tool returned no result"}
        return result
    except TypeError as e:
        return {"error": f"Invalid arguments for tool '{tool_name}': {str(e)}"}
    except Exception as e:
        return {"error": f"Tool execution error in '{tool_name}': {str(e)}"}
