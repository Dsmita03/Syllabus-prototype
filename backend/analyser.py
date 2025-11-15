# import os
# import random
# import joblib  # Or import pickle if you used that
# from typing import List, Dict, Any
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.svm import SVC
# from sklearn.preprocessing import LabelEncoder
# import logging

# # --- Configuration ---
# # Set paths to your saved model files
# MODEL_DIR = os.path.dirname(__file__) # Assumes models are in the same directory
# VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib')
# MODEL_PATH = os.path.join(MODEL_DIR, 'svm_model.joblib')
# LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder_level.joblib')
# NUM_KEYWORDS = 7 # Number of top keywords to extract for outcome generation

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # --- Load Models ---
# try:
#     vectorizer = joblib.load(VECTORIZER_PATH)
#     model = joblib.load(MODEL_PATH)
#     label_encoder_level = joblib.load(LABEL_ENCODER_PATH)
#     MODELS_LOADED = True
#     logger.info("Successfully loaded TF-IDF vectorizer, SVM model, and LabelEncoder.")
# except FileNotFoundError as e:
#     logger.error(f"Error loading model files: {e}. Outcome generation will be disabled.")
#     MODELS_LOADED = False
# except Exception as e:
#     logger.error(f"An unexpected error occurred loading models: {e}")
#     MODELS_LOADED = False

# # --- Action Templates (adapted from your notebook) ---
# # Using random choice for variety, as in cell 20 of the notebook
# actions = {
#     "Remembering": [
#         "List or identify the key elements of {keyword}.",
#         "Recall and state the basic characteristics of {keyword}.",
#         "Define and describe the purpose of {keyword}.",
#         "Name essential aspects related to {keyword}."
#     ],
#     "Understanding": [
#         "Explain the concept and importance of {keyword}.",
#         "Summarize the role of {keyword} in its context.",
#         "Discuss how {keyword} operates and why it is necessary.",
#         "Interpret the main functions of {keyword}."
#     ],
#     "Applying": [
#         "Demonstrate how {keyword} is applied in practical situations.",
#         "Use {keyword} in a scenario to illustrate its application.",
#         "Apply {keyword} to solve a real-world problem.",
#         "Implement {keyword} in a specific task or project."
#     ],
#     "Analyzing": [
#         "Examine and differentiate {keyword} from related concepts.",
#         "Break down the structure of {keyword} and explore its components.",
#         "Investigate the relationship between {keyword} and similar elements.",
#         "Analyze how {keyword} contributes to its field and compare with alternatives."
#     ],
#     "Evaluating": [
#         "Critique the effectiveness of {keyword} in meeting its intended goals.",
#         "Assess the strengths and weaknesses of {keyword}.",
#         "Judge the impact of {keyword} on its intended outcomes.",
#         "Evaluate the value and limitations of {keyword} in various contexts."
#     ],
#     "Creating": [
#         "Design an innovative approach or component within the context of {keyword}.",
#         "Formulate a new model or method involving {keyword}.",
#         "Develop a unique solution using {keyword}.",
#         "Construct a proposal for improving or expanding {keyword}."
#     ]
# }

# def get_template_for_level(bloom_level: str, keyword: str) -> str:
#     """Selects a random template for the given Bloom level and keyword."""
#     # Fallback template if level is unknown or has no templates
#     fallback_template = f"Explore {keyword}."
    
#     # Get templates for the level, default to fallback if level not found
#     level_templates = actions.get(bloom_level)
    
#     if not level_templates:
#         logger.warning(f"No templates found for Bloom level '{bloom_level}'. Using fallback.")
#         return fallback_template.format(keyword=keyword)
        
#     try:
#         # Choose a random template from the list for the specified level
#         template = random.choice(level_templates)
#         # Format the chosen template with the keyword
#         return template.format(keyword=keyword)
#     except Exception as e:
#         logger.error(f"Error formatting template for level '{bloom_level}' with keyword '{keyword}': {e}")
#         # Return fallback if formatting fails for any reason
#         return fallback_template.format(keyword=keyword)


