import os
import random
import joblib  # Or import pickle if you used that
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import logging

# --- Configuration ---
# Set paths to your saved model files
MODEL_DIR = os.path.dirname(__file__) # Assumes models are in the same directory
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib')
MODEL_PATH = os.path.join(MODEL_DIR, 'svm_model.joblib')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder_level.joblib')
NUM_KEYWORDS = 7 # Number of top keywords to extract for outcome generation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Load Models ---
try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)
    label_encoder_level = joblib.load(LABEL_ENCODER_PATH)
    MODELS_LOADED = True
    logger.info("Successfully loaded TF-IDF vectorizer, SVM model, and LabelEncoder.")
except FileNotFoundError as e:
    logger.error(f"Error loading model files: {e}. Outcome generation will be disabled.")
    MODELS_LOADED = False
except Exception as e:
    logger.error(f"An unexpected error occurred loading models: {e}")
    MODELS_LOADED = False

# --- Action Templates (adapted from your notebook) ---
# Using random choice for variety, as in cell 20 of the notebook
actions = {
    "Remembering": [
        "List or identify the key elements of {keyword}.",
        "Recall and state the basic characteristics of {keyword}.",
        "Define and describe the purpose of {keyword}.",
        "Name essential aspects related to {keyword}."
    ],
    "Understanding": [
        "Explain the concept and importance of {keyword}.",
        "Summarize the role of {keyword} in its context.",
        "Discuss how {keyword} operates and why it is necessary.",
        "Interpret the main functions of {keyword}."
    ],
    "Applying": [
        "Demonstrate how {keyword} is applied in practical situations.",
        "Use {keyword} in a scenario to illustrate its application.",
        "Apply {keyword} to solve a real-world problem.",
        "Implement {keyword} in a specific task or project."
    ],
    "Analyzing": [
        "Examine and differentiate {keyword} from related concepts.",
        "Break down the structure of {keyword} and explore its components.",
        "Investigate the relationship between {keyword} and similar elements.",
        "Analyze how {keyword} contributes to its field and compare with alternatives."
    ],
    "Evaluating": [
        "Critique the effectiveness of {keyword} in meeting its intended goals.",
        "Assess the strengths and weaknesses of {keyword}.",
        "Judge the impact of {keyword} on its intended outcomes.",
        "Evaluate the value and limitations of {keyword} in various contexts."
    ],
    "Creating": [
        "Design an innovative approach or component within the context of {keyword}.",
        "Formulate a new model or method involving {keyword}.",
        "Develop a unique solution using {keyword}.",
        "Construct a proposal for improving or expanding {keyword}."
    ]
}

def get_template_for_level(bloom_level: str, keyword: str) -> str:
    """Selects a random template for the given Bloom level and keyword."""
    # Fallback template if level is unknown or has no templates
    fallback_template = f"Explore {keyword}."
    
    # Get templates for the level, default to fallback if level not found
    level_templates = actions.get(bloom_level)
    
    if not level_templates:
        logger.warning(f"No templates found for Bloom level '{bloom_level}'. Using fallback.")
        return fallback_template.format(keyword=keyword)
        
    try:
        # Choose a random template from the list for the specified level
        template = random.choice(level_templates)
        # Format the chosen template with the keyword
        return template.format(keyword=keyword)
    except Exception as e:
        logger.error(f"Error formatting template for level '{bloom_level}' with keyword '{keyword}': {e}")
        # Return fallback if formatting fails for any reason
        return fallback_template.format(keyword=keyword)


def extract_keywords_from_text(text: str, num_keywords: int = NUM_KEYWORDS) -> List[str]:
    """
    Extracts top keywords from the combined module text using TF-IDF scores.
    Uses a simple TF-IDF sum approach for keyword importance.
    """
    if not MODELS_LOADED:
        logger.warning("Models not loaded, cannot extract keywords.")
        return []
    if not text.strip():
        logger.warning("Input text for keyword extraction is empty.")
        return []
        
    try:
        # Use a local vectorizer just for keyword extraction based on term frequency
        # This is simpler than using the pre-trained one which might be fitted differently
        kw_vectorizer = TfidfVectorizer(stop_words='english', max_features=100) # Limit features
        tfidf_matrix = kw_vectorizer.fit_transform([text])
        
        # Sum TF-IDF scores for each term across the document (only one doc here)
        sum_tfidf = tfidf_matrix.sum(axis=0)
        
        # Get feature names (terms)
        terms = kw_vectorizer.get_feature_names_out()
        
        # Map terms to their scores
        scores = {terms[col]: sum_tfidf[0, col] for col in range(sum_tfidf.shape[1])}
        
        # Sort terms by score and get the top N
        sorted_terms = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        keywords = [term for term, score in sorted_terms[:num_keywords]]
        logger.info(f"Extracted keywords: {keywords}")
        return keywords
    except Exception as e:
        logger.error(f"Error during keyword extraction: {e}")
        return []

