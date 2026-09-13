# --- llm_handler.py (CODE COMPLET FINAL avec correction sémantique) ---
import os
from openai import OpenAI

# ... (Initialisation inchangée)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("La variable d'environnement OPENROUTER_API_KEY n'est pas définie. Veuillez l'initialiser avec 'set OPENROUTER_API_KEY=...' dans votre console.")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

HAIKU_MODEL = "anthropic/claude-3-haiku" 

# CHANGEMENT ICI : Ajout d'une règle pour corriger la mauvaise traduction de "ḥamra" (rouge à lèvres/fard)
SYSTEM_PROMPT = """
You are a makeup expert assistant.
Answer questions clearly and concisely.
Use context if provided.
IMPORTANT: When translating Arabic questions, assume that 'ḥamra' (حمرة) refers to 'lipstick', 'blush', or 'cosmetic coloring', NOT 'fish' or 'animal'.
"""

# --- FONCTION PRINCIPALE DE GÉNÉRATION DE RÉPONSE (ask_llm) ---
def ask_llm(user_input: str, context: str = "") -> str:
    """Génère la réponse du chatbot en utilisant la requête (en anglais) et le contexte RAG (Claude 3 Haiku)."""
    try:
        prompt = f"CONTEXT: {context}\n\nQUESTION: {user_input}\n\nINSTRUCTION: Based on the context, answer the question. Your response MUST be ONLY in English." if context else f"QUESTION: {user_input}\n\nINSTRUCTION: Answer the question. Your response MUST be ONLY in English."
        
        response = client.chat.completions.create(
            model=HAIKU_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            timeout=30.0
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors du traitement de la requête: {str(e)}"

# --- FONCTION 1: DÉTECTION DE LANGUE (Claude 3 Haiku) ---
def detect_language(text: str) -> str:
    # ... (fonction detect_language inchangée)
    try:
        detection_prompt = (
            f"Identify the language code (ISO 639-1, e.g., 'fr', 'ar', 'en') of the following text: '{text}'. "
            "Output ONLY the language code, nothing else."
        )
        
        response = client.chat.completions.create(
            model=HAIKU_MODEL, 
            messages=[
                {"role": "user", "content": detection_prompt}
            ],
            timeout=10.0,
            max_tokens=5 
        )
        lang_code = response.choices[0].message.content.strip().lower()
        
        if len(lang_code) == 2 and lang_code.isalpha():
            if lang_code == "en" and any(c.isdigit() for c in text):
                 return "ar" 
            return lang_code
        return "en" 
        
    except Exception:
        return "en" 

# --- FONCTION 2: TRADUCTION DE TEXTE (Claude 3 Haiku) ---
def translate_text(text: str, target_lang: str) -> str:
    """Traduit le texte en utilisant Claude 3 Haiku."""
    
    lang_map = {
        "fr": "French",
        "ar": "Tunisian Arabic (Derja)", 
        "en": "English",
    }
    target_lang_name = lang_map.get(target_lang.lower(), target_lang)

    # Cas 1: Traduction vers l'Anglais (Etape 1: Traduction de la requête utilisateur)
    if target_lang_name.lower() in ["english", "en"]:
        if target_lang.lower() == "en":
            return text 
            
        if any(c.isdigit() for c in text):
            # Prompt spécial pour la Derja Latine/chiffrée
            translation_prompt = (
                f"Translate the following Arabic text, which is transcribed using Latin characters and numbers (Derja/chat-speak), into clear English. Output ONLY the translation. Text to translate: '{text}'"
            )
            system_prompt = "You are a specialized translator, adept at translating non-standard Arabic transcriptions. Output ONLY the translation."
        else:
            # Pour le Français ou l'Arabe standard vers l'Anglais
            translation_prompt = f"Translate the following text into English. Output ONLY the translation. Text to translate: '{text}'"
            system_prompt = "You are a specialized translation engine. Output ONLY the translation."

        try:
            response = client.chat.completions.create(
                model=HAIKU_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": translation_prompt}
                ],
                timeout=15.0,
                max_tokens=3000 
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Avertissement: Échec de l'API pour la traduction de la requête vers l'Anglais: {e}")
            return text
            
    # Cas 2: Traduction vers la Langue d'Origine (Etape 4: Traduction de la réponse finale)
    try:
        translation_prompt = (
            f"Translate the following text into {target_lang_name}. Text to translate: '{text}'"
        )
        
        response = client.chat.completions.create(
            model=HAIKU_MODEL,
            messages=[
                # SYSTEM PROMPT SPÉCIAL POUR LA DERJA : Force le dialecte et les caractères arabes
                {"role": "system", "content": f"You are a specialized translation engine. Your sole job is to translate the provided text. When translating to Tunisian Arabic (Derja), you **MUST** use the local dialect and vocabulary, and the entire response **MUST** be written in Arabic script. AVOID using Standard Arabic (Fusha)."}, 
                {"role": "user", "content": translation_prompt}
            ],
            timeout=15.0,
            max_tokens=3000 
        )
        
        translated_text = response.choices[0].message.content.strip()
        
        # Test de robustesse
        if len(translated_text) < (len(text) * 0.2):
             print(f"Avertissement: Traduction vers {target_lang} échouée (trop courte). Retourne le texte anglais.") 
             return text 
        
        if translated_text.startswith(text):
            translated_text = translated_text[len(text):].strip()

        return translated_text
        
    except Exception as e:
        print(f"Avertissement: Échec critique de l'API pour la traduction vers {target_lang}. Retourne le texte anglais: {e}")
        return text