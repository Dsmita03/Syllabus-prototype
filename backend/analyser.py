"""
ANALYSER.PY  (Keras / TFLite Version, no SVM)
--------------------------------------------
Generates Course Outcomes dynamically, module-by-module.

Algorithms used (aligned with Automated Course Outcome file):
2) Implementation of Keyword using Partially Connected Graph
3) Centrality Measures
4) Bloom Model (here: Keras / TFLite Bloom classifier, not Bloombart/SVM/DT/RF)
6) Ranked ILOs/COs based on Term Frequency Importance

Features:
✓ Multi-word keyword extraction (spaCy + TF-IDF + centrality)
✓ Partially connected knowledge graph over phrases
✓ Per-module outcome generation (no mixing entire syllabus)
✓ Bloom-Level prediction using Keras / TFLite model + LabelEncoder
✓ Outcomes ranked by term-frequency importance
✓ Aggregated TOTAL course outcomes across all modules
✓ Clean JSON output for backend API

Expected assets (created by train_bloom_keras_tflite.py):
- models/bloom_keras_model.keras          (standard Keras model)
- models/bloom_keras_model.tflite        (optional – TFLite Lite model)
- models/tokenizer.pkl
- models/label_encoder.pkl
"""

import os
import re
import pickle
import numpy as np
import spacy
import networkx as nx
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

 
# Load NLP + Keras / TFLite Bloom Model
 
nlp = spacy.load("en_core_web_sm")

MODELS_LOADED = False
USE_TFLITE = False 
MAX_LEN = 10   

MODEL = None
TFLITE_INTERPRETER = None
TFLITE_INPUT_INDEX = None
TFLITE_OUTPUT_INDEX = None

TOKENIZER = None
LABEL_ENCODER = None

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, "models")

    # ---- Load tokenizer & label encoder (common for both Keras and TFLite) ----
    with open(os.path.join(MODELS_DIR, "tokenizer.pkl"), "rb") as f:
        TOKENIZER = pickle.load(f)

    with open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "rb") as f:
        LABEL_ENCODER = pickle.load(f)

    # ---- Prefer TFLite model if available (Keras Lite) ----
    tflite_model_path = os.path.join(MODELS_DIR, "bloom_keras_model.tflite")
    keras_model_path = os.path.join(MODELS_DIR, "bloom_keras_model.keras")

    if os.path.exists(tflite_model_path):
        # Use TFLite interpreter (CPU friendly, "lite" deployment)
        TFLITE_INTERPRETER = tf.lite.Interpreter(model_path=tflite_model_path)
        TFLITE_INTERPRETER.allocate_tensors()
        input_details = TFLITE_INTERPRETER.get_input_details()
        output_details = TFLITE_INTERPRETER.get_output_details()
        # assume single input/output
        TFLITE_INPUT_INDEX = input_details[0]["index"]
        TFLITE_OUTPUT_INDEX = output_details[0]["index"]
        USE_TFLITE = True
        print("TFLite Bloom model loaded successfully.")
    else:
        # Fall back to full Keras model (still runs on CPU if no GPU)
        MODEL = keras.models.load_model(keras_model_path)
        USE_TFLITE = False
        print("Keras Bloom model loaded successfully (no TFLite).")

    MODELS_LOADED = True

except Exception as e:
    print("Bloom model NOT loaded:", e)
    MODELS_LOADED = False

 
# 2. PHRASE / KEYWORD EXTRACTION + PARTIALLY CONNECTED GRAPH


def extract_phrases(text: str):
    """
    Extract multi-word noun phrases & entity phrases, plus comma-separated
    fragments. This acts as the 'concept set' for the knowledge graph.
    """
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

    # Comma-separated fallback
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


def create_partially_connected_knowledge_graph(concepts):
    """
    Create a fully connected graph and then convert to a partially connected
    graph by pruning some edges via neighbor-of-neighbor logic, similar to
    the Automated Course implementation.
    """
    G = nx.Graph()
    G.add_nodes_from(concepts)

    # Fully connect all concepts
    for node1, node2 in combinations(concepts, 2):
        G.add_edge(node1, node2)

    # Prune edges to get a partially connected graph
    for node in list(G.nodes()):
        for neighbor in list(G.neighbors(node)):
            for neighbor_of_neighbor in list(G.neighbors(neighbor)):
                if neighbor_of_neighbor != node and G.has_edge(node, neighbor_of_neighbor):
                    G.remove_edge(node, neighbor_of_neighbor)

    return G

 
# 3. CENTRALITY + TF-IDF SCORING FOR KEYWORD RANKING
 