# def extract_keywords_from_text(text: str, num_keywords: int = NUM_KEYWORDS) -> List[str]:
#     """
#     Extracts top keywords from the combined module text using TF-IDF scores.
#     Uses a simple TF-IDF sum approach for keyword importance.
#     """
#     if not MODELS_LOADED:
#         logger.warning("Models not loaded, cannot extract keywords.")
#         return []
#     if not text.strip():
#         logger.warning("Input text for keyword extraction is empty.")
#         return []
        
#     try:
#         # Use a local vectorizer just for keyword extraction based on term frequency
#         # This is simpler than using the pre-trained one which might be fitted differently
#         kw_vectorizer = TfidfVectorizer(stop_words='english', max_features=100) # Limit features
#         tfidf_matrix = kw_vectorizer.fit_transform([text])
        
#         # Sum TF-IDF scores for each term across the document (only one doc here)
#         sum_tfidf = tfidf_matrix.sum(axis=0)
        
#         # Get feature names (terms)
#         terms = kw_vectorizer.get_feature_names_out()
        
#         # Map terms to their scores
#         scores = {terms[col]: sum_tfidf[0, col] for col in range(sum_tfidf.shape[1])}
        
#         # Sort terms by score and get the top N
#         sorted_terms = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
#         keywords = [term for term, score in sorted_terms[:num_keywords]]
#         logger.info(f"Extracted keywords: {keywords}")
#         return keywords
#     except Exception as e:
#         logger.error(f"Error during keyword extraction: {e}")
#         return []

# def map_keywords_to_bloom(keywords: List[str]) -> Dict[str, str]:
#     """
#     Predicts the Bloom's Taxonomy level for each keyword using the loaded SVM model.
#     """
#     if not MODELS_LOADED:
#         logger.warning("Models not loaded, cannot map keywords to Bloom levels.")
#         return {}
#     if not keywords:
#         logger.warning("No keywords provided for Bloom level mapping.")
#         return {}
        
#     try:
#         # Transform keywords using the loaded TF-IDF vectorizer
#         X_new = vectorizer.transform(keywords)
        
#         # Predict encoded labels using the loaded SVM model
#         predicted_levels_encoded = model.predict(X_new)
        
#         # Decode labels using the loaded LabelEncoder
#         predicted_levels = label_encoder_level.inverse_transform(predicted_levels_encoded)
        
#         keyword_bloom_map = dict(zip(keywords, predicted_levels))
#         logger.info(f"Mapped keywords to Bloom levels: {keyword_bloom_map}")
#         return keyword_bloom_map
#     except Exception as e:
#         logger.error(f"Error during Bloom level prediction: {e}")
#         return {}

# def generate_outcome_statements(keyword_bloom_mapping: Dict[str, str]) -> List[str]:
#     """
#     Generates formatted course outcome statements based on keywords and their predicted Bloom levels.
#     """
#     if not keyword_bloom_mapping:
#         logger.warning("No keyword-Bloom mapping provided for generating outcomes.")
#         return []
        
#     outcomes = []
#     for keyword, bloom_level in keyword_bloom_mapping.items():
#         try:
#             # Generate the outcome text using the template function
#             template = get_template_for_level(bloom_level, keyword)
#             # Format the final outcome string
#             outcome_statement = f"{bloom_level} - {keyword.capitalize()} - {template}"
#             outcomes.append(outcome_statement)
#         except Exception as e:
#             logger.error(f"Error generating outcome for keyword '{keyword}' (level '{bloom_level}'): {e}")
#             # Optionally add a placeholder or skip
#             outcomes.append(f"Error generating outcome for {keyword}")
            
#     logger.info(f"Generated {len(outcomes)} outcome statements.")
#     return outcomes

