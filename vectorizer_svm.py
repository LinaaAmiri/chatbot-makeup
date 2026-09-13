
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import OneClassSVM

with open("corpus.txt", "r", encoding="utf-8") as f:
    makeup_queries = [line.strip() for line in f if line.strip()]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(makeup_queries)

svm = OneClassSVM(kernel='linear', nu=0.05)
svm.fit(X)

def is_makeup_query(query):
    query_vec = vectorizer.transform([query])
    return svm.predict(query_vec)[0] == 1
