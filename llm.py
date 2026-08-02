
import os
import json
import anthropic
from dotenv import load_dotenv
load_dotenv()


client = anthropic.Anthropic()

SAMPLE_ARTICLE = """
NetPurna was founded after seeing too many products designed for systems instead of people
- built to satisfy stakeholders, not the humans who actually use them.
We exist to help product teams build with intention, clarity, and craft -
working inside the problem alongside them, not delivering solutions from the outside.
"""

def process_article(text: str) -> dict:
   
    system_prompt = (
        "You are an expert AI research assistant. Your task is to analyze the provided article "
        "and return a JSON response with three keys:\n"
        '1. "summary": A concise 2-sentence summary.\n'
        '2. "themes": A list of key themes (3-5 items).\n'
        '3. "research_questions": A list of 2-3 insightful research questions.'
    )

    user_prompt = f"Analyze the following article:\n\n{text}"

    # API Call
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.2,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract response text
    raw_content = response.content[0].text

    # Parse JSON output
    try:
        parsed_data = json.loads(raw_content)
        return parsed_data
    except json.JSONDecodeError:
        # Fallback handling in case of formatting quirks
        print("Warning: Raw output was not strict JSON. ")
        return {"raw_output": raw_content}

if __name__ == "__main__":
    
    print("Running LLM Analysis Pipeline...\n")
    results = process_article(SAMPLE_ARTICLE)
    print(json.dumps(results, indent=2))