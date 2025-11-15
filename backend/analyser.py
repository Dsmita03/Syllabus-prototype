"""
ANALYSER.PY  (Keras Version, no SVM)
---------------------------------------
Generates Course Outcomes dynamically, module-by-module.

Features:
✓ Multi-word keyword extraction (NLP + TF-IDF + centrality)
✓ Per-module outcome generation (no mixing entire syllabus)
✓ Bloom-Level prediction using Keras model + LabelEncoder
✓ Clean JSON output for backend API

Expected Keras assets (already created by train_bloom_keras_tflite.py):
- models/bloom_keras_model.keras
- models/tokenizer.pkl
- models/label_encoder.pkl
"""

import os
import pickle
import numpy as np
import spacy
import networkx as nx
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer

from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

 
# Load NLP + Keras Model
nlp = spacy.load("en_core_web_sm")

MODELS_LOADED = False
MAX_LEN = 10   

MODEL = None
TOKENIZER = None
LABEL_ENCODER = None

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, "models")

    keras_model_path = os.path.join(MODELS_DIR, "bloom_keras_model.keras")
    MODEL = keras.models.load_model(keras_model_path)

    with open(os.path.join(MODELS_DIR, "tokenizer.pkl"), "rb") as f:
        TOKENIZER = pickle.load(f)

    with open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "rb") as f:
        LABEL_ENCODER = pickle.load(f)

    MODELS_LOADED = True
    print("✅ Keras Bloom model loaded successfully.")
except Exception as e:
    print("⚠️ Bloom Keras model NOT loaded:", e)
    MODELS_LOADED = False

# PHRASE EXTRACTION
 
def extract_phrases(text: str):
    """Extract multi-word noun phrases & entity phrases."""
    if not text:
        return []

    doc = nlp(text)
    phrases = set()

    # Noun chunks
    for chunk in doc.noun_chunks:
        phr = chunk.text.strip().lower()
        if len(phr.split()) >= 2:
            phrases.add(phr)

    # Entities
    for ent in doc.ents:
        phr = ent.text.strip().lower()
        if len(phr.split()) >= 2:
            phrases.add(phr)

    # Comma fallback (for comma-separated lists)
    for part in text.split(","):
        part = part.strip().lower()
        if len(part.split()) >= 2:
            phrases.add(part)

    # Cleanup
    cleaned = []
    for p in phrases:
        p = p.replace("-", " ").replace("  ", " ").strip()
        if p:
            cleaned.append(p)

    return list(set(cleaned))

# TF-IDF Scoring
 
def ranked_by_tfidf(phrases, full_text):
    if not phrases or not full_text:
        return {}

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform([full_text])
    scores = X.toarray().flatten()
    terms = vectorizer.get_feature_names_out()

    phrase_score = {}
    for ph in phrases:
        total = 0.0
        count = 0
        for term, score in zip(terms, scores):
            if term in ph:
                total += score
                count += 1
        phrase_score[ph] = total / (count + 1e-6)
    return phrase_score


 
# Graph Centrality Scoring
 
def ranked_by_centrality(phrases):
    if not phrases:
        return {}

    G = nx.Graph()
    G.add_nodes_from(phrases)

    # Connect phrases sharing at least 1 common word
    for p1, p2 in combinations(phrases, 2):
        if len(set(p1.split()) & set(p2.split())) > 0:
            G.add_edge(p1, p2)

    return nx.degree_centrality(G)

# Combined Keyword Ranking
 
def extract_keywords(text, top_n=6):
    """
    Use TF-IDF + centrality to select the top N multi-word phrases per module.
    """
    phrases = extract_phrases(text)
    if not phrases:
        return []

    tfidf_scores = ranked_by_tfidf(phrases, text)
    central_scores = ranked_by_centrality(phrases)

    final_scores = {}
    for p in phrases:
        final_scores[p] = (
            tfidf_scores.get(p, 0.0) * 0.6 +
            central_scores.get(p, 0.0) * 0.4
        )

    ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return [p for p, _ in ranked[:top_n]]

# Bloom Level Prediction (Keras)
 
