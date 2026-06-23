import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from badge_harness import HarnessError, upload_to_tmp


class UploadToTmpTests(unittest.TestCase):
    def test_single_file_uploads_as_run_py(self):
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as drive_dir:
            src = Path(src_dir) / "probe.py"
            src.write_text("print('marker')\n", encoding="utf-8")

            uploaded = upload_to_tmp(src, Path(drive_dir))

            self.assertEqual([Path(drive_dir) / "tmp" / "run.py"], uploaded)
            self.assertEqual("print('marker')\n", (Path(drive_dir) / "tmp" / "run.py").read_text(encoding="utf-8"))

    def test_directory_upload_preserves_relative_paths(self):
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as drive_dir:
            src = Path(src_dir)
            (src / "lib").mkdir()
            (src / "run.py").write_text("import lib.helper\n", encoding="utf-8")
            (src / "lib" / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")

            uploaded = upload_to_tmp(src, Path(drive_dir))

            self.assertEqual(
                {Path(drive_dir) / "tmp" / "run.py", Path(drive_dir) / "tmp" / "lib" / "helper.py"},
                set(uploaded),
            )
            self.assertTrue((Path(drive_dir) / "tmp" / "lib" / "helper.py").is_file())

    def test_directory_upload_requires_run_py(self):
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as drive_dir:
            src = Path(src_dir)
            (src / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")

            with self.assertRaises(HarnessError):
                upload_to_tmp(src, Path(drive_dir))


if __name__ == "__main__":
    unittest.main()
