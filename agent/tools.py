import yfinance as yf
import json
from duckduckgo_search import DDGS
from langchain_core.tools import tool        # ← new import path
from agent.retriever import vector_search


@tool
def search_financial_docs(query: str) -> str:
    """
    Search uploaded 10-K, 10-Q, and annual report PDFs for relevant information.
    Use this for: revenue figures, risk factors, business segments, management
    commentary, guidance, and any qualitative information from filings.
    Input: a natural language question or keyword phrase.
    """
    results = vector_search(query, n_results=3)
    if not results:
        return "No relevant documents found in the knowledge base."

    formatted = []
    for r in results:
        company  = r["metadata"].get("company", "unknown")
        doc_type = r["metadata"].get("type", "document")
        source   = r["metadata"].get("source", "unknown")
        formatted.append(f"[{company} | {doc_type} | {source}]\n{r['text']}")

    return "\n\n---\n\n".join(formatted)


@tool
def get_financial_statements(ticker: str) -> str:
    """
    Fetch real-time financial metrics from Yahoo Finance.
    Returns: market cap, P/E ratio, revenue, margins, debt, analyst targets.
    Use this for all quantitative financial analysis.
    Input: stock ticker symbol — e.g. AAPL, TSLA, AMZN, MSFT, NVDA
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        metrics = {
            "Company"              : info.get("longName", ticker),
            "Sector"               : info.get("sector", "N/A"),
            "Industry"             : info.get("industry", "N/A"),
            "Market Cap ($B)"      : round(info.get("marketCap", 0) / 1e9, 2) if info.get("marketCap") else "N/A",
            "PE Ratio (TTM)"       : info.get("trailingPE", "N/A"),
            "Forward PE"           : info.get("forwardPE", "N/A"),
            "Revenue TTM ($B)"     : round(info.get("totalRevenue", 0) / 1e9, 2) if info.get("totalRevenue") else "N/A",
            "Gross Margin"         : f"{round(info.get('grossMargins', 0) * 100, 2)}%" if info.get("grossMargins") else "N/A",
            "Profit Margin"        : f"{round(info.get('profitMargins', 0) * 100, 2)}%" if info.get("profitMargins") else "N/A",
            "EPS (TTM)"            : info.get("trailingEps", "N/A"),
            "Debt to Equity"       : info.get("debtToEquity", "N/A"),
            "Current Ratio"        : info.get("currentRatio", "N/A"),
            "Free Cash Flow ($B)"  : round(info.get("freeCashflow", 0) / 1e9, 2) if info.get("freeCashflow") else "N/A",
            "52W High"             : info.get("fiftyTwoWeekHigh", "N/A"),
            "52W Low"              : info.get("fiftyTwoWeekLow", "N/A"),
            "Analyst Target ($)"   : info.get("targetMeanPrice", "N/A"),
            "Recommendation"       : info.get("recommendationKey", "N/A"),
            "Number of Analysts"   : info.get("numberOfAnalystOpinions", "N/A"),
        }
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"


@tool
def search_financial_news(query: str) -> str:
    """
    Search for recent financial news, earnings reactions, and market sentiment.
    Use this for: recent events, acquisitions, regulatory issues, analyst upgrades,
    product launches, and overall market sentiment about a company.
    Input: company name or topic — e.g. 'Tesla earnings 2025', 'Apple AI strategy'
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=6))

        if not results:
            return "No recent news found."

        formatted = []
        for r in results:
            formatted.append(
                f"📰 {r['title']}\n"
                f"   Source: {r.get('source', 'N/A')} | Date: {r.get('date', 'N/A')}\n"
                f"   {r.get('body', '')}"
            )
        return "\n\n".join(formatted)
    except Exception as e:
        return f"News search error: {str(e)}"


@tool
def calculate_risk_score(ticker: str) -> str:
    """
    Calculate a quantitative risk score (0-100) based on volatility, debt,
    valuation, and profitability metrics.
    Use this when analyzing investment risk or comparing risk profiles.
    Input: stock ticker — e.g. AAPL, TSLA, AMZN, MSFT, NVDA
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        risk_score = 40
        flags = []

        # Debt risk
        de = info.get("debtToEquity") or 0
        if de > 200:
            risk_score += 20
            flags.append(f"⚠️  Very high D/E ratio: {de:.1f}")
        elif de > 100:
            risk_score += 10
            flags.append(f"⚠️  Elevated D/E ratio: {de:.1f}")

        # Volatility
        beta = info.get("beta") or 1
        if beta > 2:
            risk_score += 15
            flags.append(f"⚠️  High beta (very volatile): {beta:.2f}")
        elif beta > 1.5:
            risk_score += 8
            flags.append(f"📊 Above-average beta: {beta:.2f}")

        # Valuation risk
        pe = info.get("trailingPE") or 20
        if pe > 80:
            risk_score += 12
            flags.append(f"⚠️  Very high P/E (overvalued?): {pe:.1f}")
        elif pe > 50:
            risk_score += 6
            flags.append(f"📊 High P/E ratio: {pe:.1f}")

        # Profitability
        margin = info.get("profitMargins") or 0
        if margin < 0:
            risk_score += 15
            flags.append(f"🔴 Negative profit margin: {margin:.1%}")
        elif margin < 0.05:
            risk_score += 7
            flags.append(f"📊 Very thin profit margin: {margin:.1%}")

        risk_score = min(risk_score, 100)
        label = "🟢 LOW" if risk_score < 40 else "🟡 MEDIUM" if risk_score < 65 else "🔴 HIGH"

        result  = f"Risk Score: {risk_score}/100  [{label} RISK]\n\n"
        result += "Risk Flags:\n"
        result += "\n".join(flags) if flags else "✅ No major risk flags detected."
        return result
    except Exception as e:
        return f"Risk calculation error: {str(e)}"


@tool
def detect_price_trends(ticker: str) -> str:
    """
    Analyze 6-month price history to detect momentum, moving average crossovers,
    support/resistance levels, and overall trend direction.
    Use this for technical trend analysis and price momentum signals.
    Input: stock ticker — e.g. AAPL, TSLA, AMZN, MSFT, NVDA
    """
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="6mo")

        if hist.empty:
            return f"No price history found for {ticker}"

        close         = hist["Close"]
        current       = round(close.iloc[-1], 2)
        six_month_ago = round(close.iloc[0], 2)
        pct_change    = round(((current - six_month_ago) / six_month_ago) * 100, 2)

        ma20 = round(close.rolling(20).mean().iloc[-1], 2)
        ma50 = round(close.rolling(50).mean().iloc[-1], 2)

        trend    = "BULLISH 📈" if ma20 > ma50 else "BEARISH 📉"
        momentum = "POSITIVE ✅" if pct_change > 0 else "NEGATIVE ❌"

        high_6m = round(close.max(), 2)
        low_6m  = round(close.min(), 2)

        return (
            f"Ticker        : {ticker.upper()}\n"
            f"Current Price : ${current}\n"
            f"6-Month Change: {pct_change}%\n"
            f"6-Month High  : ${high_6m}\n"
            f"6-Month Low   : ${low_6m}\n"
            f"MA20          : ${ma20}  |  MA50: ${ma50}\n"
            f"Trend Signal  : {trend}\n"
            f"Momentum      : {momentum}"
        )
    except Exception as e:
        return f"Trend analysis error: {str(e)}"