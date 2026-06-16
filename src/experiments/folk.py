import json

from src.llms import invoke_with_json
from src.utils import google_top_snippet


def create_fol_subclaim(model, claim):
    format_output = {
        "type": "object",
        "properties": {"response": {"type": "string"}},
        "required": ["response"],
    }
    prompt = f"""
    You are given a problem description and a claim. The task is to define all the predicates in the claim and return in JSON format like in example. Below is the claim:
    {claim}
   
    Below is example
    Claim: Howard University Hospital and Providence Hospital are both located in Washington, D.C.
    >>>>>>
    {{
        "response": "Predicates:\n1. Location(Howard_University_Hospital, Washington_D.C.) ::: Verify Howard University Hospital is located in Washington, D.C.\n2. Location(Providence_Hospital, Washington_D.C.) ::: Verify Providence Hospital is located in Washington, D.C.\n\nFollowup Question: Where is Howard University Hospital located?\nFollowup Question: Where is Providence Hospital located?"
    }}
    ------
    Claim: In 1959, former Chilean boxer Alfredo Cornejo Cuevas (born June 6, 1933) won the gold medal in the welterweight division at the Pan American Games (held in Chicago, United States, from August 27 to September 7) in Chicago, United States, and the world amateur welterweight title in Mexico City.
    >>>>>>
    {{
        "response": "Predicates:\n1. Born(Alfredo Cornejo Cuevas, June 6 1933) ::: Verify that Alfredo Cornejo Cuevas was born June 6, 1933.\n2. Won(Alfredo Cornejo Cuevas, the gold medal in the welterweight division at the Pan American Games in 1959) ::: Verify that Alfredo Cornejo Cuevas won the gold medal in the welterweight division at the Pan American Games in 1959.\n3. Held(The Pan American Games in 1959, Chicago United States) ::: Verify that The Pan American Games in 1959 was held in Chicago, United States.\n4. Won(Alfredo Cornejo Cuevas, the world amateur welterweight title in Mexico City).\n\nFollowup Question: When was Alfredo Cornejo Cuevas born?\nFollowup Question: Where were the 1959 Pan American Games held?\nFollowup Question: What title did Alfredo Cornejo Cuevas win in Mexico City?"
    }}
    """
    return invoke_with_json(model_name=model, prompt=prompt, json_schema=format_output)


def create_a_question(model, claim, k):
    format_output = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "claim": {"type": "string"},
                "questions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["claim", "questions"],
        },
    }
    prompt = f"""
    For each input subclaim, generate {k} Google search questions that could be used to find evidence to verify the subclaim.
    The questions should be diverse, exploring different aspects or perspectives related to the subclaim, but still ensure simple and straightforward. There are some tips:
    1. Use specific keywords.
    2. Include synonyms and related terms.
    3. Balance broad and long-tail keywords.
   
    Return the output in JSON format like this [{{"claim": "Location(Howard Hospital, Washington D.C.) ::: Verify Howard University Hospital is located in Washington, D.C.", "questions": ["Where is Howard Hospital located?"]}}]
 
    Below are given claims
    {claim}
    """
    return invoke_with_json(model_name=model, prompt=prompt, json_schema=format_output)


def folk(model, data):
    fol_response = create_fol_subclaim(model, data)
    fol_output = fol_response["response"]

    followup_questions = []
    for line in fol_output.split("\n"):
        if line.startswith("Followup Question:"):
            question = line.replace("Followup Question:", "").strip()
            followup_questions.append(question)

    evidence = []
    for ques in followup_questions:
        try:
            snippet = google_top_snippet(ques)
        except Exception as e:
            snippet = f"Error fetching evidence: {str(e)}"
        evidence.append({"question": ques, "evidence": snippet})

    prompt_predict = f"""
    You are an AI assistant responsible for determining whether a subclaim is supported by retrieved evidence.  

    ## Provided Information:
    This is a claim to do fact-checking:  
    {data}
    Here are its subquestions, and retrieved evidence for each subquestion:  
    {json.dumps(evidence, indent=2)}  

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

    format_output = {
        "type": "object",
        "properties": {
            "label": {"type": "string", "enum": ["supported", "not_supported"]},
            "explanation": {"type": "string"},
        },
        "required": ["label", "explanation"],
    }

    return invoke_with_json(model_name=model, prompt=prompt_predict, json_schema=format_output)
