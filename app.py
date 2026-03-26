from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from finance_engine import (
    TaxInputs,
    calculate_fire_plan,
    compare_tax_regimes,
    load_pdf_text,
    parse_cas_text,
    parse_form16_text,
    portfolio_xray,
    score_money_health,
)
from mock_data_generator import generate_demo_documents


st.set_page_config(
    page_title="ET WealthPulse",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #1f2a30;
            --muted: #5e6a71;
            --paper: #f7f2e8;
            --panel: #fffdf8;
            --accent: #0b6e69;
            --accent-soft: #d9efeb;
            --highlight: #c98629;
            --border: #dccdb8;
        }
        .stApp {
            background:
                linear-gradient(135deg, #112533 0%, #172f43 35%, #1f3752 100%);
            color: #f3f5f6;
            transition: background 0.8s ease-in-out;
            min-height: 100vh;
        }
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at top right, rgba(255,255,255,0.08), transparent 35%),
                        radial-gradient(circle at bottom left, rgba(255,255,255,0.06), transparent 40%);
            pointer-events: none;
            z-index: 0;
        }
        h1, h2, h3 {
            font-family: Georgia, "Times New Roman", serif;
            color: #fff;
            text-shadow: 0 1px 6px rgba(0,0,0,0.6);
        }
        .pulse-card, .source-chip, .stDataFrame {
            backdrop-filter: blur(10px);
            background-color: rgba(17, 33, 53, 0.80) !important;
            border-color: rgba(255,255,255,0.18) !important;
            box-shadow: 0 8px 16px rgba(0,0,0,0.32);
            border-radius: 14px;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .pulse-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.45);
        }
        .pulse-card {
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: rgba(255, 253, 248, 0.88);
            box-shadow: 0 10px 28px rgba(47, 55, 60, 0.06);
        }
        .pulse-badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.2rem 0.65rem;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 0.85rem;
            margin-right: 0.35rem;
        }
        .source-chip {
            display: inline-block;
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            margin: 0.15rem 0.25rem 0 0;
            color: var(--muted);
            background: rgba(255,255,255,0.6);
            font-size: 0.82rem;
        }
        .small-note {
            color: var(--muted);
            font-size: 0.92rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1d2a 0%, #12263b 100%) !important;
            color: #f1f8ff !important;
            box-shadow: 0 0 28px rgba(0, 0, 0, 0.45);
        }
        [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #eef6ff !important;
        }
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea, [data-testid="stSidebar"] select {
            color: #eef6ff !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        [data-testid="stSidebar"] .stButton>button {
            color: #eef6ff !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        .stButton>button, .stSelectbox>div>div>div>div, .stTextInput>div>div>input {
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .stButton>button:hover, .stSelectbox>div>div>div>div:hover, .stTextInput>div>div>input:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.35);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fmt_currency(value: float | int | None) -> str:
    value = 0.0 if value is None else float(value)
    return f"Rs. {value:,.0f}"


def fmt_percent(value: float | None, scale: float = 100) -> str:
    if value is None:
        return "N/A"
    return f"{value * scale:,.2f}%"


@st.cache_data(show_spinner=False)
def get_demo_docs() -> dict[str, Any]:
    return generate_demo_documents()


