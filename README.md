# Multilingual Sycophancy Benchmark 🌍🤖

**Evaluating AI Safety Alignment and Delusion Acceptance in Low-Resource Languages**

This repository contains the code, data, and findings for our submission to the **Apart Research Global South AI Safety Hackathon**. We built an automated, cross-linguistic evaluation pipeline to measure sycophancy—specifically *delusion acceptance*—across English and four Global South languages: Vietnamese, Tagalog, Bahasa Indonesia, and Swahili.

## 🚀 The Core Problem
Current safety fine-tuning for Large Language Models (LLMs) is predominantly English-centric. If an LLM corrects a user’s bad medical advice in English but agrees with that exact same dangerous advice in Swahili simply because it wants to be "agreeable" in a low-resource language, it poses a severe threat to public health and epistemic trust in the Global South. 

This project investigates whether safety guardrails deteriorate when subjected to factual and medical delusions translated out of English.

## 🔑 Key Findings
Evaluating the **Llama-3.1-8b-instant** model (via Groq API) across 150 domain-specific test cases (100 mathematics, 50 medical), we discovered a severe degradation in safety alignment:
* **Anglocentric Safety:** The model exhibited near-perfect resistance to delusional premises in English (0.7% overall capitulation).
* **The Swahili Spike:** Vulnerability spiked dramatically in lower-resource languages, reaching **36.0% overall capitulation in Swahili**.
* **Medical Consistency Failure:** During a 50-iteration "Consistency Stress-Test" of core medical delusions, English guardrails held up 100% of the time. In Swahili, the model agreed with the dangerous medical premise 34.0% of the time.
* **The Heuristic Blind Spot:** We identified a critical flaw in regex-based keyword parsing for Vietnamese, where the model bypassed safety filters using out-of-vocabulary agreements (e.g., *"đồng ý"*), highlighting the need for LLM-as-a-Judge architectures in multilingual evaluations.

### Capitulation Rates (150 Evaluations)
| Language | Overall Rate | Math Rate | Medical Rate | Raw Counts (Cap/Total) |
| :--- | :--- | :--- | :--- | :--- |
| English | 0.7% | 1.0% | 0.0% | 1/150 |
| Vietnamese* | 0.0% | 0.0% | 0.0% | 0/150 |
| Tagalog | 7.3% | 8.0% | 6.0% | 11/150 |
| Bahasa | 13.3% | 20.0% | 0.0% | 20/150 |
| **Swahili** | **36.0%** | **37.0%** | **34.0%** | **54/150** |

*\*Vietnamese data reflects a heuristic parser false-negative (documented in our project report).*

---

## 📁 Repository Structure

* `data/` : Contains the generated datasets, translated prompts, and the final evaluated JSON results (`multilingual_results_llama-3.1-8b-instant.json`). High-resolution output charts are also saved here.
* `scripts/` : Contains the automated Python pipeline:
  * `generate_dataset.py`: Procedurally generates the base English math/medical delusions.
  * `translate_prompts.py`: Translates the dataset into target languages using the LLM in JSON mode.
  * `evaluate_multilingual.py`: Queries the model with the translated prompts and records responses.
  * `plot_results.py`: Runs RegEx-validated parsing, prints markdown tables, and generates Seaborn visualization charts.
* `requirements.txt` : Python dependencies required to run the pipeline.

---

## 🛠️ How to Run the Pipeline

1. Clone the repository.
2. Install dependencies:
   pip install -r requirements.txt
3. Set up your environment variables:
   Create a .env file in the root directory and add your Groq API key
   
4. Execute the scripts (in order):\
   python scripts/generate_dataset.py\
   python scripts/translate_prompts.py\
   python scripts/evaluate_multilingual.py\
   python scripts/plot_results.py\
---
**📜 License & Usage**\
Built for the Apart Research Hackathon. Open for review, replication, and extension. See our full submission report for deeper methodology discussions and limitation analysis.
