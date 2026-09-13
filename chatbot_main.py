# --- chatbot_main.py ---

# Importations nécessaires depuis les autres modules
from vectorizer_svm import is_makeup_query # Importé mais non utilisé (filtre supprimé)
from llm_handler import ask_llm as generate_answer, detect_language, translate_text 
from document_loader import load_documents

# Charger tout le contenu des documents une seule fois au démarrage
# Ceci sert de contexte RAG pour toutes les requêtes.
ALL_DOCUMENTS_TEXT = load_documents()

def chatbot(query: str) -> str:
    """
    Fonction principale du chatbot gérant le flux de la requête utilisateur :
    Détection -> Traduction de la requête -> Appel LLM (en Anglais) -> Traduction de la réponse.
    """
    
    # 0. DÉTECTION DE LA LANGUE D'ORIGINE
    original_lang = detect_language(query)
    
    # 1. TRADUCTION DE LA REQUÊTE EN ANGLAIS (Langue de travail pour le LLM)
    # Le LLM (Claude Haiku) est instruit pour répondre en Anglais, donc sa requête doit l'être aussi.
    if original_lang != "en":
        query_for_llm = translate_text(query, "English")
    else:
        query_for_llm = query
    
    # 2. FILTRAGE SVM: Supprimé pour ce test final (comme indiqué dans l'original).
    # is_relevant = is_makeup_query(query_for_llm)
    # ...
    
    # 3. APPEL DU LLM (avec la requête en ANGLAIS)
    # La réponse retournée (llm_response_en) est garantie d'être en anglais par llm_handler.py.
    llm_response_en = generate_answer(query_for_llm, context=ALL_DOCUMENTS_TEXT)
    
    # 4. TRADUCTION DE LA RÉPONSE FINALE DANS LA LANGUE D'ORIGINE
    if original_lang != "en":
        # Traduire la réponse en anglais vers la langue d'origine (via Mistral)
        final_response = translate_text(llm_response_en, original_lang)
    else:
        # CORRECTION : Si la langue d'origine est l'anglais, la réponse du LLM est la réponse finale.
        final_response = llm_response_en
        
    return final_response

# Exemple d'utilisation (non inclus dans le fichier, mais pour le test)
# if __name__ == "__main__":
#     print(chatbot("Quels sont les avantages du fond de teint ?"))
#     print(chatbot("What is the benefit of foundation?"))