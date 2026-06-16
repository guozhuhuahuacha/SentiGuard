from src.llms import invoke_with_json


def cot(model, data):
    format_output = {
        "type": "object",
        "properties": {
            "label": {"type": "string", "enum": ["supported", "not_supported"]},
            "explanation": {"type": "string"},
        },
        "required": ["label", "explanation"],
    }
    prompt = f"""
    You are a truth-detecting machine. Your task is to verify whether a given claim is Supported (truthful) or Not Supported (non-truthful).
    
    Follow this Chain of Thought (CoT) process:
    
    1. Break down the main claim into smaller subclaims.
    2. Evaluate each subclaim individually:
       - If a subclaim is factually correct, note it as "supported."
       - If a subclaim is factually incorrect, note it as "not supported."
    3. Based on the evaluation of all subclaims, make a final decision:
       - If all subclaims are supported, the main claim is "supported."
       - If any subclaim is not supported, the main claim is "not_supported."
    
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