# def generate_course_outcomes_from_modules(modules: List[Dict[str, Any]]) -> List[str]:
#     """
#     Main function to generate course outcomes from a list of module dictionaries.
#     Combines module content, extracts keywords, maps to Bloom levels, and generates statements.
#     """
#     if not MODELS_LOADED:
#         logger.error("Cannot generate outcomes because models failed to load.")
#         return ["Outcome generation is disabled due to model loading errors."]
        
#     if not modules:
#         logger.warning("No modules provided to generate course outcomes.")
#         return ["No modules available to generate outcomes."]

#     # --- Combine module content ---
#     combined_module_content = ""
#     for mod in modules:
#         title = mod.get("title", "")
#         content = mod.get("content", "")
#         if content.strip().lower().startswith(title.strip().lower()):
#              combined_module_content += f"{content}\n\n"
#         else:
#              combined_module_content += f"{title}\n{content}\n\n"

#     if not combined_module_content.strip():
#         logger.warning("Combined module content is empty.")
#         return ["Could not extract valid content from modules."]

#     # --- Generate Outcomes ---
#     try:
#         keywords = extract_keywords_from_text(combined_module_content)
#         if not keywords:
#             logger.info("No significant keywords extracted from module content.")
#             return ["No significant keywords found to generate outcomes."]
            
#         keyword_bloom_map = map_keywords_to_bloom(keywords)
#         if not keyword_bloom_map:
#              logger.warning("Failed to map keywords to Bloom levels.")
#              return ["Failed to map keywords to Bloom's levels."]
             
#         course_outcomes = generate_outcome_statements(keyword_bloom_map)
        
#         return course_outcomes

#     except Exception as e:
#         logger.exception("An error occurred during the outcome generation pipeline.")
#         return [f"An error occurred during outcome generation: {str(e)}"]

# # --- Example Usage (for testing this file directly) ---
# if __name__ == "__main__":
#     # Ensure you have the model files (.joblib) in the same directory
#     # or update the paths in the Configuration section.
    
#     # Dummy module data for testing
#     test_modules = [
#         {"id": "module_1", "title": "Software Project Planning", "content": "Introduction to project planning, scope definition, and resource allocation."},
#         {"id": "module_2", "title": "Cost Estimation", "content": "Techniques like COCOMO, function point analysis, and estimation models."},
#         {"id": "module_3", "title": "Project Scheduling", "content": "Using Gantt charts, PERT, and Critical Path Method (CPM) for scheduling tasks."},
#         {"id": "module_4", "title": "Configuration Management", "content": "Version control, change management, and baseline establishment."}
#     ]
    
#     if MODELS_LOADED:
#         print("--- Testing Outcome Generation ---")
#         generated_outcomes = generate_course_outcomes_from_modules(test_modules)
#         print("\n--- Generated Course Outcomes ---")
#         if generated_outcomes:
#             for outcome in generated_outcomes:
#                 print(f"- {outcome}")
#         else:
#             print("No outcomes were generated.")
#     else:
#         print("Cannot run test: Models did not load.")


# import json
# import spacy
# import networkx as nx
# from itertools import combinations
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.svm import SVC
# import joblib

# # ================================
# # 🔹 0. Load Models and NLP
# # ================================
# nlp = spacy.load("en_core_web_sm")

# # Load Bloom-level classification model and vectorizer
# try:
#     BLOOM_SVM_MODEL = joblib.load("models/bloom_svm_model.pkl")
#     BLOOM_VECTORIZER = joblib.load("models/tfidf_vectorizer.pkl")
#     MODELS_LOADED = True
# except Exception as e:
#     print("⚠️ Warning: Could not load Bloom models:", str(e))
#     MODELS_LOADED = False


# # ================================
# # 🔹 1. Entity & Relation Extraction
# # ================================
# def extract_entities_relations(text):
#     """
#     Extract entities and syntactic relationships from module content.
#     """
#     doc = nlp(text)
#     entities = []
#     relations = []

#     for ent in doc.ents:
#         entities.append((ent.text, ent.label_))

#     for token in doc:
#         if token.dep_ in ("nsubj", "dobj"):
#             relations.append((token.head.text, token.text))

