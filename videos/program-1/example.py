"""Beginner Program 1, first run: train and save, then exit Python.

Run from the repository root after completing README setup.
After this script exits, run videos/program-1/predict.py separately.
Six synthetic examples illustrate the flow, not production accuracy.

Where our tools come from:
- Python's standard library ships with Python; pathlib is one of its modules.
- joblib and scikit-learn are separately installed libraries (see repo setup).
  scikit-learn is the installation name; sklearn is its Python import name.
- "from ... import ..." brings a named tool from a module into this program.
- TfidfVectorizer, LogisticRegression and Pipeline are classes. Adding ()
  creates an object using that class. Creating them does not train them;
  model.fit(train_text, train_labels) is the training step below.
"""
# pathlib (Python standard library): Path handles folder and file paths.
from pathlib import Path

# joblib (installed library): dump saves and load restores the fitted pipeline.
import joblib
# sklearn.feature_extraction.text: text tools; this converts messages to numbers.
from sklearn.feature_extraction.text import TfidfVectorizer
# sklearn.linear_model: model algorithms; this learns to classify spam or ham.
# Despite its name, LogisticRegression is a classifier in this example.
from sklearn.linear_model import LogisticRegression
# sklearn.pipeline: Pipeline connects the converter and classifier in order.
from sklearn.pipeline import Pipeline

train_text = [
    "Claim your free prize now",
    "You have won a cash reward",
    "Call now to claim your winnings",
    "Can we meet for lunch",
    "Please bring your laptop tomorrow",
    "I will reach home by evening",
]
train_labels = ["spam", "spam", "spam", "ham", "ham", "ham"]

model = Pipeline([
    ("text_converter", TfidfVectorizer()),
    ("classifier", LogisticRegression()),
])
model.fit(train_text, train_labels)

model_folder = Path("artifacts")
model_folder.mkdir(exist_ok=True)
model_file = model_folder / "learning-spam-filter.joblib"
joblib.dump(model, model_file)
print("Saved the trained pipeline to:", model_file)
print("Training is complete. This Python process now exits.")
print("Next, start a new process: python videos/program-1/predict.py")
