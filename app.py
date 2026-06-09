import streamlit as st
import os
import tempfile
from agent.core import build_agent
from agent.ingestion import ingest_pdf
from agent.report import generate_investment_report

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Research Agent",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Financial Research Agent")
st.caption("Agentic RAG • ReAct Loop • Multi-Source Analysis")

# ── Session State ──────────────────────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Section 1: Upload Documents
    st.header("📂 Upload Financial Documents")
    company_name = st.text_input("Company Name", placeholder="e.g., Apple, TCS")
    doc_type = st.selectbox("Document Type", [
        "Annual Report", "Earnings Call Transcript",
        "10-K Filing", "10-Q Filing", "Investor Presentation"
    ])
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file and company_name:
        if st.button("📥 Ingest Document"):
            with st.spinner("Parsing and embedding document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                n_chunks = ingest_pdf(tmp_path, doc_type, company_name)
                os.unlink(tmp_path)
                st.success(f"✅ Ingested {n_chunks} chunks from {uploaded_file.name}")

    st.divider()

    # Section 2: Quick Research
    st.header("🎯 Quick Research")
    quick_ticker = st.text_input("Ticker Symbol", placeholder="AAPL / TCS.NS / TSLA")
    if st.button("🔍 Full Research Report") and quick_ticker:
        st.session_state.quick_query = (
            f"Generate a complete investment research report for {quick_ticker}. "
            f"Include financial health, risk score, price trends, recent news, "
            f"earnings summary, and investment verdict."
        )

    st.divider()

    # Section 3: Clear History
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.agent = build_agent()
        st.rerun()

# ── Display Chat History ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Handle Quick Query ─────────────────────────────────────────────────────────
if "quick_query" in st.session_state:
    query = st.session_state.pop("quick_query")
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Agent reasoning..."):
            try:
                result = st.session_state.agent.invoke({"input": query})
                raw_output = result["output"]

                if "intermediate_steps" in result and result["intermediate_steps"]:
                    with st.expander("🔍 View Agent Reasoning Chain (ReAct Loop)"):
                        for i, (action, observation) in enumerate(result["intermediate_steps"]):
                            st.markdown(f"**Step {i+1}: {action.tool}**")
                            st.code(f"Tool: {action.tool}\nInput: {action.tool_input}", language="yaml")
                            st.info(str(observation)[:500])

                ticker_guess = quick_ticker if quick_ticker else query.split()[0]
                report = generate_investment_report(raw_output, ticker_guess)
                st.markdown(report)
                st.session_state.messages.append({"role": "assistant", "content": report})
            except Exception as e:
                st.error(f"Agent error: {str(e)}")

# ── Main Chat Input ────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything: 'Analyze AAPL risk' or 'Summarize Tesla earnings'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent thinking..."):
            try:
                result = st.session_state.agent.invoke({"input": prompt})
                raw_output = result["output"]

                if "intermediate_steps" in result and result["intermediate_steps"]:
                    with st.expander("🔍 ReAct Reasoning Steps"):
                        for i, (action, observation) in enumerate(result["intermediate_steps"]):
                            st.markdown(f"**Step {i+1}: {action.tool}**")
                            st.code(str(action.tool_input))
                            st.success(str(observation)[:300] + "...")

                st.markdown(raw_output)
                st.session_state.messages.append({"role": "assistant", "content": raw_output})
            except Exception as e:
                st.error(f"Error: {str(e)}")