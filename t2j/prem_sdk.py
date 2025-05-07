import os
import json
import time
import requests
from tqdm import tqdm
from typing import List
from dotenv import load_dotenv, find_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

from t2j.prompts import Prompts

load_dotenv(find_dotenv('.env'))


class PremSDK:
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        self.prompts = Prompts()
        
    def generate(self, input_text: str, temperature: float = 0.2):
        def send_request():
            time.sleep(2)
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": input_text}],
                "stream": False,
                "temperature": temperature,
                "max_tokens": 2048
            }
            headers = {
                "Authorization": os.getenv("PREM_APIKEY"),
                "Content-Type": "application/json"
            }
            api_url = os.getenv("PREM_URL")
            return requests.post(api_url, headers=headers, json=payload)

        for attempt in range(3):
            try:
                response = send_request()
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(3)
        raise Exception("OPENAI API failed ...")
        
    def generate_parallel(self, input_texts: List[str], temperature: float = 0.2, max_workers: int = 5):
        time.sleep(0.1)
        results = [None] * len(input_texts)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.generate, text, temperature): idx
                for idx, text in enumerate(input_texts)
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="Generating responses"):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    print(f"Error processing input {idx}: {e}")
                    results[idx] = None
                    
        return results
    
    def generate_sequential(self, input_texts: List[str], temperature: float = 0.2):
        time.sleep(0.1)
        results = []

        for text in tqdm(input_texts, desc="Generating responses"):
            try:
                output = self.generate(text, temperature)
            except Exception as e:
                print(f"Error processing input: {e}")
                output = None
            results.append(output)

        return results
    
    def extract_json(self, text: str):
        cleaned = text.replace('```json', "").replace("```", "").strip()
        failure_count = 3
        for i in range(failure_count):
            try:
                output = json.loads(cleaned)
                return output
            except:
                print("Fixing JSON ...")
                prompt = self.prompts.fix_json(cleaned)
                output = self.generate(prompt)
                cleaned = output.replace('```json', "").replace("```", "").strip()
                
        raise json.JSONDecodeError()