import streamlit as st
import pandas as pd
import traceback

# Content Generation
from app.content_engine.content_generator import generate_variations

# Trend Optimization
from app.content_engine.trend_based_optimizer import optimize_content

# A/B Testing
from app.ab_testing.ab_coach import run_ab_test

# Sentiment Analysis
from app.sentiment_engine.sentiment import analyze_texts
from app.sentiment_engine.sentiment_analyzer import analyze_sentiment

# Metrics Systems
from app.metrics_engine.metrics_tracker import update_google_sheet
from app.metrics_engine.metrics_hub2 import record_campaign_metrics

# Notifications
from app.notifications.slack_notifier import send_ab_test_winner, send_ab_test_full_report



# ============================================================
# UI DESIGN THEME (ADD AFTER IMPORTS)
# ============================================================
st.markdown("""
<style>

    /* ===== MAIN PAGE STYLE ===== */
    .main {
        background-color: #F8F9FC;
        padding: 0 2rem;
    }

    /* Page title */
    .block-container h1 {
        color: #374785;
        font-weight: 800;
        padding-bottom: 10px;
    }

    /* Subheaders */
    .block-container h2, .block-container h3 {
        color: #24305E;
        font-weight: 700;
        margin-top: 25px;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 10px !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4a90e2, #1c75bc);
        color: white;
        padding: 10px 22px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.03);
        background: linear-gradient(90deg, #1c75bc, #4a90e2);
    }

    /* Download Button */
    .stDownloadButton>button {
        background: #00C8A8;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 10px 18px;
        border: none;
        transition: 0.3s;
    }

    .stDownloadButton>button:hover {
        background: #00997f;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #24305E;
        padding-top: 20px;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-size: 17px;
        font-weight: 700;
    }

    /* Cards */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)



# ============================================================
# Streamlit Page Setup
# ============================================================
st.set_page_config(page_title="AI Marketing Dashboard", layout="wide")

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to:",
    [
        "Content Generation",
        "Trend Optimization",
        "Sentiment Analysis",
        "A/B Testing",
        "Metrics & Reports"
    ],
    index=0
)

st.title("🚀 AI Content Marketing Optimizer Dashboard")

# ============================================================
# Utility Helpers
# ============================================================

def df_from_variations(variations):
    rows = []
    for i, v in enumerate(variations, start=1):
        rows.append({
            "variant_id": f"V{i}",
            "text": v.get("text"),
            "quality": v.get("quality", None),
            "meta": v.get("meta", {})
        })
    return pd.DataFrame(rows)

def download_df(df, filename="data.csv"):
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        filename,
        "text/csv"
    )


# ============================================================
# PAGE — CONTENT GENERATION
# ============================================================
if page == "Content Generation":
    st.subheader("📝 Content Input + RAW Content Generation")

    with st.form("content_form"):
        topic = st.text_input("Topic", value="How AI is transforming marketing")
        audience = st.text_input("Audience", value="Marketers, Creators, Startups")
        targeted_audience = st.text_input("Targeted Audience", value="SaaS Growth Marketers")
        tone = st.selectbox("Tone", ["positive", "educational", "emotional", "humorous", "persuasive"])
        platform = st.selectbox("Platform", ["Twitter", "LinkedIn", "Instagram", "Facebook", "YouTube"])
        keywords = st.text_input("Keywords (comma separated)", value="#AI, #Marketing, #Growth")
        word_count = st.slider("Target Word Count", 20, 300, 60)
        n_variants = st.slider("How many variations?", 1, 10, 3)

        submitted = st.form_submit_button("Generate RAW Variations")

    if submitted:
        st.session_state["input_data"] = {
            "topic": topic,
            "audience": audience,
            "targeted_audience": targeted_audience,
            "tone": tone,
            "platform": platform,
            "keywords": [k.strip() for k in keywords.split(",")] if keywords else [],
            "word_count": word_count,
            "n_variants": n_variants
        }

        st.info("Generating RAW (non-optimized) content…")

        from app.content_engine.dynamic_prompt import generate_engaging_prompt

        prompt = generate_engaging_prompt(
            topic=topic,
            platform=platform,
            keywords=st.session_state["input_data"]["keywords"],
            audience=audience or targeted_audience,
            tone=tone,
            word_count=word_count
        )

        try:
            raw = generate_variations(prompt, n=n_variants)

            raw_df = pd.DataFrame([
                {"variant_id": f"RAW-{i+1}", "text": txt}
                for i, txt in enumerate(raw)
            ])

            st.session_state["raw_df"] = raw_df

            st.success("RAW content generated successfully!")
            st.dataframe(raw_df, height=400)

            download_df(raw_df, "raw_generated_variations.csv")

        except Exception:
            st.error("❌ Error generating RAW content.")
            st.code(traceback.format_exc())



# ============================================================
# PAGE — TREND OPTIMIZATION
# ============================================================
elif page == "Trend Optimization":
    st.subheader("📈 Trend Optimization")

    raw_df = st.session_state.get("raw_df", pd.DataFrame())
    if raw_df.empty:
        st.info("Generate raw content first.")
        st.stop()

    if st.button("Apply Trend Optimization"):
        optimized = []
        for _, row in raw_df.iterrows():
            result = optimize_content(row["text"])
            optimized.append({
                "variant_id": row["variant_id"],
                "text": result["optimized_text"],
                "meta": result
            })

        opt_df = pd.DataFrame(optimized)
        st.session_state["optimized_df"] = opt_df

        st.success("Trend Optimization Applied!")
        st.dataframe(opt_df, height=400)



# ============================================================
# PAGE — SENTIMENT ANALYSIS
# ============================================================
elif page == "Sentiment Analysis":
    st.subheader("💬 Sentiment Analysis")

    df = st.session_state.get("optimized_df", pd.DataFrame())

    if df.empty:
        st.info("Generate content before running sentiment.")
    else:
        st.dataframe(df, height=350)

        if st.button("Run Sentiment Analysis"):
            try:
                texts = [{"id": str(i+1), "text": t} for i, t in enumerate(df["text"].tolist())]
                results = analyze_texts(texts)

                rows = []
                for r in results:
                    rows.append({
                        "id": r.id,
                        "text": r.text,
                        "label": r.label,
                        "score": r.score,
                        "polarity": r.polarity,
                        "toxicity": r.toxicity
                    })

                sent_df = pd.DataFrame(rows)
                st.session_state["sentiment_df"] = sent_df

                st.success("Sentiment Analysis Complete.")
                st.dataframe(sent_df, height=450)
                download_df(sent_df, "sentiment_results.csv")

            except Exception:
                st.error("❌ Sentiment analysis failed.")
                st.code(traceback.format_exc())



# ============================================================
# PAGE — A/B TESTING
# ============================================================
elif page == "A/B Testing":
    st.subheader("🧪 A/B Test Simulation")

    df = st.session_state.get("optimized_df", pd.DataFrame())

    if df.empty:
        st.info("Generate content first.")
    else:
        st.dataframe(df, height=350)
        impressions = st.number_input("Impressions per Variation", 100, 50000, 1500)

        if st.button("Run A/B Test"):
            try:
                variations = [{"text": row["text"], "meta": row["meta"]} for _, row in df.iterrows()]

                res = run_ab_test(
                    campaign_name="dashboard_test",
                    topic="dashboard_topic",
                    platform="Twitter",
                    keywords=[],
                    audience="general",
                    tone="positive",
                    n_variants=len(variations),
                    impressions_per_variant=int(impressions),
                    existing_variations=variations
                )

                st.session_state["ab_test_result"] = res
                st.session_state["ab_test_winner"] = res.get("winner")
                if "summary" in res:
                    st.session_state["ab_results_df"] = pd.DataFrame(res["summary"])

                st.success("A/B Test Complete. Results saved!")

            except Exception:
                st.error("❌ A/B Test failed.")
                st.code(traceback.format_exc())

    res = st.session_state.get("ab_test_result")
    winner = st.session_state.get("ab_test_winner")

    if res and winner:
        st.markdown("### 🏆 A/B Test Winner")

        st.success(f"**Winner Variant:** {winner['variant']}")

        st.markdown(
            f"""
            **CTR:** `{winner['ctr']:.4f}`  
            **Conversion Rate:** `{winner['conv_rate']:.4f}`  
            **Impressions:** `{winner['impressions']}`  
            **Clicks:** `{winner['clicks']}`  
            """
        )

        with st.expander("📌 Winning Text"):
            st.write(winner["text"])

        if st.button("Send Winner Alert to Slack"):
            ok = send_ab_test_winner("dashboard_test", winner)
            if ok:
                st.success("🏆 Winner alert sent to Slack!")
            else:
                st.error("❌ Failed to send winner alert.")



# ============================================================
# PAGE — METRICS & REPORTS
# ============================================================
elif page == "Metrics & Reports":
    st.subheader("📊 Metrics & Analytics")

    sent_df = st.session_state.get("sentiment_df", pd.DataFrame())

    if sent_df.empty:
        st.info("Run Sentiment Analysis first to view sentiment metrics.")
    else:
        st.markdown("### 🧠 Sentiment Analysis Results")
        st.dataframe(sent_df, height=300)

    ab_df = st.session_state.get("ab_results_df", pd.DataFrame())

    st.markdown("### 🚀 A/B Test Performance Results")

    if ab_df.empty:
        st.warning("⚠️ A/B Test results not found. Run A/B Test before pushing metrics.")
    else:
        st.dataframe(ab_df, height=300)

    st.markdown("### 📤 Push Metrics")

    if st.button("Push to Google Sheets"):
        if ab_df.empty:
            st.warning("⚠️ Run A/B Test first — sentiment results cannot be pushed to Google Sheets.")
        else:
            try:
                if "impressions" in ab_df.columns:
                    ab_df = ab_df.rename(columns={"impressions": "views"})

                if "likes" not in ab_df.columns:
                    ab_df["likes"] = 0  

                if "sentiment_score" in ab_df.columns:
                    ab_df = ab_df.rename(columns={"sentiment_score": "sentiment_label"})

                if "trend_score" in ab_df.columns:
                    ab_df = ab_df.rename(columns={"trend_score": "polarity"})

                update_google_sheet("dashboard_sheet", ab_df)
                st.success("✅ Metrics successfully pushed to Google Sheets!")

            except Exception as e:
                st.error("❌ Failed to push metrics.")
                st.code(str(e))


    if st.button("Push Summary to Metrics Hub"):
        if ab_df.empty:
            st.warning("⚠️ Run A/B Test first before sending metrics to Metrics Hub.")
        else:
            try:
                for _, row in ab_df.iterrows():
                    record_campaign_metrics(
                        campaign_id="dashboard_campaign",
                        variant=row["variant"],
                        impressions=int(row["impressions"]),
                        clicks=int(row["clicks"]),
                        conversions=int(row["conversions"]),
                        sentiment_score=float(0),
                        trend_score=float(0)
                    )
                st.success("📡 All variant metrics pushed to Metrics Hub!")
            except Exception as e:
                st.error("❌ Failed to push metrics to Metrics Hub.")
                st.code(str(e))
