"""Shared visual language for the PyAtlas Streamlit interface."""

APP_CSS = r"""
<style>
:root {
    --atlas-bg: light-dark(#f2f5fa, #06101d);
    --atlas-bg-raised: light-dark(#ffffff, #091728);
    --atlas-panel: light-dark(#ffffff, #0e1d31);
    --atlas-panel-hover: light-dark(#edf3fa, #142842);
    --atlas-border: light-dark(rgba(15, 23, 42, 0.17), rgba(148, 163, 184, 0.23));
    --atlas-border-strong: light-dark(rgba(0, 127, 163, 0.40), rgba(83, 212, 255, 0.38));
    --atlas-text: light-dark(#111827, #f4f8ff);
    --atlas-muted: light-dark(#43516a, #a8b8cc);
    --atlas-subtle: light-dark(#637089, #7f91aa);
    --atlas-cyan: light-dark(#007fa3, #53d4ff);
    --atlas-indigo: light-dark(#5557c9, #8587ff);
    --atlas-green: light-dark(#087d62, #3dd6a3);
    --atlas-yellow: light-dark(#956200, #f9c74f);
    --atlas-orange: light-dark(#b54c00, #f8961e);
    --atlas-red: light-dark(#c73550, #f05d75);
    --atlas-header: light-dark(rgba(242, 245, 250, 0.90), rgba(6, 16, 29, 0.88));
    --atlas-ribbon: light-dark(#f9fcff, #0c1c30);
    --atlas-sidebar: light-dark(#eaf0f7, #081422);
    --atlas-control: light-dark(#ffffff, #0d1b2d);
    --atlas-alert: light-dark(#eef6ff, #0f2035);
    --atlas-code: light-dark(#f1f5f9, #060e19);
    --atlas-primary: light-dark(#007fa3, #53d4ff);
    --atlas-primary-hover: light-dark(#006b8a, #78dfff);
    --atlas-primary-text: light-dark(#ffffff, #04111c);
    --atlas-privacy-text: light-dark(#35675b, #9ec7bd);
    --atlas-radius: 14px;
    --atlas-shadow: light-dark(0 16px 38px rgba(15, 23, 42, 0.10), 0 18px 44px rgba(0, 0, 0, 0.24));
    --atlas-shadow-soft: light-dark(0 7px 22px rgba(15, 23, 42, 0.07), 0 8px 26px rgba(0, 0, 0, 0.16));
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 88% -8%, color-mix(in srgb, var(--atlas-indigo) 8%, transparent) 0, transparent 30rem),
        var(--atlas-bg);
    color: var(--atlas-text);
}

[data-testid="stHeader"] {
    background: var(--atlas-header);
    border-bottom: 1px solid var(--atlas-border);
    backdrop-filter: blur(18px);
}

[data-testid="stToolbar"] {
    right: 1rem;
}

.block-container {
    max-width: 1480px;
    padding-top: 3.25rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] strong {
    color: var(--atlas-text);
    letter-spacing: -0.025em;
}

h1 {
    font-size: clamp(2.1rem, 3.3vw, 3.15rem) !important;
    line-height: 1.02 !important;
    font-weight: 760 !important;
    margin: 0.1rem 0 0.35rem !important;
}

h2, h3 {
    font-weight: 680 !important;
}

p, li, label, [data-testid="stCaptionContainer"] {
    color: var(--atlas-muted);
}

a {
    color: var(--atlas-cyan) !important;
}

.atlas-lead {
    max-width: 900px;
    color: var(--atlas-muted) !important;
    font-size: 0.92rem;
    line-height: 1.45;
    margin: 0 0 0.5rem;
}

.atlas-rule {
    height: 1px;
    background: linear-gradient(90deg, var(--atlas-border-strong), transparent 72%);
    margin: 0 0 0.65rem;
}

.project-ribbon {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.68rem 0.82rem;
    margin: 0.1rem 0 0.45rem;
    border: 1px solid var(--atlas-border-strong);
    border-radius: var(--atlas-radius);
    background: var(--atlas-ribbon);
    box-shadow: var(--atlas-shadow);
}

.project-ribbon__eyebrow,
.atlas-section__eyebrow,
.sidebar-eyebrow {
    color: var(--atlas-cyan);
    font-size: 0.67rem;
    font-weight: 760;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.project-ribbon__name {
    color: var(--atlas-text);
    font-size: 1.08rem;
    font-weight: 700;
    margin-top: 0.2rem;
}

.project-ribbon__path {
    color: var(--atlas-muted);
    font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    font-size: 0.76rem;
    margin-top: 0.25rem;
    overflow-wrap: anywhere;
}

.risk-chip {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    gap: 0.45rem;
    padding: 0.42rem 0.65rem;
    border-radius: 999px;
    border: 1px solid currentColor;
    font-size: 0.76rem;
    font-weight: 700;
    white-space: nowrap;
}

.risk-chip::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: currentColor;
}

.tone-low { color: var(--atlas-green); }
.tone-guarded { color: light-dark(#5f8500, #8fd14f); }
.tone-moderate { color: var(--atlas-yellow); }
.tone-high { color: var(--atlas-orange); }
.tone-critical { color: var(--atlas-red); }

.atlas-section {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin: 1.05rem 0 0.5rem;
}

.atlas-section__title {
    color: var(--atlas-text);
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    margin-top: 0.18rem;
}

.atlas-section__copy {
    color: var(--atlas-muted);
    font-size: 0.8rem;
    max-width: 520px;
    text-align: right;
}

.welcome-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 1rem 0 1.1rem;
}

.welcome-card {
    min-height: 112px;
    padding: 0.9rem;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
}

.welcome-card__index {
    color: var(--atlas-cyan);
    font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    font-size: 0.72rem;
    font-weight: 700;
}

.welcome-card__title {
    color: var(--atlas-text);
    font-size: 0.96rem;
    font-weight: 680;
    margin: 0.55rem 0 0.3rem;
}

.welcome-card__copy {
    color: var(--atlas-muted);
    font-size: 0.82rem;
    line-height: 1.55;
}

[data-testid="stSidebar"] {
    background: var(--atlas-sidebar);
    border-right: 1px solid var(--atlas-border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.8rem;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: var(--atlas-text);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.1rem 0 0.9rem;
}

.sidebar-brand__mark {
    display: grid;
    place-items: center;
    width: 38px;
    height: 38px;
    border: 1px solid var(--atlas-border-strong);
    border-radius: 11px;
    background: var(--atlas-panel-hover);
    color: var(--atlas-cyan);
    font-size: 1.05rem;
    font-weight: 800;
    box-shadow: var(--atlas-shadow-soft);
}

.sidebar-brand__name {
    color: var(--atlas-text);
    font-size: 1.03rem;
    font-weight: 760;
}

.sidebar-brand__meta {
    color: var(--atlas-subtle);
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.sidebar-eyebrow {
    margin: 0.2rem 0 0.45rem;
}

.privacy-note {
    padding: 0.6rem 0.7rem;
    border: 1px solid color-mix(in srgb, var(--atlas-green) 24%, transparent);
    border-radius: 12px;
    background: color-mix(in srgb, var(--atlas-green) 7%, transparent);
    color: var(--atlas-privacy-text);
    font-size: 0.7rem;
    line-height: 1.4;
}

.privacy-note strong {
    color: var(--atlas-green) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    background: var(--atlas-control) !important;
    border-color: var(--atlas-border) !important;
    color: var(--atlas-text) !important;
    border-radius: 11px !important;
    transition: border-color 140ms ease, box-shadow 140ms ease, background 140ms ease;
}

[data-testid="stTextInput"] input:hover,
[data-testid="stTextArea"] textarea:hover,
[data-baseweb="select"] > div:hover {
    border-color: var(--atlas-border-strong) !important;
}

[data-testid="stTextArea"] textarea {
    min-height: 74px !important;
}

[data-testid="stSidebar"] hr {
    margin: 0.75rem 0 !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--atlas-cyan) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--atlas-cyan) 16%, transparent) !important;
}

button:focus-visible,
a:focus-visible,
[role="tab"]:focus-visible,
input:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible {
    outline: 2px solid var(--atlas-cyan) !important;
    outline-offset: 2px !important;
}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    min-height: 2.75rem;
    border: 1px solid var(--atlas-primary);
    border-radius: 11px;
    background: var(--atlas-primary);
    color: var(--atlas-primary-text);
    font-weight: 760;
    box-shadow: 0 10px 30px color-mix(in srgb, var(--atlas-cyan) 18%, transparent);
}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    border-color: var(--atlas-primary-hover);
    background: var(--atlas-primary-hover);
    color: var(--atlas-primary-text);
    transform: translateY(-1px);
}

.stDownloadButton > button {
    min-height: 2.65rem;
    border: 1px solid var(--atlas-border-strong);
    border-radius: 11px;
    background: var(--atlas-panel);
    color: var(--atlas-text);
    font-weight: 680;
}

[data-testid="stMetric"] {
    min-height: 78px;
    padding: 0.52rem 0.62rem;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
    box-shadow: var(--atlas-shadow-soft);
    transition: border-color 150ms ease, transform 150ms ease;
}

[data-testid="stMetric"]:hover {
    border-color: var(--atlas-border-strong);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--atlas-muted);
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.055em;
    text-transform: uppercase;
}

[data-testid="stMetricLabel"] p {
    overflow: visible;
    text-overflow: clip;
    white-space: normal;
    line-height: 1.25;
}

[data-testid="stMetricValue"] {
    color: var(--atlas-text);
    font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    font-size: 1.28rem;
    font-weight: 700;
}

.st-key-project_kpis [data-testid="stHorizontalBlock"],
.st-key-module_kpis [data-testid="stHorizontalBlock"],
.st-key-function_kpis [data-testid="stHorizontalBlock"] {
    gap: 0.55rem;
}

.st-key-project_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-module_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-function_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 0 !important;
    width: auto !important;
}

.explore-panel-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.75rem;
    min-height: 38px;
    padding: 0 0.15rem 0.45rem;
}

.explore-panel-heading__title {
    color: var(--atlas-text);
    font-size: 0.98rem;
    font-weight: 700;
}

.explore-panel-heading__copy {
    color: var(--atlas-muted);
    font-size: 0.7rem;
    text-align: right;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--atlas-border) !important;
    border-radius: var(--atlas-radius) !important;
    background: var(--atlas-panel) !important;
    box-shadow: var(--atlas-shadow-soft);
}

[data-testid="stPlotlyChart"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
    box-shadow: var(--atlas-shadow-soft);
}

[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
    box-shadow: var(--atlas-shadow-soft);
}

[data-testid="stAlert"] {
    margin-block: 0.35rem;
    border-radius: 13px;
    border-color: var(--atlas-border) !important;
    background: var(--atlas-alert) !important;
    box-shadow: var(--atlas-shadow-soft);
}

[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
    line-height: 1.4;
}

[data-testid="stExpander"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border) !important;
    border-radius: 13px !important;
    background: var(--atlas-panel) !important;
}

[data-baseweb="tab-list"],
[role="tablist"] {
    gap: 0.35rem;
    padding: 0.24rem;
    border: 1px solid var(--atlas-border);
    border-radius: 12px;
    background: color-mix(in srgb, var(--atlas-panel) 76%, transparent);
    border-bottom-color: var(--atlas-border);
}

[data-baseweb="tab"],
[role="tab"] {
    height: 2.15rem;
    padding: 0 0.9rem;
    border-radius: 9px;
    color: var(--atlas-muted);
    font-weight: 650;
}

[aria-selected="true"][data-baseweb="tab"],
[role="tab"][aria-selected="true"] {
    background: color-mix(in srgb, var(--atlas-cyan) 13%, var(--atlas-panel));
    color: var(--atlas-cyan);
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--atlas-cyan) 28%, transparent);
}

[role="tab"] .react-aria-SelectionIndicator {
    display: none;
}

[data-testid="stCode"] {
    border: 1px solid var(--atlas-border);
    border-radius: 13px;
    background: var(--atlas-code);
}

hr {
    border-color: var(--atlas-border) !important;
}

@media (max-width: 900px) {
    .block-container { padding-top: 3.25rem; }
    .project-ribbon { align-items: flex-start; flex-direction: column; }
    .atlas-section { align-items: flex-start; flex-direction: column; }
    .atlas-section__copy { text-align: left; }
    .explore-panel-heading { align-items: flex-start; flex-direction: column; gap: 0.15rem; }
    .explore-panel-heading__copy { text-align: left; }
    .welcome-grid { grid-template-columns: 1fr; }

    .st-key-project_kpis [data-testid="stHorizontalBlock"],
    .st-key-function_kpis [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .st-key-module_kpis [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }

    .st-key-project_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-module_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-function_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: none !important;
        min-width: 0 !important;
        width: auto !important;
    }
}

@media (max-width: 600px) {
    .block-container {
        padding-inline: 0.75rem;
        padding-bottom: 1.5rem;
    }

    h1 { font-size: 2rem !important; }
    .project-ribbon { gap: 0.65rem; }
    .atlas-section { margin-top: 0.9rem; gap: 0.35rem; }

    .st-key-project_kpis [data-testid="stHorizontalBlock"],
    .st-key-module_kpis [data-testid="stHorizontalBlock"],
    .st-key-function_kpis [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    [data-baseweb="tab"],
    [role="tab"] {
        padding-inline: 0.7rem;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""
