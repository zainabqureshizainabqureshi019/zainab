"""Shared visual styling and page helpers."""
import streamlit as st


def apply_styles(authenticated: bool = True):
    sidebar_visibility = "" if authenticated else """
      [data-testid="stSidebar"],
      [data-testid="collapsedControl"] { display: none !important; }
    """
    st.markdown(
        f"""
        <style>
          :root {{
            --ink: #16263f;
            --muted: #718198;
            --brand: #245b91;
            --brand-dark: #14365e;
            --line: #e5eaf1;
            --surface: #ffffff;
            --canvas: #f3f6fa;
          }}

          html, body, [class*="css"] {{
            font-family: Inter, "Segoe UI", -apple-system, BlinkMacSystemFont,
              sans-serif;
            color: var(--ink);
          }}
          .stApp, [data-testid="stAppViewContainer"] {{
            background: var(--canvas);
          }}
          [data-testid="stHeader"] {{
            background: transparent;
          }}
          [data-testid="stMainBlockContainer"] {{
            max-width: 1440px;
            padding: 2rem 2.5rem 3.5rem;
          }}
          {sidebar_visibility}

          [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #12223c 0%, #172f50 100%);
            border-right: 1px solid #253b58;
          }}
          [data-testid="stSidebar"] * {{
            color: #e8eff8;
          }}
          [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: #9fb1c9 !important;
          }}
          [data-testid="stSidebar"] [data-testid="stRadio"] > label {{
            color: #91a6c1 !important;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.11em;
          }}
          [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {{
            gap: 0.25rem;
          }}
          [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {{
            padding: 0.55rem 0.7rem;
            border: 1px solid transparent;
            border-radius: 0.65rem;
            transition: background 150ms ease, border-color 150ms ease;
          }}
          [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {{
            background: #ffffff12;
            border-color: #ffffff18;
          }}
          .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 0.3rem 0 0.5rem;
          }}
          .sidebar-brand-mark, .login-brand-mark {{
            display: grid;
            place-items: center;
            width: 2.55rem;
            height: 2.55rem;
            flex: 0 0 2.55rem;
            border: 1px solid #ffffff2b;
            border-radius: 0.8rem;
            background: #ffffff16;
            color: #ffffff;
            font-size: 1.15rem;
            font-weight: 800;
          }}
          .sidebar-brand-name {{
            color: #ffffff;
            font-size: 1rem;
            font-weight: 750;
            letter-spacing: -0.02em;
          }}
          .sidebar-brand-caption {{
            margin-top: 0.13rem;
            color: #a7bad1;
            font-size: 0.61rem;
            font-weight: 700;
            letter-spacing: 0.12em;
          }}

          h1, h2, h3 {{
            color: var(--ink);
            letter-spacing: -0.035em;
          }}
          h2 {{ font-size: 1.25rem; }}
          h3 {{ font-size: 1.02rem; }}
          p, label {{ color: var(--ink); }}
          [data-testid="stCaptionContainer"] {{
            color: var(--muted);
          }}
          .page-header {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.5rem;
            overflow: hidden;
            margin: 0 0 1.75rem;
            padding: 1.7rem 2rem;
            border: 1px solid #24446a;
            border-radius: 1.05rem;
            background: linear-gradient(115deg, #142945 0%, #214d78 100%);
            box-shadow: 0 12px 30px #152b4614;
          }}
          .page-header::after {{
            position: absolute;
            top: -5rem;
            right: 12%;
            width: 15rem;
            height: 15rem;
            border: 1px solid #ffffff13;
            border-radius: 50%;
            content: "";
            pointer-events: none;
          }}
          .page-header-eyebrow {{
            margin-bottom: 0.45rem;
            color: #b7c9dc;
            font-size: 0.68rem;
            font-weight: 750;
            letter-spacing: 0.14em;
            text-transform: uppercase;
          }}
          .page-header h1 {{
            margin: 0;
            color: #ffffff !important;
            font-size: clamp(1.65rem, 3vw, 2.15rem);
            font-weight: 760;
            line-height: 1.2;
          }}
          .page-header p {{
            margin: 0.55rem 0 0;
            color: #d3e1ef;
            font-size: 0.94rem;
          }}
          .page-header-mark {{
            position: relative;
            z-index: 1;
            display: grid;
            width: 3rem;
            height: 3rem;
            flex: 0 0 3rem;
            place-items: center;
            border: 1px solid #ffffff2a;
            border-radius: 0.95rem;
            background: #ffffff12;
            color: #ffffff;
            font-size: 1.3rem;
          }}

          div[data-testid="stMetric"] {{
            min-height: 7rem;
            padding: 1.05rem 1.15rem;
            border: 1px solid var(--line);
            border-radius: 0.9rem;
            background: var(--surface);
            box-shadow: 0 3px 12px #172b4d08;
          }}
          [data-testid="stMetricLabel"] {{
            color: var(--muted);
            font-size: 0.79rem;
            font-weight: 650;
          }}
          [data-testid="stMetricValue"] {{
            color: var(--ink);
            font-size: 1.65rem;
            font-weight: 750;
          }}
          [data-testid="stDataFrame"], [data-testid="stTable"] {{
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 0.85rem;
            background: var(--surface);
          }}
          [data-testid="stTabs"] [role="tablist"] {{
            gap: 0.35rem;
            border-bottom: 1px solid var(--line);
          }}
          [data-testid="stTabs"] button[role="tab"] {{
            padding: 0.7rem 1rem;
            color: var(--muted);
            font-weight: 650;
          }}
          [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
            color: var(--brand);
          }}
          [data-testid="stTextInput"] input,
          [data-testid="stNumberInput"] input,
          [data-testid="stTextArea"] textarea,
          [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
            border-color: #d8e0ea;
            border-radius: 0.65rem;
            background: #ffffff;
          }}
          [data-testid="stTextInput"] input:focus,
          [data-testid="stNumberInput"] input:focus,
          [data-testid="stTextArea"] textarea:focus {{
            border-color: #4b83b4;
            box-shadow: 0 0 0 3px #245b9118;
          }}
          div.stButton > button,
          div.stFormSubmitButton > button,
          div[data-testid="stDownloadButton"] > button {{
            min-height: 2.65rem;
            border-radius: 0.65rem;
            font-weight: 650;
            transition: transform 120ms ease, box-shadow 120ms ease;
          }}
          [data-testid="stButton"] button[kind="primary"],
          [data-testid="stFormSubmitButton"] button[kind="primary"] {{
            border-color: var(--brand);
            background: var(--brand);
            color: #ffffff;
          }}
          div.stButton > button:hover,
          div.stFormSubmitButton > button:hover,
          div[data-testid="stDownloadButton"] > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 5px 14px #172b4d18;
          }}
          [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: var(--line);
            border-radius: 0.9rem;
          }}
          hr {{
            border-color: var(--line);
          }}

          [data-testid="stMainBlockContainer"]:has(.login-page-marker) {{
            max-width: 1180px;
            padding-top: clamp(1.5rem, 7vh, 5rem);
          }}
          .login-page-marker {{
            display: none;
          }}
          .login-hero {{
            display: flex;
            min-height: 29rem;
            flex-direction: column;
            justify-content: space-between;
            padding: clamp(1.75rem, 4vw, 3rem);
            border: 1px solid #24446a;
            border-radius: 1.2rem;
            background:
              radial-gradient(ellipse at 82% 15%, #3b76a34d 0, transparent 34%),
              linear-gradient(145deg, #12253f, #214b72);
            box-shadow: 0 18px 42px #152b461c;
          }}
          .login-brand {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 750;
            letter-spacing: 0.06em;
          }}
          .login-brand-mark {{
            width: 2.8rem;
            height: 2.8rem;
            flex-basis: 2.8rem;
            border-radius: 0.9rem;
            background: #ffffff1a;
          }}
          .login-copy {{
            margin: 3.5rem 0 2.4rem;
          }}
          .login-copy h1 {{
            max-width: 27rem;
            margin: 0;
            color: #ffffff !important;
            font-size: clamp(2.15rem, 4.5vw, 3.35rem);
            font-weight: 780;
            letter-spacing: -0.055em;
            line-height: 1.08;
          }}
          .login-copy p {{
            max-width: 26rem;
            margin: 1rem 0 0;
            color: #d2e0ee;
            font-size: 1rem;
            line-height: 1.7;
          }}
          .login-feature-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
          }}
          .login-feature {{
            padding: 0.5rem 0.75rem;
            border: 1px solid #ffffff28;
            border-radius: 2rem;
            background: #ffffff10;
            color: #edf4fa;
            font-size: 0.78rem;
            font-weight: 600;
          }}
          .login-card-title {{
            margin: 0 0 0.35rem;
            color: var(--ink);
            font-size: 1.45rem;
            font-weight: 750;
            letter-spacing: -0.035em;
          }}
          [data-testid="stVerticalBlockBorderWrapper"]:has(.login-card-title) {{
            padding: 1.1rem;
            border-color: var(--line);
            background: #ffffff;
            box-shadow: 0 12px 30px #172b4d0d;
          }}
          .login-card-subtitle {{
            margin: 0 0 1.5rem;
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.55;
          }}
          .login-footnote {{
            margin-top: 1rem;
            color: var(--muted);
            font-size: 0.79rem;
            line-height: 1.5;
            text-align: center;
          }}

          @media (max-width: 760px) {{
            [data-testid="stMainBlockContainer"] {{
              padding: 1.1rem 1rem 2rem;
            }}
            [data-testid="stMainBlockContainer"]:has(.login-page-marker) {{
              padding-top: 1rem;
            }}
            .login-hero {{
              min-height: auto;
              margin-bottom: 1rem;
              padding: 1.5rem;
            }}
            .login-copy {{
              margin: 2rem 0 1.5rem;
            }}
            .page-header {{
              padding: 1.35rem 1.25rem;
            }}
            .page-header-mark {{
              display: none;
            }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="page-header">
          <div>
            <div class="page-header-eyebrow">Workspace</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div class="page-header-mark" aria-hidden="true">&#9638;</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