def ranked_by_tfidf(phrases, full_text):
    """
    Compute a TF-IDF based score for each multi-word phrase, matching the
    term-importance idea from the Automated Course notebook.
    """
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


def ranked_by_centrality(phrases):
    """
    Compute centrality scores on the partially connected knowledge graph.
    We try eigenvector centrality first; if that fails, fallback to degree.
    """
    if not phrases:
        return {}

    G = create_partially_connected_knowledge_graph(phrases)

    try:
        centrality = nx.eigenvector_centrality_numpy(G)
    except Exception:
        centrality = nx.degree_centrality(G)

    return centrality


def extract_keywords(text, top_n=6):
    """
    Use TF-IDF + centrality to select the top N multi-word phrases per module.
    This implements:
      2) partially connected graph
      3) centrality measures
    combined with TF-IDF weighting.
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


 
# Bloom Level Prediction (Keras / TFLite)
 

def _predict_bloom_levels_keras(keywords):
    """
    Internal helper – run Keras or TFLite model on a list of keywords → logits.
    """
    if not keywords or not MODELS_LOADED:
        return None

    # Text → sequence indices
    seqs = TOKENIZER.texts_to_sequences(keywords)
    padded = pad_sequences(seqs, maxlen=MAX_LEN, padding="post")

    if USE_TFLITE and TFLITE_INTERPRETER is not None:
        # TFLite: run inference on CPU, "lite" model
        TFLITE_INTERPRETER.set_tensor(TFLITE_INPUT_INDEX, padded.astype(np.int32))
        TFLITE_INTERPRETER.invoke()
        preds = TFLITE_INTERPRETER.get_tensor(TFLITE_OUTPUT_INDEX)
    else:
        # Standard Keras model (also runs on CPU)
        preds = MODEL.predict(padded, verbose=0)

    return preds


def map_keywords_to_bloom(keywords):
    """
    Map keywords to Bloom levels using Keras / TFLite model.
    Replaces the Bloombart + SVM/DT/RF combination from the notebook.
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
 
# Generate Course Outcome Statements  (Automated Course style templates)
 

def generate_outcome_statements(keyword_bloom_map):
    """
    Generate course outcomes using Bloom-level-specific templates,
    following the style of the 'Automated Course Outcome' system.
    """
    bloom_templates = {
        "Remembering": (
            "Upon completion of this course, students will be able to:\n"
            "- Recall fundamental concepts related to {keyword}.\n"
            "- List key features and basic terminology of {keyword}."
        ),
        "Understanding": (
            "Upon completion of this course, students will be able to:\n"
            "- Explain the underlying principles of {keyword}.\n"
            "- Describe the role and significance of {keyword} in the given context."
        ),
        "Applying": (
            "Upon completion of this course, students will be able to:\n"
            "- Apply the concepts of {keyword} to solve practical problems.\n"
            "- Use appropriate techniques and tools involving {keyword} in real-world scenarios."
        ),
        "Analyzing": (
            "Upon completion of this course, students will be able to:\n"
            "- Analyze various elements of {keyword} and their interrelationships.\n"
            "- Break down complex situations involving {keyword} into manageable components."
        ),
        "Evaluating": (
            "Upon completion of this course, students will be able to:\n"
            "- Evaluate different approaches to {keyword} and justify optimal choices.\n"
            "- Critically review existing solutions or strategies involving {keyword}."
        ),
        "Creating": (
            "Upon completion of this course, students will be able to:\n"
            "- Design innovative solutions or systems involving {keyword}.\n"
            "- Develop new methods or frameworks that leverage {keyword} for improved performance."
        )
    }

    default_template = (
        "Upon completion of this course, students will be able to:\n"
        "- Explain the concept of {keyword} and outline its applications."
    )

    outcomes = []
    for kw, bloom in keyword_bloom_map.items():
        template = bloom_templates.get(bloom, default_template)
        sentence = template.format(keyword=kw)
        outcomes.append({
            "keyword": kw,
            "bloom_level": bloom,
            "outcome": sentence
        })

    return outcomes

# 6. Ranked ILOs/COs based on Term Frequency Importance
 

