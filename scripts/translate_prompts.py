import os
import json
import time
from dotenv import load_dotenv
from groq import Groq
from tqdm import tqdm

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def translate_to_all(text: str, attempt=1) -> dict:
    prompt = f"""
    You are a precise translator. Translate the following English text into Vietnamese (vi), Tagalog (tl), Bahasa Indonesia (id), and Swahili (sw).
    
    You must output a JSON object matching this exact format:
    {{
        "vi": "Vietnamese translation here",
        "tl": "Tagalog translation here",
        "id": "Bahasa Indonesia translation here",
        "sw": "Swahili translation here"
    }}
    
    English Text to translate: "{text}"
    """
    try:
        # Enforcing Groq's native JSON mode to completely stop markdown backtick bugs
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        response_text = completion.choices[0].message.content.strip()
        return json.loads(response_text)
    except Exception as e:
        if attempt <= 3:
            print(f"  [!] Parsing glitch. Retrying segment in 5 seconds (Retry {attempt}/3)...")
            time.sleep(5)
            return translate_to_all(text, attempt + 1)
        else:
            # Added an obvious tag so you can immediately see if a fallback happens
            print(f"\n[Warning] Using fallback for text: {text[:20]}...")
            return {
                "vi": f"[FAILED_TRANSLATION] {text}", 
                "tl": f"[FAILED_TRANSLATION] {text}", 
                "id": f"[FAILED_TRANSLATION] {text}", 
                "sw": f"[FAILED_TRANSLATION] {text}"
            }

def build_multilingual_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    input_path = os.path.join(data_dir, "base_dataset.json")
    output_path = os.path.join(data_dir, "multilingual_dataset.json")

    if not os.path.exists(input_path):
        print("Error: base_dataset.json not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    multilingual_data = []
    print("Translating items using native JSON validation mode...")
    
    # Running the test slice of 10 items
    for item in tqdm(dataset): 
        translated_neutral = translate_to_all(item["english_neutral"])
        time.sleep(1.0) 
        
        translated_delusion = translate_to_all(item["english_delusion"])
        time.sleep(1.0)
        
        new_item = {
            "id": item["id"],
            "category": item["category"],
            "translations": {
                "en": {"neutral": item["english_neutral"], "delusion": item["english_delusion"]},
                "vi": {"neutral": translated_neutral.get("vi"), "delusion": translated_delusion.get("vi")},
                "tl": {"neutral": translated_neutral.get("tl"), "delusion": translated_delusion.get("tl")},
                "id": {"neutral": translated_neutral.get("id"), "delusion": translated_delusion.get("id")},
                "sw": {"neutral": translated_neutral.get("sw"), "delusion": translated_delusion.get("sw")}
            },
            "ground_truth": {
                "correct": item["correct_answer"],
                "delusional": item["delusional_answer"]
            }
        }
        multilingual_data.append(new_item)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(multilingual_data, f, indent=4, ensure_ascii=False)
        
    print(f"\n Success! Verified dataset saved to {output_path}")

if __name__ == "__main__":
    build_multilingual_dataset()