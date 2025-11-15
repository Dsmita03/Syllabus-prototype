# """
# Train and export TF-IDF, SVM, and LabelEncoder models
# for the Automated Course Outcome Extraction System.
# """

# import joblib
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.preprocessing import LabelEncoder
# from sklearn.svm import SVC

# # ======================================================
# # 1️⃣ TRAINING DATA (You can expand this with your syllabus)
# # ======================================================
# data = [
#     ("Define software engineering principles", "Remembering"),
#     ("List different types of software process models", "Remembering"),
#     ("Explain the need for version control", "Understanding"),
#     ("Summarize the stages of the SDLC", "Understanding"),
#     ("Use Git to manage source code", "Applying"),
#     ("Apply testing methods on real projects", "Applying"),
#     ("Analyze project risks in development", "Analyzing"),
#     ("Differentiate between verification and validation", "Analyzing"),
#     ("Evaluate software quality metrics", "Evaluating"),
#     ("Critique a project's scheduling plan", "Evaluating"),
#     ("Design a REST API using Flask", "Creating"),
#     ("Develop a project plan for development", "Creating"),
# ]

# df = pd.DataFrame(data, columns=["text", "bloom_level"])

# # ======================================================
# # 2️⃣ ENCODE LABELS
# # ======================================================
# label_encoder = LabelEncoder()
# y = label_encoder.fit_transform(df["bloom_level"])

# # ======================================================
# # 3️⃣ VECTORIZE TEXT (TF-IDF)
# # ======================================================
# vectorizer = TfidfVectorizer(stop_words="english")
# X = vectorizer.fit_transform(df["text"])

# # ======================================================
# # 4️⃣ TRAIN MODEL ON FULL DATA
# # ======================================================
# # We train on full data to avoid small dataset split errors
# model = SVC(kernel="linear", probability=True)
# model.fit(X, y)

# # ======================================================
# # 5️⃣ SAVE TRAINED COMPONENTS
# # ======================================================
# joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
# joblib.dump(model, "svm_model.joblib")
# joblib.dump(label_encoder, "label_encoder_level.joblib")

# # ======================================================
# # 6️⃣ VERIFY
# # ======================================================
# print("\n✅ Models trained and saved successfully!")
# print("   - tfidf_vectorizer.joblib")
# print("   - svm_model.joblib")
# print("   - label_encoder_level.joblib")
# print(f"\nClasses encoded: {list(label_encoder.classes_)}")

"""
Train and export TF-IDF, SVM, and LabelEncoder models
for the Automated Course Outcome Extraction System.

This version improves:
✅ Reproducibility
✅ Model validation
✅ File structure consistency with analyser.py
✅ Extensibility for larger datasets
"""

# import os
# import joblib
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.preprocessing import LabelEncoder
# from sklearn.svm import SVC
# from sklearn.pipeline import Pipeline
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report, accuracy_score

# # ======================================================
# # 1️⃣ TRAINING DATA — Expandable & Clear
# # ======================================================

# data = [
#     # --- Remembering ---
#     ("Define software engineering principles", "Remembering"),
#     ("List different types of software process models", "Remembering"),
#     ("State the purpose of documentation", "Remembering"),

#     # --- Understanding ---
#     ("Explain the need for version control", "Understanding"),
#     ("Summarize the stages of the SDLC", "Understanding"),
#     ("Describe the function of project management tools", "Understanding"),

#     # --- Applying ---
#     ("Use Git to manage source code", "Applying"),
#     ("Apply testing methods on real projects", "Applying"),
#     ("Implement version control using GitHub", "Applying"),

#     # --- Analyzing ---
#     ("Analyze project risks in development", "Analyzing"),
#     ("Differentiate between verification and validation", "Analyzing"),
#     ("Break down the phases of agile methodology", "Analyzing"),

#     # --- Evaluating ---
#     ("Evaluate software quality metrics", "Evaluating"),
#     ("Critique a project's scheduling plan", "Evaluating"),
#     ("Assess the effectiveness of software testing", "Evaluating"),

#     # --- Creating ---
#     ("Design a REST API using Flask", "Creating"),
#     ("Develop a project plan for development", "Creating"),
#     ("Construct a UML diagram for a system", "Creating"),
# ]

# df = pd.DataFrame(data, columns=["text", "bloom_level"])

# # ======================================================
# # 2️⃣ ENCODE LABELS
# # ======================================================
# label_encoder = LabelEncoder()
# y = label_encoder.fit_transform(df["bloom_level"])