def _predict_bloom_levels_keras(keywords):
    """
    Internal helper – run Keras model on a list of keywords → logits.
    """
    if not keywords or not MODELS_LOADED:
        return None

    seqs = TOKENIZER.texts_to_sequences(keywords)
    padded = pad_sequences(seqs, maxlen=MAX_LEN, padding="post")
    preds = MODEL.predict(padded, verbose=0)  # (N, num_classes)
    return preds


def map_keywords_to_bloom(keywords):
    """
    Map keywords to Bloom levels using Keras model.
    """
    if not keywords:
        return {}

    if not MODELS_LOADED:
        # graceful fallback
        return {k: "Unknown" for k in keywords}

    preds = _predict_bloom_levels_keras(keywords)
    if preds is None:
        return {k: "Unknown" for k in keywords}

    bloom_map = {}
    for i, kw in enumerate(keywords):
        class_index = int(np.argmax(preds[i]))
        label = LABEL_ENCODER.inverse_transform([class_index])[0]
        bloom_map[kw] = str(label)

    return bloom_map

# Generate Course Outcome Statements
 
def generate_outcome_statements(keyword_bloom_map):
    """
    Convert keyword → Bloom level into textual course outcomes.
    """
    templates = {
        "Remembering": "Recall and describe the concept of {}.",
        "Understanding": "Explain the principles of {}.",
        "Applying": "Apply the knowledge of {} to real-world problems.",
        "Analyzing": "Analyze the structure and components of {}.",
        "Evaluating": "Evaluate the effectiveness of {} using criteria.",
        "Creating": "Design or develop innovative solutions using {}."
    }

    outcomes = []
    for kw, bloom in keyword_bloom_map.items():
        template = templates.get(bloom, "Explain the concept of {}.")
        sentence = template.format(kw)
        outcomes.append({
            "keyword": kw,
            "bloom_level": bloom,
            "outcome": sentence
        })

    return outcomes
 
# Main Function (MODULE-BY-MODULE)
 
def generate_outcomes_per_module(modules):
    """
    Generate course outcomes for each module separately.

    Expected module format (from processor.SyllabusProcessor):
    {
      "id": "module_1",
      "module_id": 1,
      "title": "...",
      "content": "..."
    }

    Returns:
    [
      {
        "module_id": 1,
        "title": "...",
        "keywords": [...],
        "outcomes": [
          { "keyword": "...", "bloom_level": "...", "outcome": "..." },
          ...
        ]
      },
      ...
    ]
    """

    final_output = []

    for mod in modules:
        text = (
            mod.get("content")
            or mod.get("module_content")
            or ""
        )

        # 1) extract per-module keywords
        keywords = extract_keywords(text, top_n=6)

        # 2) map to Bloom levels
        bloom_map = map_keywords_to_bloom(keywords)

        # 3) generate COs
        outcomes = generate_outcome_statements(bloom_map)

        final_output.append({
            "module_id": mod.get("module_id"),
            "title": mod.get("title", f"Module {mod.get('module_id')}"),
            "keywords": keywords,
            "outcomes": outcomes
        })

    return final_output

#Optional Terminal Print Helpers
 
def print_module_outcomes(result):
    """Pretty print the module-by-module output."""
    print("\n==================== GENERATED COURSE OUTCOMES ====================\n")

    for mod in result:
        print(f"📘 Module {mod['module_id']}: {mod['title']}")
        print("Keywords:", ", ".join(mod["keywords"]))
        print("Outcomes:")
        for oc in mod["outcomes"]:
            print(f"  - [{oc['bloom_level']}] {oc['outcome']}")
        print("\n-------------------------------------------------------------------")


def print_generated_outcomes(result):
    print("\n=========== GENERATED OUTCOMES ===========\n")
    for module in result:
        print(f"Module {module['module_id']} - {module['title']}")
        print("Keywords:", ", ".join(module["keywords"]))
        print("Outcomes:")
        for oc in module["outcomes"]:
            print(f" - [{oc['bloom_level']}] {oc['outcome']}")
        print("\n------------------------------------------")
