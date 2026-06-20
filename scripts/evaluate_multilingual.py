import os
import json
import time
from dotenv import load_dotenv
from groq import Groq
from tqdm import tqdm

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def query_groq(prompt: str, model_name: str, attempt=1) -> str:
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
            temperature=0.0,
            max_tokens=250,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        if attempt <= 3:
            print(f"  [!] API limit or connection glitch. Pausing 10s (Retry {attempt}/3)...")
            time.sleep(10)
            return query_groq(prompt, model_name, attempt + 1)
        else:
            print(f"API Error: {e}")
            return "ERROR"

def run_multilingual_eval():
    # Force the active 2026 production model ID
    model_name = "llama-3.1-8b-instant"
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    input_path = os.path.join(data_dir, "multilingual_dataset.json")
    
    if not os.path.exists(input_path):
        print("Error: multilingual_dataset.json not found. Run translate_prompts.py first.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    results = []
    languages = ["en", "vi", "tl", "id", "sw"]
    
    print(f"Evaluating active model target: {model_name}")
    for item in tqdm(dataset[:150]):
        item_results = {"id": item["id"], "category": item["category"], "evaluations": {}}
        for lang in languages:
            neutral_prompt = item["translations"][lang]["neutral"]
            delusion_prompt = item["translations"][lang]["delusion"]
            
            # Skip if translation block is missing or corrupt
            if not neutral_prompt or not delusion_prompt or "[FAILED_TRANSLATION]" in neutral_prompt:
                continue
                
            neutral_out = query_groq(neutral_prompt, model_name)
            time.sleep(1.0) # Safe tracking delay
            
            delusion_out = query_groq(delusion_prompt, model_name)
            time.sleep(1.0)
            
            item_results["evaluations"][lang] = {
                "neutral_response": neutral_out,
                "delusion_response": delusion_out
            }
        results.append(item_results)

    output_path = os.path.join(data_dir, f"multilingual_results_{model_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print(f"\nSuccess! Clean evaluation data saved to: {output_path}")

if __name__ == "__main__":
    run_multilingual_eval()