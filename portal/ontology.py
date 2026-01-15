import json
import os

# Updated to use relative path for portability
VOCAB_FILE = os.path.join(os.path.dirname(__file__), "vocabulary.json")

def load_vocabulary():
    """Loads the vocabulary JSON file."""
    if not os.path.exists(VOCAB_FILE):
        return {}
    with open(VOCAB_FILE, 'r') as f:
        return json.load(f)

def save_vocabulary(vocab):
    """Saves the vocabulary to JSON."""
    with open(VOCAB_FILE, 'w') as f:
        json.dump(vocab, f, indent=4)

def get_sections():
    """Returns list of top-level sections."""
    vocab = load_vocabulary()
    return list(vocab.keys())

def get_categories(section):
    """Returns categories in a section."""
    vocab = load_vocabulary()
    if section in vocab:
        return vocab[section]
    return {}

def add_term(section, category, term):
    """Adds a new term to a category within a section."""
    vocab = load_vocabulary()
    if section in vocab and category in vocab[section]:
        if term not in vocab[section][category]['values']:
            vocab[section][category]['values'].append(term)
            save_vocabulary(vocab)
            return True, f"Added '{term}' to '{category}'."
        else:
            return False, f"'{term}' already exists in '{category}'."
    else:
        return False, f"Category '{category}' not found in '{section}'."

def add_category(section, category, description=""):
    """Adds a new category to a section."""
    vocab = load_vocabulary()
    if section not in vocab:
         vocab[section] = {}
         
    if category not in vocab[section]:
        vocab[section][category] = {"description": description, "values": []}
        save_vocabulary(vocab)
        return True, f"Created category '{category}' in '{section}'."
    return False, "Category already exists."
