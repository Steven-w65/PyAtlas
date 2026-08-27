import logging
from pathlib import Path

from streamlit import config
from streamlit.testing.v1 import AppTest


SAMPLES = Path(__file__).parent / "sample_projects"
APP_PATH = Path(__file__).parents[1] / "app.py"


def test_app_renders_initial_state_without_exception() -> None:
    app = AppTest.from_file(APP_PATH)

    app.run(timeout=20)

    assert not app.exception
    assert [item.value for item in app.title] == ["PyAtlas"]
    assert app.button[0].label == "Analyze project"
    assert app.info[0].value.startswith("Choose a local Python project")


def test_app_omits_the_clipped_local_intelligence_kicker() -> None:
    """Catch the removed pre-title label returning beneath the fixed header."""

    app = AppTest.from_file(APP_PATH)

    app.run(timeout=20)

    assert all("Local code intelligence" not in item.value for item in app.markdown)


def test_streamlit_toolbar_uses_viewer_mode() -> None:
    """Catch localhost exposing developer-only controls such as Deploy."""

    assert config.get_option("client.toolbarMode") == "viewer"


def test_app_analyzes_project_and_renders_summary() -> None:
    app = AppTest.from_file(APP_PATH)
    app.run(timeout=20)

    app.text_input[0].input(str(SAMPLES / "simple_project"))
    app.button[0].click()
    app.run(timeout=30)

    assert not app.exception
    assert len(app.metric) >= 6
    assert any(item.label == "Python Files" and item.value == "2" for item in app.metric)
    assert any("simple_project" in item.value for item in app.markdown)
    assert len(app.dataframe) >= 3


def test_app_emits_no_streamlit_deprecation_warnings(caplog) -> None:
    """Catch retired widget arguments anywhere in the complete dashboard flow."""

    from streamlit import deprecation_util

    caplog.set_level(logging.WARNING)
    deprecation_util._LOGGER.addHandler(caplog.handler)
    try:
        app = AppTest.from_file(APP_PATH)
        app.run(timeout=20)

        app.text_input[0].input(str(SAMPLES / "simple_project"))
        app.button[0].click()
        app.run(timeout=30)
    finally:
        deprecation_util._LOGGER.removeHandler(caplog.handler)

    assert "Please replace `use_container_width` with `width`" not in caplog.text