def rank_outcomes_by_term_frequency(outcomes):
    """
    Rank generated outcomes (COs) based on term-frequency importance.
    This mirrors 'Ranked ILOs based on Term Frequency Importance: CO'.
    """
    if not outcomes:
        return outcomes

    texts = [o["outcome"] for o in outcomes]

    vectorizer = CountVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)
    term_freq = np.asarray(X.sum(axis=0)).ravel()
    vocab = vectorizer.get_feature_names_out()
    term_frequency_dict = dict(zip(vocab, term_freq))

    def importance(text):
        tokens = re.findall(r"\b\w+\b", text.lower())
        return float(sum(term_frequency_dict.get(t, 0) for t in tokens))

    for o in outcomes:
        o["importance_score"] = importance(o["outcome"])

    outcomes_sorted = sorted(outcomes, key=lambda o: o["importance_score"], reverse=True)
    return outcomes_sorted

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
          {
            "keyword": "...",
            "bloom_level": "...",
            "outcome": "...",
            "importance_score": float
          },
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

        # 1) extract per-module keywords (graph + centrality + TF-IDF)
        keywords = extract_keywords(text, top_n=6)

        # 2) map to Bloom levels (Keras / TFLite)
        bloom_map = map_keywords_to_bloom(keywords)

        # 3) generate COs
        outcomes = generate_outcome_statements(bloom_map)

        # 4) rank COs by term-frequency importance
        outcomes = rank_outcomes_by_term_frequency(outcomes)

        final_output.append({
            "module_id": mod.get("module_id"),
            "title": mod.get("title", f"Module {mod.get('module_id')}"),
            "keywords": keywords,
            "outcomes": outcomes
        })
       
    return final_output

# TOTAL COURSE OUTCOMES (aggregated across modules)
 

def aggregate_course_outcomes(modules_result, top_n=None):
    """
    Aggregate & rank TOTAL course outcomes across *all* modules,
    using the same term-frequency importance idea as the Automated Course system.

    modules_result: output of generate_outcomes_per_module(modules)

    Returns:
    [
      {
        "keyword": "...",
        "bloom_level": "...",
        "outcome": "...",
        "importance_score": float,
        "modules": [module_id, ...]
      },
      ...
    ]
    """
    all_outcomes = []
    for mod in modules_result:
        mid = mod.get("module_id")
        for oc in mod.get("outcomes", []):
            entry = oc.copy()
            entry["modules"] = [mid]
            all_outcomes.append(entry)

    if not all_outcomes:
        return []

    # Merge duplicates by outcome text
    merged = {}
    for oc in all_outcomes:
        key = oc["outcome"]
        if key not in merged:
            merged[key] = oc
        else:
            # keep max importance_score and merge module list
            merged[key]["importance_score"] = max(
                merged[key].get("importance_score", 0.0),
                oc.get("importance_score", 0.0)
            )
            merged[key]["modules"] = sorted(
                list(set(merged[key]["modules"] + oc["modules"]))
            )

    # Sort by importance_score descending
    aggregated = sorted(
        merged.values(),
        key=lambda x: x.get("importance_score", 0.0),
        reverse=True
    )

    if top_n is not None:
        aggregated = aggregated[:top_n]

    return aggregated
 
# Optional Terminal Print Helpers
 

def print_module_outcomes(result):
    """Pretty print the module-by-module output."""
    print("\n==================== GENERATED COURSE OUTCOMES ====================\n")

    for mod in result:
        print(f"📘 Module {mod['module_id']}: {mod['title']}")
        print("Keywords:", ", ".join(mod["keywords"]))
        print("Outcomes:")
        for oc in mod["outcomes"]:
            print(f"  - [{oc['bloom_level']}] (score={oc.get('importance_score', 0):.2f})")
            print(f"    {oc['outcome']}")
        print("\n-------------------------------------------------------------------")


def print_total_course_outcomes(aggregated):
    """Pretty print the TOTAL aggregated course outcomes."""
    print("\n==================== TOTAL COURSE OUTCOMES (AGGREGATED) ====================\n")
    for i, oc in enumerate(aggregated, start=1):
        mods = ", ".join(str(m) for m in oc.get("modules", []))
        print(f"CO{i} (modules: {mods})")
        print(f"  [{oc['bloom_level']}] (score={oc.get('importance_score', 0):.2f})")
        print(f"  {oc['outcome']}\n")
    print("----------------------------------------------------------------------------")


# generate outcomes per module
def print_generated_outcomes(result):
    print("\n=========== GENERATED OUTCOMES ===========\n")
    for module in result:
        print(f"Module {module['module_id']} - {module['title']}")
        print("Keywords:", ", ".join(module["keywords"]))
        print("Outcomes:")
        for oc in module["outcomes"]:
            print(f" - [{oc['bloom_level']}] (score={oc.get('importance_score', 0):.2f}) {oc['outcome']}")
        print("\n------------------------------------------")
