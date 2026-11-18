"""
Train the text model used alongside the rule engine.
Usage: python train_model.py data/messages.csv
The CSV needs two columns: text, label  (1 = scam/phishing, 0 = legitimate)
Good public datasets: UCI "SMS Spam Collection", Kaggle "Phishing Email Dataset".
"""
import os
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

if len(sys.argv) < 2:
    sys.exit("Usage: python train_model.py <dataset.csv>")

df = pd.read_csv(sys.argv[1]).dropna(subset=["text", "label"])
df["text"] = df["text"].astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
)

model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), min_df=2, stop_words="english", max_features=20000),
    LogisticRegression(max_iter=1000, class_weight="balanced"),
)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test), digits=3))

os.makedirs("model", exist_ok=True)
joblib.dump(model, os.path.join("model", "text_model.joblib"))
print("Saved model/text_model.joblib")