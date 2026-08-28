from pathlib import Path

import pytest

from recruiter_agent.config import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    resume_dir = tmp_path / "resume"
    resume_dir.mkdir()
    return Settings(
        _env_file=None,
        resume_folder=resume_dir,
        tracker_path=tmp_path / "tracker.xlsx",
        state_db_path=tmp_path / "agent.db",
        config_path=Path("./config/settings.yaml"),
    )