#     return entities, relations


# # ================================
# # 🔹 2. Build Partially Connected Graph
# # ================================
# def build_partially_connected_graph(text):
#     """
#     Create a partially connected knowledge graph from text entities.
#     """
#     entities, _ = extract_entities_relations(text)

#     if not entities:
#         # fallback: comma-based split
#         entities = [(t.strip(), "CONCEPT") for t in text.split(",") if t.strip()]

#     G = nx.Graph()

#     # Add nodes
#     for entity in entities:
#         G.add_node(entity[0], label=entity[1])

#     # Fully connect all entities initially
#     for n1, n2 in combinations([e[0] for e in entities], 2):
#         G.add_edge(n1, n2)

#     # Make it partially connected
#     for node in list(G.nodes()):
#         neighbors = list(G.neighbors(node))
#         for neighbor in neighbors:
#             for neighbor_of_neighbor in list(G.neighbors(neighbor)):
#                 if neighbor_of_neighbor != node and G.has_edge(node, neighbor_of_neighbor):
#                     G.remove_edge(node, neighbor_of_neighbor)

#     return G


# # ================================
# # 🔹 3. Centrality Computation
# # ================================
# def compute_centrality(G):
#     """
#     Compute degree, closeness, and betweenness centrality.
#     Returns normalized combined importance.
#     """
#     degree_c = nx.degree_centrality(G)
#     closeness_c = nx.closeness_centrality(G)
#     betweenness_c = nx.betweenness_centrality(G)

#     combined = {}
#     for node in G.nodes():
#         combined[node] = (
#             degree_c.get(node, 0)
#             + closeness_c.get(node, 0)
#             + betweenness_c.get(node, 0)
#         ) / 3
#     return combined


# # ================================
# # 🔹 4. TF-IDF Keyword Extraction
# # ================================
# def extract_tfidf_keywords(text, top_n=10):
#     """
#     Extract top keywords using TF-IDF scores.
#     """
#     vectorizer = TfidfVectorizer(stop_words="english")
#     X = vectorizer.fit_transform([text])
#     scores = X.toarray().flatten()
#     terms = vectorizer.get_feature_names_out()

#     sorted_items = sorted(
#         zip(terms, scores), key=lambda x: x[1], reverse=True
#     )
#     top_keywords = [word for word, score in sorted_items[:top_n]]
#     return top_keywords


# # ================================
# # 🔹 5. Combine TF-IDF + Centrality
# # ================================
# def extract_keywords_with_centrality(text, top_n=7):
#     """
#     Combine TF-IDF scores and graph centrality to select keywords dynamically.
#     """
#     # TF-IDF keywords
#     tfidf_keywords = extract_tfidf_keywords(text, top_n * 2)

#     # Build graph using those keywords
#     G = nx.Graph()
#     G.add_nodes_from(tfidf_keywords)
#     for n1, n2 in combinations(tfidf_keywords, 2):
#         G.add_edge(n1, n2)

#     # Compute centrality
#     centrality_scores = compute_centrality(G)

#     # Merge (TF-IDF rank + centrality)
#     merged_scores = {}
#     for k in tfidf_keywords:
#         merged_scores[k] = centrality_scores.get(k, 0) + (1 / (tfidf_keywords.index(k) + 1))

#     ranked = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)
#     return [k for k, _ in ranked[:top_n]]

# # ================================
# # 🔹 6. Predict Bloom Levels (SVM)
# # ================================

# def map_keywords_to_bloom(keywords):
#     """
#     Use trained SVM model to predict Bloom taxonomy levels for keywords.
#     Converts numpy.int32 → string labels for JSON compatibility.
#     """
#     if not MODELS_LOADED:
#         return {k: "Unknown" for k in keywords}

#     # Transform keywords using TF-IDF
#     X = BLOOM_VECTORIZER.transform(keywords)
#     y_pred = BLOOM_SVM_MODEL.predict(X)

