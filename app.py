"""Streamlit entry point for the PyAtlas dashboard."""

import streamlit as st

from ui.dashboard import initialize_session_state, render_dashboard


def main() -> None:
    """Configure Streamlit and render the application."""

    st.set_page_config(
        page_title="PyAtlas",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_session_state()
    render_dashboard()


if __name__ == "__main__":
    main()
