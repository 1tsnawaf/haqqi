"""
Chat UI + live case-file card. Owned by P3.
Run (with the API running):  streamlit run ui/streamlit_app.py
"""
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Haqqi · حقّي", page_icon="\u2696\ufe0f", layout="wide")
st.title("\u2696\ufe0f Haqqi \u00b7 \u062d\u0642\u0651\u064a")
st.caption("Know your employment rights. This is legal information, not legal advice \u2014 "
           "consult a licensed lawyer for your specific case.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}

chat_col, case_col = st.columns([2, 1])

with case_col:
    st.subheader("Case file")
    st.json(st.session_state.profile or {"(empty)": "the agent fills this in as you talk"})

with chat_col:
    for m in st.session_state.messages:
        st.chat_message(m["role"]).write(m["content"])

    if prompt := st.chat_input("Describe your situation, or paste a contract clause..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            resp = requests.post(
                f"{API_URL}/chat",
                json={"message": prompt, "profile": st.session_state.profile, "language": "en"},
                timeout=60,
            ).json()
            reply = resp.get("reply", "(no reply)")
            st.session_state.profile = resp.get("profile", st.session_state.profile)
            if resp.get("citations"):
                refs = ", ".join(c["article_ref"] for c in resp["citations"])
                reply += f"\n\n_Sources: {refs}_"
        except Exception as e:
            reply = f"Could not reach the backend ({e}). Is `uvicorn app.main:app` running?"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
        st.rerun()