def render_metric_card(title: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="pulse-card">
            <div class="small-note">{title}</div>
            <h3 style="margin:0.35rem 0 0.15rem 0;">{value}</h3>
            <div class="small-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: list[dict[str, Any]]) -> None:
    if not sources:
        return

    chips = []
    for source in sources:
        label = source.get("label", "Source")
        citation = source.get("citation", "")
        url = source.get("url", "")
        chip = f'<span class="source-chip"><a href="{url}" target="_blank">{label}</a>: {citation}</span>' if url else f'<span class="source-chip">{label}: {citation}</span>'
        chips.append(chip)
    st.markdown("".join(chips), unsafe_allow_html=True)


def render_recommendations(recommendations: list[dict[str, Any]], empty_text: str) -> None:
    if not recommendations:
        st.info(empty_text)
        return

    for recommendation in recommendations:
        st.markdown(
            f"""
            <div class="pulse-card">
                <div class="pulse-badge">Impact {fmt_currency(recommendation.get('impact', 0.0))}</div>
                <strong>{recommendation.get('title', 'Recommendation')}</strong>
                <div style="margin-top:0.45rem;">{recommendation.get('summary', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_sources(recommendation.get("source", []))


def parse_uploaded_form16(source_bytes: bytes | None, source_label: str) -> dict[str, Any]:
    if not source_bytes:
        return {"available": False}
    try:
        text = load_pdf_text(source_bytes)
        parsed = parse_form16_text(text)
        usable = parsed.get("confidence", 0.0) >= 0.33 and parsed.get("gross_salary", 0.0) > 0
        return {
            "available": True,
            "usable": usable,
            "text": text,
            "parsed": parsed,
            "source_label": source_label,
            "error": None,
        }
    except Exception as exc:
        return {
            "available": True,
            "usable": False,
            "parsed": {},
            "text": "",
            "source_label": source_label,
            "error": str(exc),
        }


def parse_uploaded_cas(source_bytes: bytes | None, source_label: str) -> dict[str, Any]:
    if not source_bytes:
        return {"available": False}
    try:
        text = load_pdf_text(source_bytes)
        parsed = parse_cas_text(text)
        holdings_exist = not parsed.get("holdings", pd.DataFrame()).empty
        usable = parsed.get("confidence", 0.0) >= 0.20 and (
            len(parsed.get("folios", [])) > 0
            or len(parsed.get("transaction_dates", [])) > 0
            or holdings_exist
        )
        return {
            "available": True,
            "usable": usable,
            "text": text,
            "parsed": parsed,
            "source_label": source_label,
            "error": None,
        }
    except Exception as exc:
        return {
            "available": True,
            "usable": False,
            "parsed": {},
            "text": "",
            "source_label": source_label,
            "error": str(exc),
        }


def empty_transactions_editor() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["date", "folio_number", "isin", "fund_name", "transaction_type", "amount", "units", "nav", "plan_type"]
    )


def empty_holdings_editor() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["fund_name", "folio_number", "isin", "plan_type", "current_nav", "units_held", "current_value", "asset_class"]
    )


def sanitize_manual_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return empty_transactions_editor()
    df = frame.copy()
    if "date" not in df.columns:
        return empty_transactions_editor()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for column in ["amount", "units", "nav"]:
        df[column] = pd.to_numeric(df.get(column, 0), errors="coerce").fillna(0.0)
    df["folio_number"] = df.get("folio_number", "").fillna("").astype(str)
    df["isin"] = df.get("isin", "").fillna("").astype(str)
    df["fund_name"] = df.get("fund_name", "").fillna("").astype(str)
    df["transaction_type"] = df.get("transaction_type", "Purchase").fillna("Purchase").astype(str)
    df["plan_type"] = df.get("plan_type", "Regular").fillna("Regular").astype(str)
    df = df.dropna(subset=["date"])
    df = df[df["amount"].abs() > 0]
    return df.reset_index(drop=True)


def sanitize_manual_holdings(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return empty_holdings_editor()
    df = frame.copy()
    for column in ["current_nav", "units_held", "current_value"]:
        df[column] = pd.to_numeric(df.get(column, 0), errors="coerce").fillna(0.0)
    for column in ["fund_name", "folio_number", "isin", "plan_type", "asset_class"]:
        df[column] = df.get(column, "").fillna("").astype(str)
    df = df[(df["fund_name"].str.strip() != "") | (df["current_value"] > 0)]
    return df.reset_index(drop=True)


def normalize_asset_mix(asset_mix: dict[str, float]) -> dict[str, float]:
    cleaned = {key: max(0.0, float(value)) for key, value in asset_mix.items()}
    total = sum(cleaned.values())
    return cleaned if total > 0 else {"Equity": 0.0, "Debt": 0.0, "Gold": 0.0, "Cash": 0.0}


def fire_chart(fire_plan: dict[str, Any]):
    projection = fire_plan["projection"].copy()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(projection["month"], projection["projected_corpus"], linewidth=2.5, color="#0b6e69", label="Projected corpus")
    ax.plot(projection["month"], projection["target_corpus"], linewidth=2.0, color="#c98629", linestyle="--", label="Target corpus")
    ax.set_ylabel("Corpus (Rs.)")
    ax.set_xlabel("Month")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    return fig


def health_chart(health: dict[str, Any]):
    frame = pd.DataFrame(health["dimensions"])
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(frame["dimension"], frame["score"], color=["#0b6e69" if score >= 70 else "#c98629" for score in frame["score"]])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    return fig


def build_follow_up_answer(question: str, context: dict[str, Any]) -> str:
    text = question.lower()
    tax = context["tax"]
    portfolio = context["portfolio"]
    fire_plan = context["fire"]
    health = context["health"]

    if "old" in text or "new" in text or "regime" in text or "tax" in text:
        return (
            f"For {tax['tax_period']}, the better option is the {tax['better_regime'].title()} regime. "
            f"Current modeled tax is {fmt_currency(tax['current_tax']['total_tax'])}, "
            f"best tax is {fmt_currency(tax['best_tax']['total_tax'])}, and Tax Alpha is {fmt_currency(tax['tax_alpha'])}."
        )
    if "xirr" in text or "return" in text:
        xirr_value = portfolio["portfolio_xirr"]
        return f"Portfolio XIRR is {fmt_percent(xirr_value)} based on dated cash flows plus current valuation." if xirr_value is not None else "I could not compute XIRR yet because the portfolio cash-flow set is incomplete."
    if "expense" in text or "direct" in text:
        drag = portfolio["expense_drag"]
        return (
            f"Estimated annual regular-vs-direct drag is between {fmt_currency(drag['total_saving_low'])} and "
            f"{fmt_currency(drag['total_saving_high'])}, with a midpoint of {fmt_currency(drag['total_saving_mid'])}."
        )
    if "retire" in text or "fire" in text or "corpus" in text:
        return (
            f"Your target corpus is {fmt_currency(fire_plan['target_corpus'])}. "
            f"Modeled monthly investing needed is {fmt_currency(fire_plan['required_total_monthly'])}, "
            f"and the extra amount beyond current plus found money is {fmt_currency(fire_plan['additional_monthly_needed'])}."
        )
    if "score" in text or "health" in text:
        weak = sorted(health["dimensions"], key=lambda row: row["score"])[:2]
        return f"Money Health Score is {health['total_score']}/100. The weakest dimensions right now are {weak[0]['dimension']} and {weak[1]['dimension']}."
    return (
        f"Headline view: Tax Alpha {fmt_currency(tax['tax_alpha'])}, portfolio XIRR {fmt_percent(portfolio['portfolio_xirr'])}, "
        f"monthly found money {fmt_currency(context['monthly_found_money'])}, and Money Health Score {health['total_score']}/100."
    )


def ensure_chat_state() -> None:
    if "qa_transcript" not in st.session_state:
        st.session_state.qa_transcript = []


inject_styles()
ensure_chat_state()

st.title("ET WealthPulse")
st.markdown(
    """
    <div class="pulse-card">
        <div class="pulse-badge">Local-only processing</div>
        <div class="pulse-badge">FY 2025-26 tax engine</div>
        <div class="pulse-badge">Document intelligence MVP</div>
        <p style="margin-top:0.85rem;">
            Upload a Form 16 and a CAMS/KFintech statement, or flip on the built-in demo, and WealthPulse will
            compare tax regimes, compute portfolio XIRR, surface expense-ratio drag, map a FIRE path, and grade
            overall money health without storing your data.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.subheader("Input Control")
    use_demo = st.toggle("Run built-in demo scenario", value=True)

    form16_upload = st.file_uploader("Upload Form 16 PDF", type=["pdf"])
    cas_upload = st.file_uploader("Upload CAMS / KFintech PDF", type=["pdf"])

    st.caption("If a PDF is unreadable, the manual entry blocks below act as a local fallback.")

    demo_docs = get_demo_docs() if use_demo else None
    demo_tax = demo_docs["tax_profile"] if demo_docs else {}
    demo_profile = demo_docs["profile"] if demo_docs else {}
    demo_transactions = pd.DataFrame(demo_docs["transactions"]) if demo_docs else empty_transactions_editor()
    demo_holdings = pd.DataFrame(demo_docs["holdings"]) if demo_docs else empty_holdings_editor()

    current_regime = st.selectbox(
        "Current tax regime assumption",
        options=["new", "old"],
        index=1 if demo_tax.get("current_regime") == "old" else 0,
        format_func=lambda value: value.title(),
    )

    with st.expander("Manual Tax Fallback", expanded=st.session_state.get("form16_parse_failed", False)):
        manual_gross_salary = st.number_input("Gross salary", min_value=0.0, value=float(demo_tax.get("gross_salary", 0.0) if use_demo else 0.0), step=50_000.0)
        manual_80c = st.number_input("Section 80C", min_value=0.0, value=float(demo_tax.get("section_80c", 0.0) if use_demo else 0.0), step=10_000.0)
        manual_80d = st.number_input("Section 80D", min_value=0.0, value=float(demo_tax.get("section_80d", 0.0) if use_demo else 0.0), step=5_000.0)
        manual_hra = st.number_input("HRA exemption", min_value=0.0, value=float(demo_tax.get("hra_exemption", 0.0) if use_demo else 0.0), step=10_000.0)
        manual_nps = st.number_input("Employer NPS / 80CCD(2)", min_value=0.0, value=float(demo_tax.get("employer_nps", 0.0) if use_demo else 0.0), step=10_000.0)

    with st.expander("Manual MF Fallback", expanded=st.session_state.get("cas_parse_failed", False)):
        holdings_editor = st.data_editor(
            demo_holdings if use_demo else empty_holdings_editor(),
            num_rows="dynamic",
            use_container_width=True,
            key="manual_holdings_editor",
        )
        transactions_editor = st.data_editor(
            demo_transactions if use_demo else empty_transactions_editor(),
            num_rows="dynamic",
            use_container_width=True,
            key="manual_transactions_editor",
        )

    with st.expander("FIRE + Health Inputs", expanded=True):
        current_age = st.number_input("Current age", min_value=21, max_value=80, value=int(demo_profile.get("current_age", 30) if use_demo else 30))
        target_retirement_age = st.number_input("Target retirement age", min_value=current_age, max_value=85, value=int(demo_profile.get("target_retirement_age", 50) if use_demo else 50))
        monthly_expenses = st.number_input("Monthly expenses", min_value=0.0, value=float(demo_profile.get("monthly_expenses", 50_000.0) if use_demo else 50_000.0), step=10_000.0)
        annual_income = st.number_input("Annual income", min_value=0.0, value=float(demo_profile.get("annual_income", 0.0) if use_demo else 0.0), step=50_000.0)
        emergency_fund = st.number_input("Emergency corpus", min_value=0.0, value=float(demo_profile.get("emergency_fund", 0.0) if use_demo else 0.0), step=25_000.0)
        life_cover = st.number_input("Life cover", min_value=0.0, value=float(demo_profile.get("life_cover", 0.0) if use_demo else 0.0), step=100_000.0)
        monthly_emi = st.number_input("Monthly EMI", min_value=0.0, value=float(demo_profile.get("monthly_emi", 0.0) if use_demo else 0.0), step=5_000.0)
        existing_monthly_investment = st.number_input(
            "Existing monthly investments",
            min_value=0.0,
            value=float(demo_profile.get("existing_monthly_investment", 0.0) if use_demo else 0.0),
            step=5_000.0,
        )
        st.caption("Asset mix can include MF, EPF, PPF, FD, gold, and liquid balances.")
        equity = st.number_input("Equity %", min_value=0.0, max_value=100.0, value=float(demo_profile.get("asset_mix", {}).get("Equity", 0.0) if use_demo else 0.0))
        debt = st.number_input("Debt %", min_value=0.0, max_value=100.0, value=float(demo_profile.get("asset_mix", {}).get("Debt", 0.0) if use_demo else 0.0))
        gold = st.number_input("Gold %", min_value=0.0, max_value=100.0, value=float(demo_profile.get("asset_mix", {}).get("Gold", 0.0) if use_demo else 0.0))
        cash = st.number_input("Cash %", min_value=0.0, max_value=100.0, value=float(demo_profile.get("asset_mix", {}).get("Cash", 0.0) if use_demo else 0.0))

    recalculate = st.button("🔄 Recalculate", help="Force a full recalculation with current inputs")


if recalculate or 'analysis_context' not in st.session_state:
    form16_bytes = demo_docs["form16_bytes"] if use_demo and demo_docs else (form16_upload.getvalue() if form16_upload else None)
    cas_bytes = demo_docs["cas_bytes"] if use_demo and demo_docs else (cas_upload.getvalue() if cas_upload else None)
    form16_source_label = "Built-in demo Form 16" if use_demo else (form16_upload.name if form16_upload else "No Form 16")
    cas_source_label = "Built-in demo CAMS statement" if use_demo else (cas_upload.name if cas_upload else "No CAMS statement")

    form16_result = parse_uploaded_form16(form16_bytes, form16_source_label)
    cas_result = parse_uploaded_cas(cas_bytes, cas_source_label)

    st.session_state["form16_parse_failed"] = form16_result.get("available", False) and not form16_result.get("usable", False)
    st.session_state["cas_parse_failed"] = cas_result.get("available", False) and not cas_result.get("usable", False)

    manual_tax_available = manual_gross_salary > 0
    manual_transactions = sanitize_manual_transactions(transactions_editor)
    manual_holdings = sanitize_manual_holdings(holdings_editor)
    manual_portfolio_available = not manual_transactions.empty or not manual_holdings.empty

    use_manual_tax = not form16_result.get("usable", False) and manual_tax_available
    use_manual_portfolio = not cas_result.get("usable", False) and manual_portfolio_available

    tax_payload = form16_result.get("parsed", {}) if form16_result.get("usable", False) else {
        "gross_salary": manual_gross_salary,
        "section_80c": manual_80c,
        "section_80d": manual_80d,
        "hra_exemption": manual_hra,
        "employer_nps": manual_nps,
    }

    portfolio_payload = cas_result.get("parsed", {}) if cas_result.get("usable", False) else {
        "folios": sorted(manual_transactions["folio_number"].dropna().astype(str).unique().tolist()) if not manual_transactions.empty else sorted(manual_holdings["folio_number"].dropna().astype(str).unique().tolist()),
        "isins": sorted(manual_transactions["isin"].dropna().astype(str).unique().tolist()) if not manual_transactions.empty else sorted(manual_holdings["isin"].dropna().astype(str).unique().tolist()),
        "transaction_dates": manual_transactions["date"].dt.date.sort_values().tolist() if not manual_transactions.empty else [],
        "transactions": manual_transactions,
        "holdings": manual_holdings,
        "statement_date": pd.Timestamp.today().normalize(),
    }

    tax_ready = tax_payload.get("gross_salary", 0.0) > 0
    portfolio_ready = not portfolio_payload.get("transactions", pd.DataFrame()).empty or not portfolio_payload.get("holdings", pd.DataFrame()).empty

    with st.chat_message("assistant"):
        st.markdown(
            """
            I can read PDFs locally, but if a document is image-only or structured differently from expected patterns,
            I will fall back to the manual entry panels in the sidebar and keep the rest of the analysis moving.
            """
        )

    if form16_result.get("available") and not form16_result.get("usable", False):
        if not manual_tax_available:
            with st.chat_message("assistant"):
                st.warning("I could not confidently extract your Form 16. Please use the Manual Tax Fallback panel in the sidebar.")
                if form16_result.get("error"):
                    st.caption(f"Parser note: {form16_result['error']}")
        else:
            with st.chat_message("assistant"):
                st.success("Form 16 parsing failed, but manual tax values are available and being used.")

    if cas_result.get("available") and not cas_result.get("usable", False):
        if not manual_portfolio_available:
            with st.chat_message("assistant"):
                st.warning("I could not confidently extract your CAMS/KFintech statement. Please use the Manual MF Fallback panel in the sidebar.")
                if cas_result.get("error"):
                    st.caption(f"Parser note: {cas_result['error']}")
        else:
            with st.chat_message("assistant"):
                st.success("CAMS/KFintech parsing failed, but manual MF portfolio values are available and being used.")

    if not tax_ready and not portfolio_ready:
        with st.chat_message("assistant"):
            st.info(
                "Start with the built-in demo or upload at least one PDF. You can also complete the sidebar fallback forms to run the engine without private files."
            )
        st.stop()


    tax_inputs = TaxInputs(
        gross_salary=float(tax_payload.get("gross_salary", annual_income)),
        section_80c=float(tax_payload.get("section_80c", 0.0)),
        section_80d=float(tax_payload.get("section_80d", 0.0)),
        hra_exemption=float(tax_payload.get("hra_exemption", 0.0)),
        employer_nps=float(tax_payload.get("employer_nps", 0.0)),
        age=int(current_age),
        current_regime=current_regime,
    )
    tax_summary = compare_tax_regimes(tax_inputs) if tax_ready else {
        "tax_period": "FY 2025-26 (1 Apr 2025 to 31 Mar 2026) / AY 2026-27",
        "better_regime": "new",
        "current_tax": {"total_tax": 0.0},
        "best_tax": {"total_tax": 0.0},
        "old_regime": {"taxable_income": 0.0, "total_tax": 0.0, "standard_deduction": 50_000.0},
        "new_regime": {"taxable_income": 0.0, "total_tax": 0.0, "standard_deduction": 75_000.0},
        "regime_switch_alpha": 0.0,
        "missed_deduction_alpha": 0.0,
        "tax_alpha": 0.0,
        "recommendations": [],
    }

    portfolio_summary = portfolio_xray(portfolio_payload) if portfolio_ready else {
        "folios": [],
        "isins": [],
        "transaction_dates": [],
        "transactions": pd.DataFrame(),
        "holdings": pd.DataFrame(),
        "portfolio_xirr": None,
        "cash_flows": pd.DataFrame(),
        "expense_drag": {"eligible_holdings": pd.DataFrame(), "total_saving_low": 0.0, "total_saving_high": 0.0, "total_saving_mid": 0.0},
        "fund_xirr": pd.DataFrame(),
        "recommendations": [],
    }

    annual_found_money = tax_summary["tax_alpha"] + portfolio_summary["expense_drag"]["total_saving_mid"]
    monthly_found_money = annual_found_money / 12
    current_corpus = float(portfolio_summary["holdings"]["current_value"].sum()) if not portfolio_summary["holdings"].empty else 0.0

    fire_plan = calculate_fire_plan(
        current_age=int(current_age),
        target_retirement_age=int(target_retirement_age),
        monthly_expenses=float(monthly_expenses),
        found_money_monthly=float(monthly_found_money),
        current_corpus=current_corpus,
        existing_monthly_investment=float(existing_monthly_investment),
    )

    health = score_money_health(
        annual_income=float(annual_income or tax_inputs.gross_salary),
        monthly_expenses=float(monthly_expenses),
        emergency_fund=float(emergency_fund),
        life_cover=float(life_cover),
        monthly_emi=float(monthly_emi),
        current_tax=float(tax_summary["current_tax"]["total_tax"]),
        best_tax=float(tax_summary["best_tax"]["total_tax"]),
        fire_plan=fire_plan,
        asset_mix=normalize_asset_mix({"Equity": equity, "Debt": debt, "Gold": gold, "Cash": cash}),
    )

    analysis_context = {
        "tax": tax_summary,
        "portfolio": portfolio_summary,
        "fire": fire_plan,
        "health": health,
        "monthly_found_money": monthly_found_money,
    }
    
    st.session_state['analysis_context'] = analysis_context

analysis_context = st.session_state.get('analysis_context', {})

page_view = st.sidebar.radio(
    "Choose View",
    [
        "Executive Summary",
        "Tax Wizard",
        "MF Portfolio X-Ray",
        "FIRE Path Planner",
        "Money Health Score",
        "Advisor Chat",
    ],
    index=0,
)

st.sidebar.markdown(f"**Active Page:** {page_view}")

with st.chat_message("user"):
    input_note = []
    if form16_result.get("usable", False):
        input_note.append(f"Form 16 from {form16_result['source_label']}")
    elif use_manual_tax:
        input_note.append("manual tax fallback")
    if cas_result.get("usable", False):
        input_note.append(f"CAMS/KFintech statement from {cas_result['source_label']}")
    elif use_manual_portfolio:
        input_note.append("manual portfolio fallback")
    st.markdown("Inputs used: " + ", ".join(input_note or ["partial manual inputs"]))

if page_view == "Executive Summary":
    with st.chat_message("assistant"):
        st.subheader("Executive Summary")
        top_a, top_b, top_c, top_d = st.columns(4)
        with top_a:
            render_metric_card("Tax Alpha", fmt_currency(tax_summary["tax_alpha"] if tax_summary else 0.0), "Switch or deduction opportunity")
        with top_b:
            render_metric_card("Portfolio XIRR", fmt_percent(portfolio_summary["portfolio_xirr"]), "Money-weighted annualized return")
        with top_c:
            render_metric_card("Found Money / Month", fmt_currency(monthly_found_money), "Tax and TER savings routed to investing")
        with top_d:
            render_metric_card("Money Health Score", f"{health['total_score']}/100", "Across 6 planning dimensions")
    st.markdown("---")

    st.info("Use the sidebar to switch between pages for detailed analysis sections.")
    st.write("### Switch to Tax Wizard, MF Portfolio X-Ray, FIRE Path Planner or Money Health Score to dive deeper.")
    st.stop()

if page_view == "Tax Wizard":
    with st.chat_message("assistant"):
        st.subheader("Tax Wizard Engine")
        
        if not tax_ready:
            st.info("Upload a Form 16 or complete the Manual Tax Fallback panel to activate the tax wizard.")
        else:
            st.caption("Using FY 2025-26 salary-tax rules, meaning 1 April 2025 to 31 March 2026, mapped to AY 2026-27.")
            tax_table = pd.DataFrame(
                [
                    {
                        "Regime": "Old",
                        "Taxable Income": tax_summary["old_regime"]["taxable_income"],
                        "Total Tax": tax_summary["old_regime"]["total_tax"],
                        "Standard Deduction": tax_summary["old_regime"]["standard_deduction"],
                    },
                    {
                        "Regime": "New",
                        "Taxable Income": tax_summary["new_regime"]["taxable_income"],
                        "Total Tax": tax_summary["new_regime"]["total_tax"],
                        "Standard Deduction": tax_summary["new_regime"]["standard_deduction"],
                    },
                ]
            )
            st.dataframe(tax_table.style.format({"Taxable Income": "Rs. {:,.0f}", "Total Tax": "Rs. {:,.0f}", "Standard Deduction": "Rs. {:,.0f}"}), use_container_width=True)
            st.markdown(
                f"""
                <div class="pulse-card">
                    <strong>Recommendation</strong><br/>
                    Best modeled regime: <strong>{tax_summary['better_regime'].title()}</strong><br/>
                    Current modeled tax: <strong>{fmt_currency(tax_summary['current_tax']['total_tax'])}</strong><br/>
                    Best modeled tax: <strong>{fmt_currency(tax_summary['best_tax']['total_tax'])}</strong><br/>
                    Regime switch alpha: <strong>{fmt_currency(tax_summary['regime_switch_alpha'])}</strong><br/>
                    Missed deduction alpha: <strong>{fmt_currency(tax_summary['missed_deduction_alpha'])}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_recommendations(tax_summary["recommendations"], "No immediate tax opportunity surfaced beyond current assumptions.")
    st.stop()

if page_view == "MF Portfolio X-Ray":
    with st.chat_message("assistant"):
        st.subheader("MF Portfolio X-Ray")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            render_metric_card("Folios Parsed", str(len(portfolio_summary["folios"])), "Across uploaded or manual CAS data")
        with col_b:
            render_metric_card("ISINs Parsed", str(len(portfolio_summary["isins"])), "Useful for scheme matching and audit trail")
        with col_c:
            render_metric_card("Expense Drag Mid", fmt_currency(portfolio_summary["expense_drag"]["total_saving_mid"]), "Annual TER leakage estimate")
        with col_d:
            render_metric_card("Current MF Corpus", fmt_currency(current_corpus), "Based on current values")

        if portfolio_summary["holdings"].empty:
            st.info("Portfolio X-Ray needs parsed holdings or manual portfolio rows.")
        else:
            st.dataframe(portfolio_summary["holdings"][['fund_name', 'folio_number', 'isin', 'plan_type', 'current_value']].style.format({'current_value': 'Rs. {:,.0f}'}), use_container_width=True)
            if not portfolio_summary["fund_xirr"].empty:
                fund_xirr_display = portfolio_summary["fund_xirr"].copy()
                fund_xirr_display["xirr"] = fund_xirr_display["xirr"].apply(lambda v: fmt_percent(v) if pd.notna(v) else "N/A")
                st.dataframe(fund_xirr_display, use_container_width=True)
            eligible_drag = portfolio_summary["expense_drag"]["eligible_holdings"]
            if not eligible_drag.empty:
                st.dataframe(eligible_drag[["fund_name", "direct_equivalent", "current_value", "annual_saving_low", "annual_saving_high"]].style.format({"current_value": "Rs. {:,.0f}", "annual_saving_low": "Rs. {:,.0f}", "annual_saving_high": "Rs. {:,.0f}"}), use_container_width=True)
        render_recommendations(portfolio_summary["recommendations"], "No direct-plan savings or XIRR insight surfaced.")
    st.stop()

if page_view == "FIRE Path Planner":
    with st.chat_message("assistant"):
        st.subheader("FIRE Path Planner")
        fire_a, fire_b, fire_c, fire_d = st.columns(4)
        with fire_a:
            render_metric_card("Target Corpus", fmt_currency(fire_plan["target_corpus"]), "4% withdrawal rule")
        with fire_b:
            render_metric_card("Required Monthly", fmt_currency(fire_plan["required_total_monthly"]), "Total SIP needed")
        with fire_c:
            render_metric_card("Additional Needed", fmt_currency(fire_plan["additional_monthly_needed"]), "Beyond existing + found money")
        with fire_d:
            render_metric_card("Found Money/month", fmt_currency(fire_plan["found_money_monthly"]), "From tax + TER savings")
        st.pyplot(fire_chart(fire_plan), clear_figure=True)
    st.stop()

if page_view == "Money Health Score":
    with st.chat_message("assistant"):
        st.subheader("Money Health Score")
        st.write(f"Overall money health: {health['total_score']}/100")
        for item in health['dimensions']:
            st.write(f"- {item['dimension']}: {item['score']}/100 ({item['summary']})")
        render_recommendations(health['recommendations'], "No immediate money health improvement alerts.")
    st.stop()

# If page_view is Advisor Chat, continue below this point.
    with top_a:
        render_metric_card("Tax Alpha", fmt_currency(tax_summary["tax_alpha"] if tax_summary else 0.0), "Switch or deduction opportunity")
    with top_b:
        render_metric_card("Portfolio XIRR", fmt_percent(portfolio_summary["portfolio_xirr"]), "Money-weighted annualized return")
    with top_c:
        render_metric_card("Found Money / Month", fmt_currency(monthly_found_money), "Tax and TER savings routed to investing")
    with top_d:
        render_metric_card("Money Health Score", f"{health['total_score']}/100", "Across 6 planning dimensions")

with st.chat_message("assistant"):
    st.subheader("Tax Wizard Engine")
    if not tax_ready:
        st.info("Upload a Form 16 or complete the Manual Tax Fallback panel to activate the tax wizard.")
    else:
        st.caption("Using FY 2025-26 salary-tax rules, meaning 1 April 2025 to 31 March 2026, mapped to AY 2026-27.")
        tax_table = pd.DataFrame(
            [
                {
                    "Regime": "Old",
                    "Taxable Income": tax_summary["old_regime"]["taxable_income"],
                    "Total Tax": tax_summary["old_regime"]["total_tax"],
                    "Standard Deduction": tax_summary["old_regime"]["standard_deduction"],
                },
                {
                    "Regime": "New",
                    "Taxable Income": tax_summary["new_regime"]["taxable_income"],
                    "Total Tax": tax_summary["new_regime"]["total_tax"],
                    "Standard Deduction": tax_summary["new_regime"]["standard_deduction"],
                },
            ]
        )
        st.dataframe(tax_table.style.format({"Taxable Income": "Rs. {:,.0f}", "Total Tax": "Rs. {:,.0f}", "Standard Deduction": "Rs. {:,.0f}"}), use_container_width=True)
        st.markdown(
            f"""
            <div class="pulse-card">
                <strong>Recommendation</strong><br/>
                Best modeled regime: <strong>{tax_summary['better_regime'].title()}</strong><br/>
                Current modeled tax: <strong>{fmt_currency(tax_summary['current_tax']['total_tax'])}</strong><br/>
                Best modeled tax: <strong>{fmt_currency(tax_summary['best_tax']['total_tax'])}</strong><br/>
                Regime switch alpha: <strong>{fmt_currency(tax_summary['regime_switch_alpha'])}</strong><br/>
                Missed deduction alpha: <strong>{fmt_currency(tax_summary['missed_deduction_alpha'])}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_recommendations(tax_summary["recommendations"], "No immediate tax opportunity surfaced beyond the current modeling assumptions.")

with st.chat_message("assistant"):
    st.subheader("MF Portfolio X-Ray")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        render_metric_card("Folios Parsed", str(len(portfolio_summary["folios"])), "Across uploaded or manual CAS data")
    with col_b:
        render_metric_card("ISINs Parsed", str(len(portfolio_summary["isins"])), "Useful for scheme matching and audit trail")
    with col_c:
        render_metric_card("Expense Drag Midpoint", fmt_currency(portfolio_summary["expense_drag"]["total_saving_mid"]), "Annual TER leakage estimate")
    with col_d:
        render_metric_card("Current MF Corpus", fmt_currency(current_corpus), "Based on current values in the statement")

    if portfolio_summary["holdings"].empty:
        st.info("Portfolio X-Ray needs either parsed holdings or manual portfolio rows.")
    else:
        st.dataframe(
            portfolio_summary["holdings"][["fund_name", "folio_number", "isin", "plan_type", "current_value"]].style.format({"current_value": "Rs. {:,.0f}"}),
            use_container_width=True,
        )
        if not portfolio_summary["fund_xirr"].empty:
            fund_xirr_display = portfolio_summary["fund_xirr"].copy()
            fund_xirr_display["xirr"] = fund_xirr_display["xirr"].apply(lambda value: fmt_percent(value) if pd.notna(value) else "N/A")
            fund_xirr_display["current_value"] = fund_xirr_display["current_value"].apply(fmt_currency)
            st.dataframe(fund_xirr_display, use_container_width=True)
        eligible_drag = portfolio_summary["expense_drag"]["eligible_holdings"]
        if not eligible_drag.empty:
            st.dataframe(
                eligible_drag[["fund_name", "direct_equivalent", "current_value", "annual_saving_low", "annual_saving_high"]].style.format(
                    {
                        "current_value": "Rs. {:,.0f}",
                        "annual_saving_low": "Rs. {:,.0f}",
                        "annual_saving_high": "Rs. {:,.0f}",
                    }
                ),
                use_container_width=True,
            )
    render_recommendations(portfolio_summary["recommendations"], "No direct-plan savings or XIRR insight could be surfaced from the current portfolio payload.")

with st.chat_message("assistant"):
    st.subheader("FIRE Path Planner")
    fire_a, fire_b, fire_c, fire_d = st.columns(4)
    with fire_a:
        render_metric_card("Target Corpus", fmt_currency(fire_plan["target_corpus"]), "4% withdrawal rule with inflation-adjusted expenses")
    with fire_b:
        render_metric_card("Required Monthly Invest", fmt_currency(fire_plan["required_total_monthly"]), "Modeled total SIP needed")
    with fire_c:
        render_metric_card("Additional SIP Needed", fmt_currency(fire_plan["additional_monthly_needed"]), "Beyond current and found money")
    with fire_d:
        render_metric_card("Found Money Routed", fmt_currency(fire_plan["found_money_monthly"]), "Every month toward retirement")
    st.pyplot(fire_chart(fire_plan), clear_figure=True)
    with st.expander("Month-by-month investment roadmap", expanded=False):
        roadmap = fire_plan["projection"].copy()
        roadmap["month"] = roadmap["month"].dt.strftime("%b %Y")
        st.dataframe(
            roadmap[["month", "age", "monthly_investment", "found_money_monthly", "additional_monthly_needed", "projected_corpus"]].style.format(
                {
                    "age": "{:.2f}",
                    "monthly_investment": "Rs. {:,.0f}",
                    "found_money_monthly": "Rs. {:,.0f}",
                    "additional_monthly_needed": "Rs. {:,.0f}",
                    "projected_corpus": "Rs. {:,.0f}",
                }
            ),
            use_container_width=True,
            height=320,
        )
    render_recommendations(fire_plan["recommendations"], "No FIRE recommendations yet.")

with st.chat_message("assistant"):
    st.subheader("Money Health Score")
    score_left, score_right = st.columns([1, 2])
    with score_left:
        render_metric_card("Overall Score", f"{health['total_score']}/100", "Average of 6 planning dimensions")
    with score_right:
        st.pyplot(health_chart(health), clear_figure=True)
    dimensions_df = pd.DataFrame(health["dimensions"])
    st.dataframe(dimensions_df[["dimension", "score", "summary"]], use_container_width=True)
    render_recommendations(health["recommendations"], "Money Health Score is strong across all six tracked dimensions.")

with st.chat_message("assistant"):
    st.subheader("Source of Truth")
    st.markdown(
        """
        Every recommendation above cites either a tax-law source or a planning heuristic. Tax recommendations are grounded in
        Section 115BAC, Section 87A, Section 80C, Section 80D, and Section 10(13A) read with Rule 2A. Planning scores use
        explicit heuristics for emergency reserves, life cover, debt load, diversification, and FIRE modeling assumptions.
        """
    )

follow_up = st.chat_input("Ask a follow-up about tax alpha, XIRR, direct plans, FIRE, or your score")
if follow_up:
    st.session_state.qa_transcript.append({"role": "user", "content": follow_up})
    st.session_state.qa_transcript.append({"role": "assistant", "content": build_follow_up_answer(follow_up, analysis_context)})

for message in st.session_state.qa_transcript:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
