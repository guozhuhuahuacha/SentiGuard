evidence_seeking = {
    "name": "evidence_seeking",
    "description": "Retrieves evidence for subclaims based on generated queries.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "subclaims_with_query_evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "subclaim": {
                            "type": "string",
                            "description": "A subclaim derived from the main claim."
                        },
                        "queries_with_evidence": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "A query generated to seek evidence for the subclaim."
                                    },
                                    "evidence": {
                                        "type": "string",
                                        "description": "All evidences retrieved for the query."
                                    }
                                },
                                "required": ["query", "evidence"],
                                "additionalProperties": False
                            },
                            "description": "A list of queries and their corresponding evidence for the subclaim."
                        }
                    },
                    "required": ["subclaim", "queries_with_evidence"],
                    "additionalProperties": False
                },
                "description": "A list of subclaims, each containing multiple queries with their corresponding evidence."
            }
        },
        "additionalProperties": False,
        "required": ["subclaims_with_query_evidence"]
    }
}

evidence_seeking_prompt = f"""
You are a helpful assistant who extracts information from text.
Given the following query and text content, extract only the sentences or phrases that directly
relate to the query. Do not include any information that is not relevant.
If the content contains no relevant information, return None.
"""

