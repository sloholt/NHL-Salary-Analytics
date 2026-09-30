from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Repository root
# ---------------------------------------------------------------------------


def _find_repo_root() -> Path:
    """
    Locate the repository root.

    Order of precedence:
      1. The NHL_SALARY_ROOT environment variable, if set.
      2. The nearest parent directory containing .git or pyproject.toml.
      3. The nearest parent directory containing a data/ folder.
    """
    env_root = os.getenv("NHL_SALARY_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "pyproject.toml").is_file():
            return parent

    for parent in here.parents:
        if (parent / "data").is_dir():
            return parent

    raise RuntimeError(
        f"Could not find the repo root above {here}. "
        "Set the NHL_SALARY_ROOT environment variable to the repo folder."
    )


REPO_ROOT: Path = _find_repo_root()


# ---------------------------------------------------------------------------
# Data directories
# ---------------------------------------------------------------------------

DATA_DIR: Path = REPO_ROOT / "data"

RAW_DIR: Path = DATA_DIR / "raw"  # original, never edited by code
PLAYER_DATA_DIR: Path = RAW_DIR / "player_data"
PROCESSED_DIR: Path = DATA_DIR / "processed"  # cleaned/derived data (created on demand)
REFERENCE_DIR: Path = DATA_DIR / "reference"  # team names & logo mappings
RESULTS_DIR: Path = DATA_DIR / "results"  # model outputs (GLM, GMM, Gurobi)


# ---------------------------------------------------------------------------
# Raw data files
# ---------------------------------------------------------------------------

SALARY_DATA_CSV: Path = RAW_DIR / "SalaryData.csv"
TEAM_DATA_CSV: Path = RAW_DIR / "TeamData.csv"
COMBINED_CAP_HITS_XLSX: Path = RAW_DIR / "NHL_Combined_Cap_Hits_2015-2025.xlsx"
OPT_GINI_TEAMS_XLSX: Path = RAW_DIR / "Opt_Gini_teams.xlsx"


# ---------------------------------------------------------------------------
# Reference files
# ---------------------------------------------------------------------------

TEAM_NAMES_JSON: Path = REFERENCE_DIR / "Team_Names.json"


# ---------------------------------------------------------------------------
# Model result files
# ---------------------------------------------------------------------------

GLM_RESULTS_CSV: Path = RESULTS_DIR / "glm_model_results.csv"
GMM_RESULTS_CSV: Path = RESULTS_DIR / "gmm_model_results.csv"


# ---------------------------------------------------------------------------
# Paper
# ---------------------------------------------------------------------------

PAPER_DIR: Path = REPO_ROOT / "paper"
PAPER_DOCS_DIR: Path = PAPER_DIR / "docs"
PAPER_SRC_DIR: Path = PAPER_DIR / "src"
FIGURES_DIR: Path = PAPER_DOCS_DIR / "figures"  # created on demand


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_FILES: tuple[Path, ...] = (
    SALARY_DATA_CSV,
    TEAM_DATA_CSV,
    TEAM_NAMES_JSON,
    GLM_RESULTS_CSV,
    GMM_RESULTS_CSV,
)


def ensure_output_dirs() -> None:
    """Create directories that code writes into, if they don't exist yet."""
    for directory in (PROCESSED_DIR, RESULTS_DIR, FIGURES_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def missing_files(paths: tuple[Path, ...] = REQUIRED_FILES) -> list[Path]:
    """Return any required files that don't exist on disk."""
    return [p for p in paths if not p.is_file()]


def check_paths() -> None:
    """
    Raise a clear error listing every missing file.

    Call this at dashboard startup so a moved or renamed file fails
    immediately with a readable message instead of deep inside pandas.
    """
    missing = missing_files()
    if missing:
        listed = "\n  ".join(str(p.relative_to(REPO_ROOT)) for p in missing)
        raise FileNotFoundError(
            f"Missing data files (repo root: {REPO_ROOT}):\n  {listed}"
        )


if __name__ == "__main__":
    # From the repo root, run:  python src/nhl_salary/paths.py
    # (works without installing anything, since this file imports nothing
    # from the rest of the package)
    print(f"REPO_ROOT: {REPO_ROOT}")
    for name, value in sorted(globals().items()):
        if name.isupper() and isinstance(value, Path) and name != "REPO_ROOT":
            status = "ok" if value.exists() else "MISSING"
            print(f"{name:<24} {status:<8} {value.relative_to(REPO_ROOT)}")
