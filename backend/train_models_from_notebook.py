"""
Train and export TF-IDF, SVM, and LabelEncoder models
for the Automated Course Outcome Extraction System.
"""

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

# ======================================================
# 1️⃣ TRAINING DATA (You can expand this with your syllabus)
# ======================================================
data = [
    ("Define software engineering principles", "Remembering"),
    ("List different types of software process models", "Remembering"),
    ("Explain the need for version control", "Understanding"),
    ("Summarize the stages of the SDLC", "Understanding"),
    ("Use Git to manage source code", "Applying"),
    ("Apply testing methods on real projects", "Applying"),
    ("Analyze project risks in development", "Analyzing"),
    ("Differentiate between verification and validation", "Analyzing"),
    ("Evaluate software quality metrics", "Evaluating"),
    ("Critique a project's scheduling plan", "Evaluating"),
    ("Design a REST API using Flask", "Creating"),
    ("Develop a project plan for development", "Creating"),
]

df = pd.DataFrame(data, columns=["text", "bloom_level"])

# ======================================================
# 2️⃣ ENCODE LABELS
# ======================================================
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["bloom_level"])

# ======================================================
# 3️⃣ VECTORIZE TEXT (TF-IDF)
# ======================================================
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["text"])

# ======================================================
# 4️⃣ TRAIN MODEL ON FULL DATA
# ======================================================
# We train on full data to avoid small dataset split errors
model = SVC(kernel="linear", probability=True)
model.fit(X, y)

# ======================================================
# 5️⃣ SAVE TRAINED COMPONENTS
# ======================================================
joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
joblib.dump(model, "svm_model.joblib")
joblib.dump(label_encoder, "label_encoder_level.joblib")

# ======================================================
# 6️⃣ VERIFY
# ======================================================
print("\n✅ Models trained and saved successfully!")
print("   - tfidf_vectorizer.joblib")
print("   - svm_model.joblib")
print("   - label_encoder_level.joblib")
print(f"\nClasses encoded: {list(label_encoder.classes_)}")
