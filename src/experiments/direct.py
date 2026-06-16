from src.llms import invoke_with_json


def direct(model, data):
    format_output = {
        "type": "object",
        "properties": {
            "label": {"type": "string", "enum": ["supported", "not_supported"]},
            "explanation": {"type": "string"},
        },
        "required": ["label", "explanation"],
    }
    prompt = f"""
    You are a truth detecting machine, your task is given a claim, tell that is it Supported or Non-supported. Supported means truthfull and non-supported is non-truthful.
    Return your answer in JSON format as:
    {{
      "label": "<supported|not_supported>",
      "explanation": "<step-by-step explanation including subclaims and their evaluation>"
    }}
    
    This is the claim:
    \"\"\"
    {data}
    \"\"\"
    """
    return invoke_with_json(model_name=model, prompt=prompt, json_schema=format_output)
