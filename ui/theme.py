"""Shared visual language for the PyAtlas Streamlit interface."""

APP_CSS = r"""
<style>
:root {
    --atlas-bg: #07111f;
    --atlas-bg-raised: #0a1627;
    --atlas-panel: #101e33;
    --atlas-panel-hover: #142641;
    --atlas-border: rgba(148, 163, 184, 0.16);
    --atlas-border-strong: rgba(83, 212, 255, 0.28);
    --atlas-text: #edf4ff;
    --atlas-muted: #91a4bd;
    --atlas-subtle: #60738f;
    --atlas-cyan: #53d4ff;
    --atlas-indigo: #8587ff;
    --atlas-green: #3dd6a3;
    --atlas-yellow: #f9c74f;
    --atlas-orange: #f8961e;
    --atlas-red: #f05d75;
    --atlas-radius: 16px;
    --atlas-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background: var(--atlas-bg);
    color: var(--atlas-text);
}

[data-testid="stHeader"] {
    background: rgba(7, 17, 31, 0.82);
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    backdrop-filter: blur(18px);
}

[data-testid="stToolbar"] {
    right: 1rem;
}

.block-container {
    max-width: 1480px;
    padding-top: 2.25rem;
    padding-bottom: 5rem;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] strong {
    color: var(--atlas-text);
    letter-spacing: -0.025em;
}

h1 {
    font-size: clamp(2.5rem, 5vw, 4.75rem) !important;
    line-height: 0.98 !important;
    font-weight: 760 !important;
    margin: 0.35rem 0 0.65rem !important;
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

.atlas-kicker {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: var(--atlas-cyan);
    font-size: 0.72rem;
    font-weight: 750;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.15rem;
}

.atlas-kicker::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: var(--atlas-green);
    box-shadow: 0 0 18px rgba(61, 214, 163, 0.8);
}

.atlas-lead {
    max-width: 760px;
    color: #aabbd0 !important;
    font-size: 1.08rem;
    line-height: 1.7;
    margin: 0 0 2.1rem;
}

.atlas-rule {
    height: 1px;
    background: linear-gradient(90deg, var(--atlas-border-strong), transparent 72%);
    margin: 0.2rem 0 1.75rem;
}

.project-ribbon {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 1.25rem 1.4rem;
    margin: 0.3rem 0 1rem;
    border: 1px solid var(--atlas-border-strong);
    border-radius: var(--atlas-radius);
    background: #0d1c30;
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
    font-size: 1.25rem;
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
    padding: 0.55rem 0.78rem;
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
.tone-guarded { color: #8fd14f; }
.tone-moderate { color: var(--atlas-yellow); }
.tone-high { color: var(--atlas-orange); }
.tone-critical { color: var(--atlas-red); }

.atlas-section {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin: 2.6rem 0 1rem;
}

.atlas-section__title {
    color: var(--atlas-text);
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    margin-top: 0.18rem;
}

.atlas-section__copy {
    color: var(--atlas-muted);
    font-size: 0.86rem;
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
    min-height: 132px;
    padding: 1.15rem;
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
    background: #081321;
    border-right: 1px solid var(--atlas-border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.3rem;
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
    padding: 0.25rem 0 1.55rem;
}

.sidebar-brand__mark {
    display: grid;
    place-items: center;
    width: 38px;
    height: 38px;
    border: 1px solid rgba(83, 212, 255, 0.42);
    border-radius: 11px;
    background: #11243a;
    color: var(--atlas-cyan);
    font-size: 1.05rem;
    font-weight: 800;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
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
    margin: 0.35rem 0 0.65rem;
}

.privacy-note {
    padding: 0.8rem 0.9rem;
    border: 1px solid rgba(61, 214, 163, 0.18);
    border-radius: 12px;
    background: rgba(61, 214, 163, 0.055);
    color: #9ec7bd;
    font-size: 0.74rem;
    line-height: 1.5;
}

.privacy-note strong {
    color: var(--atlas-green) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    background: #0d1b2d !important;
    border-color: var(--atlas-border) !important;
    color: var(--atlas-text) !important;
    border-radius: 11px !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--atlas-cyan) !important;
    box-shadow: 0 0 0 2px rgba(83, 212, 255, 0.12) !important;
}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    min-height: 2.75rem;
    border: 1px solid #62dcff;
    border-radius: 11px;
    background: #53d4ff;
    color: #04111c;
    font-weight: 760;
    box-shadow: 0 10px 30px rgba(83, 212, 255, 0.16);
}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    border-color: #9ae8ff;
    background: #78dfff;
    color: #04111c;
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
    min-height: 116px;
    padding: 1rem 1.05rem;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.12);
    transition: border-color 150ms ease, transform 150ms ease;
}

[data-testid="stMetric"]:hover {
    border-color: var(--atlas-border-strong);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--atlas-muted);
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.055em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: var(--atlas-text);
    font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    font-size: 1.65rem;
    font-weight: 700;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--atlas-border) !important;
    border-radius: var(--atlas-radius) !important;
    background: var(--atlas-panel) !important;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
}

[data-testid="stPlotlyChart"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
}

[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border);
    border-radius: var(--atlas-radius);
    background: var(--atlas-panel);
}

[data-testid="stAlert"] {
    border-radius: 13px;
    border-color: var(--atlas-border) !important;
    background: #0f2035 !important;
}

[data-testid="stExpander"] {
    overflow: hidden;
    border: 1px solid var(--atlas-border) !important;
    border-radius: 13px !important;
    background: var(--atlas-panel) !important;
}

[data-baseweb="tab-list"] {
    gap: 0.45rem;
    border-bottom-color: var(--atlas-border);
}

[data-baseweb="tab"] {
    height: 2.8rem;
    padding: 0 1rem;
    border-radius: 10px 10px 0 0;
    color: var(--atlas-muted);
    font-weight: 650;
}

[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(83, 212, 255, 0.08);
    color: var(--atlas-cyan);
}

[data-testid="stCode"] {
    border: 1px solid var(--atlas-border);
    border-radius: 13px;
    background: #060e19;
}

hr {
    border-color: var(--atlas-border) !important;
}

@media (max-width: 900px) {
    .block-container { padding-top: 1.5rem; }
    .project-ribbon { align-items: flex-start; flex-direction: column; }
    .atlas-section { align-items: flex-start; flex-direction: column; }
    .atlas-section__copy { text-align: left; }
    .welcome-grid { grid-template-columns: 1fr; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""
