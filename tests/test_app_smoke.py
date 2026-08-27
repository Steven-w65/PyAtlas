from pathlib import Path

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