# # ======================================================
# # 3️⃣ TF-IDF + SVM PIPELINE
# # ======================================================
# vectorizer = TfidfVectorizer(
#     stop_words="english",
#     ngram_range=(1, 2),
#     max_features=1000
# )

# model = SVC(kernel="linear", probability=True, random_state=42)

# # Build pipeline for convenience
# pipeline = Pipeline([
#     ("tfidf", vectorizer),
#     ("svm", model)
# ])

# # ======================================================
# # 4️⃣ TRAIN/TEST SPLIT (for verification)
# # ======================================================
# # X_train, X_test, y_train, y_test = train_test_split(
# #     df["text"], y, test_size=0.2, random_state=42, stratify=y
# # )

# # pipeline.fit(X_train, y_train)

# # ⚙️ Train on full data (small dataset → no test split)
# pipeline.fit(df["text"], y)
# print("\n Model trained on full dataset (mock baseline).")


# # ======================================================
# # 5️⃣ VALIDATION REPORT
# # ======================================================
# # y_pred = pipeline.predict(X_test)
# # print("\n📊 Model Evaluation Results:")
# # print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
# # print(f"✅ Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# y_pred = pipeline.predict(df["text"])
# print("\n✅ Model trained successfully on all data.")


# # ======================================================
# # 6️⃣ EXPORT TRAINED COMPONENTS
# # ======================================================
# os.makedirs("models", exist_ok=True)

# # Extract components for analyser.py compatibility
# tfidf_vectorizer = pipeline.named_steps["tfidf"]
# svm_model = pipeline.named_steps["svm"]

# joblib.dump(tfidf_vectorizer, "models/tfidf_vectorizer.pkl")
# joblib.dump(svm_model, "models/bloom_svm_model.pkl")
# joblib.dump(label_encoder, "models/label_encoder.pkl")

# print("\n✅ Models trained and exported successfully!")
# print("   → models/tfidf_vectorizer.pkl")
# print("   → models/bloom_svm_model.pkl")
# print("   → models/label_encoder.pkl")

# print(f"\n🧠 Encoded Bloom Levels: {list(label_encoder.classes_)}")

"""
TRAIN BLOOM-LEVEL CLASSIFIER (Final Version)
--------------------------------------------
This script trains:
✔ TF-IDF Vectorizer
✔ SVM Classifier
✔ Label Encoder

Outputs saved:
models/
    bloom_svm_model.pkl
    tfidf_vectorizer.pkl
    label_encoder.pkl

Uses improved dataset (80 training samples).
"""

import os
import joblib
import pandas as pd
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split


# ======================================================
# 1️⃣ LOAD YOUR 80-LINE BLOOM DATASET
# ======================================================

