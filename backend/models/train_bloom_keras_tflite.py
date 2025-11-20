# models/train_bloom_keras_tflite.py
# Trains and saves:
#   - Keras text classifier (.keras)
#   - TFLite version (.tflite) for CPU-friendly "lite" inference
#   - Tokenizer (tokenizer.pkl)
#   - LabelEncoder (label_encoder.pkl)

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import LabelEncoder
import pickle
import random

# Reproducibility
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

 
# 1. Training data

training_keywords = [
    "software project planning",
    "project scheduling",
    "gantt chart",
    "pert chart",
    "critical path method",
    "configuration management",
    "cost estimation",
    "cocomo model",
    "function point analysis",
    "version control",
    "linked list implementation",
    "stack and queue operations",
    "database normalization",
    "machine learning basics",
]

training_labels = [
    "Understanding",    
    "Applying",         
    "Applying",        
    "Applying",         
    "Analyzing",       
    "Understanding",    
    "Analyzing",       
    "Analyzing",       
    "Analyzing",       
    "Remembering",     
    "Applying",        
    "Applying",         
    "Analyzing",        
    "Understanding",    
]

assert len(training_keywords) == len(training_labels)

 
# 2. Encode labels
 
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(training_labels)
num_classes = len(label_encoder.classes_)

 
# 3. Tokenize text
 
MAX_VOCAB_SIZE = 5000
MAX_LEN = 10  # MUST match analyser.py

tokenizer = keras.preprocessing.text.Tokenizer(
    num_words=MAX_VOCAB_SIZE,
    oov_token="<OOV>"
)
tokenizer.fit_on_texts(training_keywords)
seqs = tokenizer.texts_to_sequences(training_keywords)
X = keras.preprocessing.sequence.pad_sequences(
    seqs,
    maxlen=MAX_LEN,
    padding="post"
)

 
# 4. Build Keras model
 
model = keras.Sequential([
    layers.Embedding(input_dim=MAX_VOCAB_SIZE, output_dim=32, input_length=MAX_LEN),
    layers.GlobalAveragePooling1D(),
    layers.Dense(32, activation="relu"),
    layers.Dense(num_classes, activation="softmax"),
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()
model.fit(X, y, epochs=60, batch_size=4, verbose=1)

# 5. Save Keras assets
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

keras_model_path = os.path.join(MODELS_DIR, "bloom_keras_model.keras")
model.save(keras_model_path)

with open(os.path.join(MODELS_DIR, "tokenizer.pkl"), "wb") as f:
    pickle.dump(tokenizer, f)

with open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "wb") as f:
    pickle.dump(label_encoder, f)

print("Exported Keras model and assets:")
print(f" - {keras_model_path}")
print(f" - {os.path.join(MODELS_DIR, 'tokenizer.pkl')}")
print(f" - {os.path.join(MODELS_DIR, 'label_encoder.pkl')}")
print("Label classes:", list(label_encoder.classes_))
print("MAX_LEN used:", MAX_LEN)

# 6. Convert to TFLite (Keras Lite)
 
# tflite_model_path = os.path.join(MODELS_DIR, "bloom_keras_model.tflite")

# converter = tf.lite.TFLiteConverter.from_keras_model(model)

# # Optional optimizations for smaller / faster model on CPU
# converter.optimizations = [tf.lite.Optimize.DEFAULT]

# tflite_model = converter.convert()
# with open(tflite_model_path, "wb") as f:
#     f.write(tflite_model)

# print("Exported TFLite model:")
# print(f" - {tflite_model_path}")
