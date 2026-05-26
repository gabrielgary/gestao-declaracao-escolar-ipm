import os
from dotenv import load_dotenv

load_dotenv()

# Script para listar modelos disponíveis
try:
    from google import genai
    
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("=== Modelos Gemini Disponíveis ===\n")
    models = client.models.list()
    
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    
    for model in gemini_models:
        print(f"Nome: {model.name}")
        if hasattr(model, 'display_name'):
            print(f"  Display Name: {model.display_name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Suporta: {model.supported_generation_methods}")
        print()
        
    print(f"\nTotal demodelos Gemini encontrados: {len(gemini_models)}")
    
except Exception as e:
    print(f"Erro ao listar modelos: {e}")
    import traceback
    traceback.print_exc()
