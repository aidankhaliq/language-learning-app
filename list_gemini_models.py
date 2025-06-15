import google.generativeai as genai

API_KEY = "AIzaSyDJ-mZsg3HwFml2yF6kjFu_Rq1AWJWxipI"
genai.configure(api_key=API_KEY)

models = genai.list_models()
print("Available Gemini models for your API key:")
for m in models:
    print(m) 