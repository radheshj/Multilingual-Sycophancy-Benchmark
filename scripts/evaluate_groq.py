import os
import json
import time
from dotenv import load_dotenv
from groq import Groq
from tqdm import tqdm

# Load environment variables from your .env file
load_dotenv()

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GROQ_API_KEY not found in environment or .env file.")

client = Groq(api_key=api_key)

def query_groq(prompt: str, model_name: str = "llama3-8b-8192") -> str:
    """
    Sends a prompt to GroqCloud and safely returns the text response.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
            temperature=0.0,  # Greedy decoding to make evaluations reproducible
            max_tokens=300,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"\n[API Error] Failed to fetch response from model {model_name}: {e}")
        return "ERROR_OR_RATE_LIMIT"

def run_evaluation(model_name: str = "llama3-8b-8192"):
    """
    Loads the generated base dataset, evaluates both neutral and delusion prompts,
    and logs the raw outputs to a structured results JSON.
    """
    dataset_path = "data/base_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"Error: Base dataset not found at {dataset_path}. Run generate_dataset.py first.")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    results = []
    print(f"Starting evaluation on Groq model: {model_name}")
    
    # Loop over items with progress bar
    for item in tqdm(items):
        # 1. Test Neutral baseline
        response_neutral = query_groq(item["english_neutral"], model_name)
        time.sleep(0.5) # Avoid aggressive rate limiting on free tier
        
        # 2. Test Delusion context (Sycophancy Trap)
        response_delusion = query_groq(item["english_delusion"], model_name)
        time.sleep(0.5)

        evaluation_record = {
            "id": item["id"],
            "category": item["category"],
            "prompts": {
                "neutral": item["english_neutral"],
                "delusion": item["english_delusion"]
            },
            "ground_truth": {
                "correct": item["correct_answer"],
                "delusional": item["delusional_answer"]
            },
            "model_responses": {
                "neutral_output": response_neutral,
                "delusion_output": response_delusion
            }
        }
        results.append(evaluation_record)

    # Save outputs to data directory
    output_filename = f"data/results_{model_name.replace('/', '_')}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print(f"\n Evaluation complete. Results exported to {output_filename}")

if __name__ == "__main__":
    # Feel free to change model name to 'llama3-70b-8192' to test scaling effects
    run_evaluation(model_name="llama3-8b-8192")