# --- app.py (CODE COMPLET FINAL avec Plein Écran) ---
import streamlit as st
import os
import base64 

# IMPORTANT : Assurez-vous que chatbot_main.py est dans le même dossier
try:
    from chatbot_main import chatbot
except ImportError:
    st.error("Erreur: Le fichier 'chatbot_main.py' est introuvable. Assurez-vous qu'il est dans le même dossier.")
    chatbot = lambda x: "Erreur de chargement du module."

# *************************************************************************
# Configuration de l'image de fond et du CSS
# *************************************************************************

# REMPLACER CECI : Entrez le chemin complet de votre image (ex: D:\o\mon_fond.jpg)
IMAGE_FILE = r"D:\oo.jpg" 

def get_base64_image(image_path):
    """Encode l'image locale en Base64 pour l'utiliser en CSS."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Erreur : Le fichier image '{image_path}' est introuvable. Vérifiez le chemin ou le nom du fichier.")
        return None
    except Exception as e:
        st.error(f"Erreur lors de l'encodage de l'image: {e}")
        return None

def set_background_image(base64_string):
    """Injecte le CSS pour définir l'image de fond et la couleur du texte."""
    if base64_string:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{base64_string}");
                background-size: cover;          
                background-repeat: no-repeat;    
                background-attachment: fixed;    
                background-position: center;     
                /* CORRECTION POUR PLEIN ÉCRAN */
                min-height: 100vh; 
                height: 100vh;
                width: 100vw;
            }}
            
            /* CIBLE LES BULLES DE CHAT ET LE TEXTE POUR LE METTRE EN NOIR */
            .stChatMessage {{
                color: black !important; 
            }}
            .stChatMessage div[data-testid="stMarkdownContainer"] p {{
                color: black !important; 
            }}
            div[data-testid="stChatInput"] input {{
                color: black !important;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: black !important;
            }}
            div[data-testid="stMarkdownContainer"] p:first-child {{
                 color: black !important;
            }}
            
            </style>
            """,
            unsafe_allow_html=True
        )

# *************************************************************************
# Démarrage de l'application
# *************************************************************************

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Expert Maquillage Multilingue (RAG)",
    layout="wide",
)

# Appel pour définir l'image de fond et le style
base64_img = get_base64_image(IMAGE_FILE)
set_background_image(base64_img)

# Affichage du titre
st.title("💄 Chatbot Expert Maquillage")
st.markdown("Posez votre question sur les produits cosmétiques, les astuces d'application, ou les tendances. Le chatbot répond en Français et en Anglais !")

# Vérification de la clé API
if not os.getenv("OPENROUTER_API_KEY"):
    st.warning("⚠️ ATTENTION : La variable d'environnement OPENROUTER_API_KEY n'est pas définie. Le chatbot ne fonctionnera pas.")

# Initialisation de l'historique de la conversation dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Gestion des nouvelles requêtes utilisateur
if prompt := st.chat_input("Posez votre question..."):
    # 1. Ajouter la requête de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Obtenir la réponse du chatbot
    with st.spinner("Le chatbot réfléchit..."):
        response = chatbot(prompt)
    
    # 3. Afficher la réponse du chatbot
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # 4. Ajouter la réponse à l'historique
    st.session_state.messages.append({"role": "assistant", "content": response})