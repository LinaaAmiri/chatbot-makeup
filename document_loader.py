
import os

docs_folder = "documents"

def load_documents():
    all_text = ""
    for category in os.listdir(docs_folder):
        cat_path = os.path.join(docs_folder, category)
        if os.path.isdir(cat_path):
            for fname in os.listdir(cat_path):
                if fname.endswith(".txt"):
                    with open(os.path.join(cat_path, fname), "r", encoding="utf-8") as f:
                        all_text += f.read() + "\n"
    return all_text