data = [

    # REMEMBERING (15)
    ("Define the concept of software engineering", "Remembering"),
    ("List different types of software development models", "Remembering"),
    ("State the purpose of requirement analysis", "Remembering"),
    ("Recall the phases of software testing", "Remembering"),
    ("Identify components of a software project", "Remembering"),
    ("Memorize common database terminology", "Remembering"),
    ("Define operating system functions", "Remembering"),
    ("List different types of computer networks", "Remembering"),
    ("Recall fundamental data structures", "Remembering"),
    ("Identify types of UML diagrams", "Remembering"),
    ("State file handling operations in Java", "Remembering"),
    ("List different scheduling algorithms", "Remembering"),
    ("Define the role of a compiler", "Remembering"),
    ("Recall HTTP request methods", "Remembering"),
    ("Identify various cloud service models", "Remembering"),

    # UNDERSTANDING (15)
    ("Explain the need for version control in software development", "Understanding"),
    ("Describe the working of the waterfall model", "Understanding"),
    ("Summarize the features of object-oriented programming", "Understanding"),
    ("Interpret ER diagrams in database design", "Understanding"),
    ("Explain the concept of software configuration management", "Understanding"),
    ("Discuss the purpose of use-case diagrams", "Understanding"),
    ("Describe client-server architecture", "Understanding"),
    ("Explain the principles of data normalization", "Understanding"),
    ("Summarize basic network communication models", "Understanding"),
    ("Explain the concept of exception handling", "Understanding"),
    ("Illustrate the working of Gantt charts", "Understanding"),
    ("Describe the role of the JVM in Java execution", "Understanding"),
    ("Explain the lifecycle of a servlet", "Understanding"),
    ("Interpret the meaning of RESTful APIs", "Understanding"),
    ("Explain the purpose of indexing in databases", "Understanding"),

    # APPLYING (15)
    ("Apply Git commands to manage software repositories", "Applying"),
    ("Use SQL queries to manipulate database tables", "Applying"),
    ("Implement stack and queue using arrays", "Applying"),
    ("Use exception handling to build robust applications", "Applying"),
    ("Apply testing techniques to identify software defects", "Applying"),
    ("Develop a simple login system using PHP", "Applying"),
    ("Implement CRUD operations using JDBC", "Applying"),
    ("Apply loops and functions to solve problems in Python", "Applying"),
    ("Test a web application using Selenium", "Applying"),
    ("Use PERT and CPM to estimate project timelines", "Applying"),
    ("Design a basic web form using HTML and CSS", "Applying"),
    ("Deploy a small application on a cloud platform", "Applying"),
    ("Implement routing using Express.js", "Applying"),
    ("Use multithreading to improve program efficiency", "Applying"),
    ("Apply sorting algorithms to organize data", "Applying"),

    # ANALYZING (12)
    ("Analyze project risks using qualitative techniques", "Analyzing"),
    ("Differentiate between verification and validation", "Analyzing"),
    ("Break down a large system into modules", "Analyzing"),
    ("Examine performance bottlenecks in an application", "Analyzing"),
    ("Compare various software testing strategies", "Analyzing"),
    ("Inspect the causes of deadlock in operating systems", "Analyzing"),
    ("Analyze differences between TCP and UDP protocols", "Analyzing"),
    ("Break down user requirements into functional components", "Analyzing"),
    ("Compare static and dynamic websites", "Analyzing"),
    ("Distinguish between compiler and interpreter behavior", "Analyzing"),
    ("Examine data flow in client-server communication", "Analyzing"),
    ("Evaluate alternative database indexing techniques", "Analyzing"),

    # EVALUATING (12)
    ("Evaluate the effectiveness of different testing tools", "Evaluating"),
    ("Judge the quality of a software design using metrics", "Evaluating"),
    ("Critique the architecture of an existing system", "Evaluating"),
    ("Assess the reliability of network security protocols", "Evaluating"),
    ("Evaluate different cloud deployment models", "Evaluating"),
    ("Recommend improvements for a software development process", "Evaluating"),
    ("Validate the correctness of algorithms", "Evaluating"),
    ("Critically review a project management plan", "Evaluating"),
    ("Judge the performance of a DBMS indexing strategy", "Evaluating"),
    ("Evaluate user experience in a mobile application", "Evaluating"),
    ("Assess the maintainability of a large software system", "Evaluating"),
    ("Rate different UI design methodologies", "Evaluating"),

    # CREATING (11)
    ("Design a REST API using Flask", "Creating"),
    ("Develop an e-commerce checkout module", "Creating"),
    ("Construct a UML diagram for a library system", "Creating"),
    ("Design a normalized database schema", "Creating"),
    ("Develop a responsive front-end using React", "Creating"),
    ("Create a software prototype for client evaluation", "Creating"),
    ("Build a microservice architecture for a small system", "Creating"),
    ("Compose a project plan with timelines and milestones", "Creating"),
    ("Generate alternative solutions to a design problem", "Creating"),
    ("Develop a unit testing framework for an application", "Creating"),
    ("Create a machine learning model for prediction", "Creating"),
]

df = pd.DataFrame(data, columns=["text", "bloom_level"])


# ======================================================
# 2️⃣ LABEL ENCODING
# ======================================================
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["bloom_level"])


# ======================================================
# 3️⃣ TF-IDF VECTORIZER
# ======================================================
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),        # 🔥 bigrams improve accuracy
    max_features=2000
)


# ======================================================
# 4️⃣ TRAIN/TEST SPLIT
# ======================================================
X_train, X_test, y_train, y_test = train_test_split(
    df["text"],
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Fit TF-IDF
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)


# ======================================================
# 5️⃣ TRAIN SVM CLASSIFIER
# ======================================================
model = SVC(
    kernel="linear",
    probability=True,
    random_state=42
)
model.fit(X_train_vec, y_train)


# ======================================================
# 6️⃣ VALIDATION RESULTS
# ======================================================
y_pred = model.predict(X_test_vec)

print("\n📊 BLOOM CLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
print(f"🔥 Accuracy: {accuracy_score(y_test, y_pred):.4f}")


# ======================================================
# 7️⃣ SAVE ARTIFACTS
# ======================================================
os.makedirs("models", exist_ok=True)

joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
joblib.dump(model, "models/bloom_svm_model.pkl")
joblib.dump(label_encoder, "models/label_encoder.pkl")

print("\n✅ Training Complete!")
print("Saved:")
print(" → models/tfidf_vectorizer.pkl")
print(" → models/bloom_svm_model.pkl")
print(" → models/label_encoder.pkl")