def map_keywords_to_bloom(keywords: List[str]) -> Dict[str, str]:
    """
    Predicts the Bloom's Taxonomy level for each keyword using the loaded SVM model.
    """
    if not MODELS_LOADED:
        logger.warning("Models not loaded, cannot map keywords to Bloom levels.")
        return {}
    if not keywords:
        logger.warning("No keywords provided for Bloom level mapping.")
        return {}
        
    try:
        # Transform keywords using the loaded TF-IDF vectorizer
        X_new = vectorizer.transform(keywords)
        
        # Predict encoded labels using the loaded SVM model
        predicted_levels_encoded = model.predict(X_new)
        
        # Decode labels using the loaded LabelEncoder
        predicted_levels = label_encoder_level.inverse_transform(predicted_levels_encoded)
        
        keyword_bloom_map = dict(zip(keywords, predicted_levels))
        logger.info(f"Mapped keywords to Bloom levels: {keyword_bloom_map}")
        return keyword_bloom_map
    except Exception as e:
        logger.error(f"Error during Bloom level prediction: {e}")
        return {}

def generate_outcome_statements(keyword_bloom_mapping: Dict[str, str]) -> List[str]:
    """
    Generates formatted course outcome statements based on keywords and their predicted Bloom levels.
    """
    if not keyword_bloom_mapping:
        logger.warning("No keyword-Bloom mapping provided for generating outcomes.")
        return []
        
    outcomes = []
    for keyword, bloom_level in keyword_bloom_mapping.items():
        try:
            # Generate the outcome text using the template function
            template = get_template_for_level(bloom_level, keyword)
            # Format the final outcome string
            outcome_statement = f"{bloom_level} - {keyword.capitalize()} - {template}"
            outcomes.append(outcome_statement)
        except Exception as e:
            logger.error(f"Error generating outcome for keyword '{keyword}' (level '{bloom_level}'): {e}")
            # Optionally add a placeholder or skip
            outcomes.append(f"Error generating outcome for {keyword}")
            
    logger.info(f"Generated {len(outcomes)} outcome statements.")
    return outcomes

def generate_course_outcomes_from_modules(modules: List[Dict[str, Any]]) -> List[str]:
    """
    Main function to generate course outcomes from a list of module dictionaries.
    Combines module content, extracts keywords, maps to Bloom levels, and generates statements.
    """
    if not MODELS_LOADED:
        logger.error("Cannot generate outcomes because models failed to load.")
        return ["Outcome generation is disabled due to model loading errors."]
        
    if not modules:
        logger.warning("No modules provided to generate course outcomes.")
        return ["No modules available to generate outcomes."]

    # --- Combine module content ---
    combined_module_content = ""
    for mod in modules:
        title = mod.get("title", "")
        content = mod.get("content", "")
        if content.strip().lower().startswith(title.strip().lower()):
             combined_module_content += f"{content}\n\n"
        else:
             combined_module_content += f"{title}\n{content}\n\n"

    if not combined_module_content.strip():
        logger.warning("Combined module content is empty.")
        return ["Could not extract valid content from modules."]

    # --- Generate Outcomes ---
    try:
        keywords = extract_keywords_from_text(combined_module_content)
        if not keywords:
            logger.info("No significant keywords extracted from module content.")
            return ["No significant keywords found to generate outcomes."]
            
        keyword_bloom_map = map_keywords_to_bloom(keywords)
        if not keyword_bloom_map:
             logger.warning("Failed to map keywords to Bloom levels.")
             return ["Failed to map keywords to Bloom's levels."]
             
        course_outcomes = generate_outcome_statements(keyword_bloom_map)
        
        return course_outcomes

    except Exception as e:
        logger.exception("An error occurred during the outcome generation pipeline.")
        return [f"An error occurred during outcome generation: {str(e)}"]

# --- Example Usage (for testing this file directly) ---
if __name__ == "__main__":
    # Ensure you have the model files (.joblib) in the same directory
    # or update the paths in the Configuration section.
    
    # Dummy module data for testing
    test_modules = [
        {"id": "module_1", "title": "Software Project Planning", "content": "Introduction to project planning, scope definition, and resource allocation."},
        {"id": "module_2", "title": "Cost Estimation", "content": "Techniques like COCOMO, function point analysis, and estimation models."},
        {"id": "module_3", "title": "Project Scheduling", "content": "Using Gantt charts, PERT, and Critical Path Method (CPM) for scheduling tasks."},
        {"id": "module_4", "title": "Configuration Management", "content": "Version control, change management, and baseline establishment."}
    ]
    
    if MODELS_LOADED:
        print("--- Testing Outcome Generation ---")
        generated_outcomes = generate_course_outcomes_from_modules(test_modules)
        print("\n--- Generated Course Outcomes ---")
        if generated_outcomes:
            for outcome in generated_outcomes:
                print(f"- {outcome}")
        else:
            print("No outcomes were generated.")
    else:
        print("Cannot run test: Models did not load.")