import sys
import unittest
from pathlib import Path

import requests

sys.path.append(
    "C:\\Users\\Stefa\Documents\\Programmeren\\4property\\Elasticsearch-to-MySQL\\PMX-api\\"
)

from app.api.core.config.settings import TestingConfig


class ErrorTests(unittest.TestCase):
    def test_respond_200(self):
        response = requests.get(f"{TestingConfig.URL}docs")
        self.assertEqual(response.status_code, 200)

    def test_respond_404(self):
        response = requests.get(f"{TestingConfig.URL}not_a_real_endpoint")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[3]
    unittest.main()