#     # Decode numerical labels back to string Bloom levels
#     try:
#         # Load the label encoder used during training
#         label_encoder = joblib.load("models/label_encoder.pkl")
#         decoded_labels = label_encoder.inverse_transform(y_pred)
#     except Exception:
#         # Fallback if label encoder missing
#         decoded_labels = [str(lbl) for lbl in y_pred]

#     # Ensure all outputs are plain strings (no numpy.int32)
#     decoded_labels = [str(lbl) for lbl in decoded_labels]

#     return dict(zip(keywords, decoded_labels))

# # ================================
# # 🔹 7. Generate Outcome Sentences
# # ================================
# def generate_outcome_statements(keyword_bloom_map):
#     """
#     Generate human-readable Course Outcomes using Bloom verbs.
#     """
#     outcomes = []
#     templates = {
#         "Remembering": "Recall and describe concepts of {}.",
#         "Understanding": "Explain the principles of {}.",
#         "Applying": "Apply knowledge of {} to real-world problems.",
#         "Analyzing": "Analyze components or processes of {}.",
#         "Evaluating": "Assess the effectiveness of {} using metrics.",
#         "Creating": "Design or develop solutions using {}."
#     }

#     for keyword, bloom in keyword_bloom_map.items():
#         sentence = templates.get(bloom, "Understand and apply {}.").format(keyword)
#         outcomes.append({
#             "keyword": keyword,
#             "bloom_level": str(bloom),
#             "outcome": sentence
#         })

#     return outcomes


# # ================================
# # 🔹 8. MAIN PIPELINE FUNCTION
# # ================================
# def generate_course_outcomes_from_modules(modules):
#     """
#     Full dynamic pipeline integrating TF-IDF, graph centrality, and Bloom model.
#     """
#     if not modules:
#         return {"success": False, "message": "No modules provided"}

#     # Combine all module content
#     combined_text = " ".join(
#         [f"{mod.get('title', '')} {mod.get('content', '') or mod.get('module_content', '')}" for mod in modules]
#     )

#     # Step 1: Keyword extraction
#     top_keywords = extract_keywords_with_centrality(combined_text)

#     # Step 2: Bloom level mapping
#     keyword_bloom_map = map_keywords_to_bloom(top_keywords)

#     # Step 3: Generate outcomes
#     outcomes = generate_outcome_statements(keyword_bloom_map)


#     # Step 4: Return structured result
#     return {
#         "success": True,
#         "total_modules": len(modules),
#         "keywords": top_keywords,
#         "outcomes": outcomes
#     }

# # ================================
# # 🔹 9. PRINT OUTCOMES (Terminal Display Helper)
# # ================================
# def print_generated_outcomes(outcome_result):
#     """
#     Pretty-print generated outcomes in a clean, readable terminal format.
#     Works with the dictionary returned by generate_course_outcomes_from_modules().
#     """
#     print("\n" + "=" * 80)
#     print("🎯  AUTOMATED COURSE OUTCOME EXTRACTION RESULTS")
#     print("=" * 80)

#     if not outcome_result or not outcome_result.get("success"):
#         print("⚠️  No valid outcomes generated.")
#         print("=" * 80)
#         return

#     print(f"\n📚  Total Modules Processed: {outcome_result.get('total_modules', 0)}")
#     print("\n🔑  Extracted Top Keywords:")
#     print("-" * 80)
#     for i, kw in enumerate(outcome_result.get("keywords", []), 1):
#         print(f"{i:>2}. {kw}")

#     print("\n🧠  Generated Course Outcomes:")
#     print("-" * 80)
#     outcomes = outcome_result.get("outcomes", [])
#     if not outcomes:
#         print("⚠️  No course outcomes available.")
#     else:
#         for idx, item in enumerate(outcomes, 1):
#             print(f"{idx:>2}. [{item['bloom_level']}] {item['outcome']}")

#     print("=" * 80 + "\n")


