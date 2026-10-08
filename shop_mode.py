"""Shopkeeper mode: Khata Guru."""
import datetime as dt
import pandas as pd
import streamlit as st
import core


def render():
    st.title("📒 Khata Guru")
    st.caption("Speak your udhaar in Hindi or English. Runs on this laptop: Whisper + Qwen via Ollama. No cloud, no API keys.")
    con = core.get_db()

    with st.sidebar:
        st.header("Settings")
        lang_label = st.selectbox("Language you speak", ["Hindi / Hinglish", "English", "Auto-detect"])
        lang = {"Hindi / Hinglish": "hi", "English": "en", "Auto-detect": None}[lang_label]
        out_lang = st.selectbox("Read-back and advice language", ["English", "Hindi"])
        st.divider()
        st.subheader("System check")
        for name, ok in core.health().items():
            st.write(("✅ " if ok else "❌ ") + name)
        st.divider()
        if st.button("Load sample week of data"):
            now = dt.datetime.now()
            sample = [
                (6, "Ramesh", "credit_given", "rice 5 kg", 320), (5, "Lakshmi", "credit_given", "oil 1 L", 150),
                (4, "Ramesh", "credit_given", "sugar 2 kg", 90), (3, "Suresh", "credit_given", "dal, atta", 410),
                (2, "Suresh", "payment_received", "", 200), (1, "Walk-in", "cash_sale", "biscuits", 20),
                (1, "Lakshmi", "credit_given", "soap", 45),
            ]
            for days, c, k, i, a in sample:
                core.save_entries(con, [dict(customer=c, kind=k, item=i, amount=a)], when=now - dt.timedelta(days=days))
            st.success("Sample data added")
        with st.expander("Reset ledger (before the real demo)"):
            if st.checkbox("Yes, delete every entry") and st.button("Delete all"):
                core.clear_ledger(con)
                st.success("Ledger is empty")

    tab_add, tab_ledger, tab_advice = st.tabs(["🎙️ Add entries", "📒 Ledger & dues", "💡 Weekly advice"])
    hi = out_lang == "Hindi"

    with tab_add:
        st.write("**Step 1.** Record or type. **Step 2.** Check what it understood. **Step 3.** Save.")
        audio = st.audio_input("Tap to record, speak, tap to stop")
        typed = st.text_area("...or type it (backup if the mic fails)",
                             placeholder="Ramesh ne 2 kilo sugar udhaar liya 90 rupees, Suresh ne 200 wapas diye")
        if st.button("Process", type="primary"):
            if not audio and not typed.strip():
                st.warning("Record something or type a sentence first.")
            else:
                try:
                    with st.spinner("Listening and understanding..."):
                        text = core.transcribe(audio.getvalue(), lang) if audio else typed.strip()
                        st.session_state["text"] = text
                        st.session_state["entries"] = core.extract_entries(text) if text else []
                except Exception as e:
                    st.error(f"Something went wrong: {e}. Check the System check in the sidebar.")

        if "text" in st.session_state:
            st.markdown("**I heard:** " + (st.session_state["text"] or "_nothing_"))
            entries = st.session_state.get("entries", [])
            if entries:
                st.markdown("**Is this right?**")
                for e in entries:
                    st.info(core.describe(e, "hi" if hi else "en"))
                st.caption("Wrong name or amount? Fix it in the table below, then save.")
                edited = st.data_editor(
                    pd.DataFrame(entries), num_rows="dynamic", width="stretch",
                    column_config={"kind": st.column_config.SelectboxColumn("kind", options=core.KINDS)},
                )
                c1, c2 = st.columns(2)
                if c1.button("✅ Yes, save to ledger"):
                    n = core.save_entries(con, core.clean_entries(edited.to_dict("records")))
                    st.success(f"Saved {n} entries")
                    del st.session_state["text"], st.session_state["entries"]
                if c2.button("❌ No, discard"):
                    del st.session_state["text"], st.session_state["entries"]
                    st.rerun()
            elif st.session_state["text"]:
                st.warning("No entries found. Try again, speak a little slower, or type it.")

    with tab_ledger:
        df = core.load_ledger(con)
        st.subheader("Who owes you")
        bal = core.balances(df)
        st.dataframe(bal.rename(columns={"customer": "Customer", "owes": "Owes (₹)"}), width="stretch", hide_index=True)
        st.metric("Total outstanding (₹)", f"{bal['owes'].sum():,.0f}" if not bal.empty else "0")
        st.subheader("All entries")
        st.dataframe(df.drop(columns=["id"]) if not df.empty else df, width="stretch", hide_index=True)

    with tab_advice:
        st.write("Numbers are calculated by the app. The AI only turns them into advice.")
        df = core.load_ledger(con)
        if df.empty:
            st.info("Add some entries first (or load the sample week from the sidebar).")
        else:
            facts = core.weekly_facts(df)
            for line in core.plain_summary(facts):
                st.write("• " + line)
            if st.button("Get AI advice", type="primary"):
                with st.spinner("Thinking..."):
                    try:
                        st.markdown(core.weekly_advice(facts, out_lang))
                    except Exception as e:
                        st.error(f"Could not reach the model ({e}). The summary above still works.")
