import google.generativeai as genai
import os

# Load the API key from environment variables
api_key = "AIzaSyCg-JRLIVp7tyfMH5dQNNjEViDWCDQG9eE"
if not api_key:
    raise ValueError("API_KEY environment variable is not set.")

genai.configure(api_key=api_key)

def list_accessible_models():
    try:
        models = genai.list_models()
        print("Accessible Models:")
        for model in models:
            print(f"Model ID: {model.name}\nDescription: {model.description}\nInput Token Limit: {model.input_token_limit}\nOutput Token Limit: {model.output_token_limit}\n{'-'*30}")
    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    list_accessible_models()
