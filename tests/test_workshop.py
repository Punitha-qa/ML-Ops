"""Lifecycle checks with real training, a fresh process and API requests."""
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from sms_mlops.common import DEFAULT_MODEL, ROOT, assert_disjoint, load_artifact, read_messages


class WorkshopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "labs/1_model_packaging/train.py"], cwd=ROOT, check=True, capture_output=True)
        cls.app = runpy.run_path(str(ROOT / "labs/2_model_deployment/app.py"))["app"]

    def test_prediction_after_reload_in_new_process(self):
        message = "Can we meet for lunch at one?"
        model, metadata = load_artifact()
        result = subprocess.run([sys.executable, "labs/1_model_packaging/predict.py", message], cwd=ROOT,
                                check=True, capture_output=True, text=True)
        actual = json.loads(result.stdout)
        self.assertEqual(actual["label"], model.predict([message])[0])
        self.assertEqual(actual["model_version"], metadata["model_version"])

    def test_api_page_health_and_prediction(self):
        model, _ = load_artifact()
        with TestClient(self.app) as client:
            self.assertEqual(client.get("/").status_code, 200)
            self.assertIn("Check message", client.get("/").text)
            self.assertEqual(client.get("/health").json()["status"], "ready")
            response = client.post("/predict", json={"message": "Lunch at one?"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["label"], model.predict(["Lunch at one?"])[0])

    def test_invalid_api_inputs_are_rejected(self):
        with TestClient(self.app) as client:
            for payload in [{}, {"message": "   "}, {"message": 12}, {"message": "x" * 2001},
                            {"message": "Hello", "extra": True}]:
                with self.subTest(payload=str(payload)[:50]):
                    self.assertEqual(client.post("/predict", json=payload).status_code, 422)

    def test_prepared_splits_are_disjoint(self):
        datasets = [read_messages(ROOT / "data" / name)[0] for name in
                    ["train.csv", "baseline.csv", "new_same_distribution.csv", "new_messages.csv"]]
        for i, first in enumerate(datasets):
            for second in datasets[i + 1:]:
                assert_disjoint(first, second)

    def test_corrupt_artifact_is_rejected_before_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / DEFAULT_MODEL.name
            shutil.copy2(DEFAULT_MODEL, artifact)
            shutil.copy2(DEFAULT_MODEL.with_suffix(".metadata.json"), artifact.with_suffix(".metadata.json"))
            with artifact.open("ab") as stream:
                stream.write(b"unexpected change")
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_artifact(artifact)

    def test_monitoring_shift_control_and_small_sample_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            command = [sys.executable, "labs/3_model_monitoring/monitor.py", "--output", str(output)]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
            self.assertEqual(json.loads(output.read_text())["decision"], "INVESTIGATE_AND_CONSIDER_RETRAINING")
            subprocess.run(command + ["--new-data", "data/new_same_distribution.csv"], cwd=ROOT, check=True, capture_output=True)
            control = json.loads(output.read_text())
            self.assertEqual(control["decision"], "NO_THRESHOLD_ALERT")
            self.assertIn("Continue monitoring", control["next_step"])
            subprocess.run(command + ["--min-rows", "100"], cwd=ROOT, check=True, capture_output=True)
            small = json.loads(output.read_text())
            self.assertEqual(small["decision"], "INSUFFICIENT_DATA")
            self.assertIn("Collect more", small["next_step"])


if __name__ == "__main__":
    unittest.main()
