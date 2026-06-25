import json

from src.main.python.providers.llm import invoke_with_json
from src.main.python.utils import google_top_snippet


def self_ask(model, data):
    format_output = {
        "type": "object",
        "properties": {
            "questions": {"type": "string",
                          "description": "Follow-up questions separated by newline (\\n)."},
        },
        "required": ["questions"],
    }

    prompt = f"""
    You are a critical thinking assistant.
    
    Given a claim, your task is to generate follow-up questions that help:
    - Clarify ambiguous parts,
    - Probe for evidence or examples,
    - Test the truthfulness of the claim.
    
    Guidelines:
    - Ask 3 to 5 questions.
    - Questions should be open-ended and specific.
    - Do not answer the claim; only generate questions.
    
    Return your output in JSON format like this:
    {{
      "questions": "<Question 1>\\n<Question 2>\\n<Question 3>"
    }}
    
    Here is the claim:
    \"\"\"
    {data}
    \"\"\"
    
    Generate the follow-up questions:
    """
    questions_obj = invoke_with_json(model_name=model, prompt=prompt, json_schema=format_output)
    string_questions = questions_obj["questions"]
    lst_questions = string_questions.split("\n")
    lst_questions = [ques for ques in lst_questions if ques]

    evidence = []
    for ques in lst_questions:
        d = {"question": ques}
        d["evidence"] = google_top_snippet(ques)
        evidence.append(d)

    prompt_predict = f"""
    You are an AI assistant responsible for determining whether a subclaim is supported by retrieved evidence.  

    ## Provided Information:
    This is a claim to do fact-checking:  
    \\n {data}
    Here are its subquestions, and retrieved evidence for each subquestion:  
    \\n {json.dumps(evidence, indent=2)}  

    ## Decision-Making Process:

    1. Analyze the Retrieved Evidence  
    2. Apply a Voting System for Classification  
    3. Provide a Justification  

    ## Response Format:
    Your response must be a structured JSON object:  

    {{
        "label": "supported" or "not_supported",
        "explanation": "A concise, evidence-based summary supporting your decision."
    }}
    """
    format_output_predict = {
        "type": "object",
        "properties": {
            "label": {"type": "string", "enum": ["supported", "not_supported"]},
            "explanation": {"type": "string"},
        },
        "required": ["label", "explanation"],
    }
    return invoke_with_json(model_name=model, prompt=prompt_predict,
                            json_schema=format_output_predict)
