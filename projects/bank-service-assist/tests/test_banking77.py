"""Small authored fixtures only; these are not imported BANKING77 samples."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "banking77", Path(__file__).resolve().parents[1] / "scripts/banking77.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BankingDataChecks(unittest.TestCase):
    def test_tampered_snapshot_is_rejected_before_profiling(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            original = b"text,category\nInvented request,a\n"
            (folder / "train.csv").write_bytes(original + b"tampered")
            manifest = {"files": {"train.csv": {
                "bytes": len(original), "sha256": module.digest(original)
            }}}
            (folder / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                module.read_snapshot(folder)

    def test_csv_records_not_physical_lines(self):
        rows = module.parse_csv(b'text,category\n"Line one,\nline two",a\n', {"a"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["text"], "Line one,\nline two")

    def test_unknown_label_is_rejected(self):
        with self.assertRaises(ValueError):
            module.parse_csv(b"text,category\nAn invented request,b\n", {"a"})

    def test_extra_field_and_blank_text_are_rejected(self):
        for data in (b"text,category\nx,a,extra\n", b"text,category\n ,a\n"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                module.parse_csv(data, {"a"})

    def test_overlap_and_conflicting_labels_are_not_hidden(self):
        train = [{"text": "Check   STATUS", "category": "a"}] * 2
        test = [{"text": "check status", "category": "b"}]
        result = module.profile(train, test, ["a", "b"])
        self.assertEqual(result["splits"]["train"]["normalized_duplicate_excess"], 1)
        self.assertEqual(result["cross_split_normalized_groups"], 1)
        self.assertEqual(result["conflicting_label_groups"], 1)
        self.assertEqual(result["splits"]["test"]["missing_labels"], ["a"])


if __name__ == "__main__":
    unittest.main()
