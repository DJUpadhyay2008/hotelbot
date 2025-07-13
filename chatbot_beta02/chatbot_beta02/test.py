import google.generativeai as genai

genai.configure(api_key="AIzaSyB4id64G_cstJ-X9-ZqqahcjIiLkjx72dg")
models = genai.list_models()

for m in models:
    print(m.name)
