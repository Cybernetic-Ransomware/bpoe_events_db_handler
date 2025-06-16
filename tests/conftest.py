import sys

import pytest
from dotenv import load_dotenv
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

load_dotenv(dotenv_path=Path(".") / ".env.test", override=True)

@pytest.fixture(scope="session")
def app():
    from src.main import app as fastapi_app
    return fastapi_app
