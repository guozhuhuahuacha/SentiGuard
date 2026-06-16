verdict_prediction = {
    "name": "verdict_prediction",
    "description": "Predicts whether the input claim is supported based on retrieved evidence.",
    "parameters": {
        "type": "object",
        "properties": {
            "result": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "enum": ["supported", "not_supported"],
                        "description": "The verdict on whether the claim is supported by the evidence."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "A textual explanation justifying the verdict based on the evidence."
                    }
                },
                "required": ["label", "explanation"],
                "additionalProperties": False
            }
        },
        "required": ["result"],
        "additionalProperties": False
    }
}


verdict_prediction_prompt = """
You are an AI assistant responsible for determining whether a subclaim is supported by retrieved evidence.  
 
## Provided Information:
This is a claim to do fact-checking:  
\\n {claim}
Here is the given subclaims, its subquestions, and retrieved evidence for each subquestion:  
\\n {cell}  

## Decision-Making Process:

1. Analyze the Retrieved Evidence  
- Review all provided evidence relevant to the subclaim.  
- Assess the credibility, consistency, and reliability of each piece of evidence.  

2. Apply a Voting System for Classification  
- If multiple sources strongly support the subclaim, classify it as "supported".  
- If multiple sources contradict the subclaim, classify it as "not_supported".  
- If the evidence is mixed, insufficient, or inconclusive, classify it as "not_supported".  

3. Provide a Justification  
- Clearly explain why the subclaim is classified as "supported" or "not_supported".  
- Reference key pieces of evidence that influenced your decision.  
- If the evidence is inconclusive, explain the limitations or uncertainties.  
- Remember to adjust not to include " for later parse
"""