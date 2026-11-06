"""Beginner Program 1, second run: load and predict in a new Python process.

Run from the repository root after example.py has finished.
There are no training examples or fit calls in this script.
Only load the artifact created by your own trusted training script.
"""
# pathlib (Python standard library): represent the saved file's location.
from pathlib import Path

# joblib (installed library): restore the fitted converter and classifier.
# scikit-learn must also be installed: the saved objects come from that library.
import joblib

model_file = Path("artifacts") / "learning-spam-filter.joblib"
if not model_file.is_file():
    raise SystemExit("First run: python videos/program-1/example.py")

loaded_model = joblib.load(model_file)
new_message = "Can we meet for lunch tomorrow?"
prediction = loaded_model.predict([new_message])
print("Message:", new_message)
print("Prediction:", prediction[0])