"""
ANALYSER.PY  (Final Production Version)
---------------------------------------
Generates Course Outcomes dynamically, module-by-module.

Features:
✓ Multi-word keyword extraction (NLP + TF-IDF + centrality)
✓ Per-module outcome generation (no mixing entire syllabus)
✓ Bloom-Level prediction using SVM + LabelEncoder
✓ Clean JSON output for backend API
"""

import spacy
import networkx as nx
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# ================================
# 0️⃣ Load NLP + ML Models
# ================================
nlp = spacy.load("en_core_web_sm")

try:
    BLOOM_SVM_MODEL = joblib.load("models/bloom_svm_model.pkl")
    TFIDF_VECTORIZER = joblib.load("models/tfidf_vectorizer.pkl")
    LABEL_ENCODER = joblib.load("models/label_encoder.pkl")
    MODELS_LOADED = True
except Exception as e:
    print("⚠️ Bloom models NOT loaded:", e)
    MODELS_LOADED = False


# ================================
# 1️⃣ PHRASE EXTRACTION
# ================================
def extract_phrases(text):
    """Extract multi-word noun phrases & entity phrases."""
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

    # Comma fallback
    for part in text.split(","):
        part = part.strip().lower()
        if len(part.split()) >= 2:
            phrases.add(part)

    # Cleanup
    cleaned = []
    for p in phrases:
        p = p.replace("-", " ").replace("  ", " ").strip()
        cleaned.append(p)

    return list(set(cleaned))


# ================================
# 2️⃣ TF-IDF Scoring
# ================================
def ranked_by_tfidf(phrases, full_text):
    if not phrases:
        return {}

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform([full_text])
    scores = X.toarray().flatten()
    terms = vectorizer.get_feature_names_out()

    phrase_score = {}
    for ph in phrases:
        total = 0
        count = 0
        for term, score in zip(terms, scores):
            if term in ph:
                total += score
                count += 1
        phrase_score[ph] = total / (count + 1e-6)
    return phrase_score


# ================================
# 3️⃣ Graph Centrality Scoring
# ================================
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


# ================================
# 4️⃣ Combined Keyword Ranking
# ================================
def extract_keywords(text, top_n=6):
    phrases = extract_phrases(text)
    if not phrases:
        return []

    tfidf_scores = ranked_by_tfidf(phrases, text)
    central_scores = ranked_by_centrality(phrases)

    final_scores = {}
    for p in phrases:
        final_scores[p] = (
            tfidf_scores.get(p, 0) * 0.6 +
            central_scores.get(p, 0) * 0.4
        )

    ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return [p for p, _ in ranked[:top_n]]


# ================================
# 5️⃣ Bloom Level Prediction
# ================================
def map_keywords_to_bloom(keywords):
    if not MODELS_LOADED:
        return {k: "Unknown" for k in keywords}

    X = TFIDF_VECTORIZER.transform(keywords)
    y_pred = BLOOM_SVM_MODEL.predict(X)

    # convert int → Bloom label
    bloom_levels = LABEL_ENCODER.inverse_transform(y_pred)

    return dict(zip(keywords, bloom_levels))


# ================================
# 6️⃣ Generate Course Outcome Statements
# ================================
def generate_outcome_statements(keyword_bloom_map):

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


# ================================
# 7️⃣ Main Function (MODULE-BY-MODULE)
# ================================
def generate_outcomes_per_module(modules):
    """
    Generate course outcomes for each module separately.
    Output Format:
    [
      {
        "module_id": 1,
        "title": "...",
        "keywords": [...],
        "outcomes": [...]
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

        # extract per-module keywords
        keywords = extract_keywords(text, top_n=6)

        # map to Bloom levels
        bloom_map = map_keywords_to_bloom(keywords)

        # generate COs
        outcomes = generate_outcome_statements(bloom_map)

        final_output.append({
            "module_id": mod.get("module_id"),
            "title": mod.get("title", f"Module {mod.get('module_id')}"),
            "keywords": keywords,
            "outcomes": outcomes
        })

    return final_output


# ================================
# 8️⃣ Optional Terminal Print Helper
# ================================
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
