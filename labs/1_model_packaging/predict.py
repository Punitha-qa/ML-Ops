"""Load the saved pipeline and predict without training again."""
# argparse (Python standard library): read the message from the command line.
import argparse
# json (Python standard library): format our prediction as JSON text.
import json

# Our workshop helper in src/sms_mlops/common.py: check the saved artifact and
# load the fitted pipeline using joblib. It returns the pipeline and metadata.
from sms_mlops.common import load_artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", help="A message to classify, enclosed in quotes")
    args = parser.parse_args()
    if not args.message.strip() or len(args.message) > 2000:
        parser.error("Use a nonblank message of at most 2000 characters.")
    model, metadata = load_artifact()
    prediction = model.predict([args.message.strip()])[0]
    print(json.dumps({"label": str(prediction), "model_version": metadata["model_version"]}))


if __name__ == "__main__":
    main()
