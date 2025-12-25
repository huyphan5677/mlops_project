from pathlib import Path
import importlib
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))


def test_config_module_importable():
    """
    Config module should be importable without errors.
    """
    module = importlib.import_module("btc_prediction.config")
    assert module is not None


def test_project_root_is_path():
    """
    PROJ_ROOT should be a pathlib.Path instance.
    """
    from btc_prediction.config import PROJ_ROOT

    assert isinstance(PROJ_ROOT, Path)


def test_data_directories_structure():
    """
    Data directory structure should be correctly defined.
    """
    from btc_prediction.config import (
        PROJ_ROOT,
        DATA_DIR,
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
    )

    assert DATA_DIR == PROJ_ROOT / "data"
    assert RAW_DATA_DIR == DATA_DIR / "raw"
    assert INTERIM_DATA_DIR == DATA_DIR / "interim"
    assert PROCESSED_DATA_DIR == DATA_DIR / "processed"
    assert EXTERNAL_DATA_DIR == DATA_DIR / "external"


def test_models_and_reports_dirs():
    """
    Models and reports directories should be correctly defined.
    """
    from btc_prediction.config import (
        PROJ_ROOT,
        MODELS_DIR,
        REPORTS_DIR,
        FIGURES_DIR,
    )

    assert MODELS_DIR == PROJ_ROOT / "models"
    assert REPORTS_DIR == PROJ_ROOT / "reports"
    assert FIGURES_DIR == REPORTS_DIR / "figures"


def test_paths_are_path_objects():
    """
    Config paths should be Path objects, not create directories.
    """
    from btc_prediction.config import DATA_DIR, MODELS_DIR

    assert isinstance(DATA_DIR, Path)
    assert isinstance(MODELS_DIR, Path)