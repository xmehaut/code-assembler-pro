import unittest
import tempfile
import shutil
import time
import os
from pathlib import Path
import sys

# Ajout du src au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.core import assemble_codebase


class TestDeltaScenario(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

        # Structure complexe pour tester l'indentation
        # root/
        #   ├── api/
        #   │    └── config.py  <-- Fichier A
        #   └── db/
        #        └── config.py  <-- Fichier B (Même nom !)

        (self.root / "api").mkdir()
        (self.root / "db").mkdir()

        self.file_a = self.root / "api" / "config.py"
        self.file_b = self.root / "db" / "config.py"

        self.file_a.write_text("API_CONFIG = 1", encoding="utf-8")
        self.file_b.write_text("DB_CONFIG = 1", encoding="utf-8")

        past_time = time.time() - 300
        os.utime(self.file_a, (past_time, past_time))
        os.utime(self.file_b, (past_time, past_time))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_duplicate_filenames_handling(self):
        """
        Vérifie que modifier db/config.py n'inclut pas api/config.py
        malgré le même nom de fichier.
        """
        ref_md = self.root / "reference.md"
        delta_md = self.root / "delta.md"

        # 1. Générer la référence
        assemble_codebase(
            paths=[str(self.root)],
            extensions=[".py"],
            output=str(ref_md),
            show_progress=False
        )

        # Pause pour garantir un mtime différent (systèmes de fichiers rapides)
        time.sleep(1.1)

        # 2. Modifier SEULEMENT db/config.py
        self.file_b.write_text("DB_CONFIG = 2  # Modified", encoding="utf-8")

        # 3. Générer le delta
        assemble_codebase(
            paths=[str(self.root)],
            extensions=[".py"],
            output=str(delta_md),
            since=str(ref_md),  # <-- Option clé
            show_progress=False
        )

        # 4. Analyser le résultat
        content = delta_md.read_text(encoding="utf-8")

        # VÉRIFICATIONS
        print("\n--- Contenu du Delta ---")
        print(content)
        print("------------------------")

        # Le fichier modifié DOIT être présent
        self.assertIn("DB_CONFIG = 2", content, "Le fichier modifié (db/config.py) est absent !")

        # Le fichier non modifié NE DOIT PAS être présent
        self.assertNotIn("API_CONFIG = 1", content, "Le fichier non modifié (api/config.py) est présent à tort !")

        # Vérifier le header
        self.assertIn("> ✏️  Modified (1): config.py", content)


if __name__ == "__main__":
    unittest.main()