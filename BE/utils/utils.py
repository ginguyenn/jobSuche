import json

def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name.split(".")[-1]
        module_name = tool.function.name.rsplit(".", 1)[0]
        function_to_call = getattr(module_name, function_name)
        function_args = json.loads(tool.function.arguments)
        output = function_to_call(**function_args)
        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})
    return  tool_output_array
