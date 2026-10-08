"""Student mode: SpendWise on local SQLite (no Flask, no MySQL, no login)."""
import sqlite3
import datetime as dt
import pandas as pd
import streamlit as st

DB = "spendwise.db"
CATS = {"Food": "🍔", "Travel": "🚌", "Education": "📚", "Shopping": "🛍️", "Entertainment": "🎮", "Other": "📦"}
PAGES = ["🏠 Dashboard", "💳 Expenses", "📊 Analytics", "🎯 Savings Goals"]


def rs(x):
    return f"₹{float(x or 0):,.0f}"


def db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, amount REAL NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL, type TEXT NOT NULL, date TEXT NOT NULL, payment TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, target REAL NOT NULL, saved REAL NOT NULL DEFAULT 0)")
    con.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value REAL)")
    return con


def add_expense(con, amount, desc, cat, typ, day, pay):
    con.execute("INSERT INTO expenses(amount,description,category,type,date,payment) VALUES (?,?,?,?,?,?)",
                (float(amount), desc, cat, typ, str(day), pay))
    con.commit()


def render():
    con = db()
    st.title("🎓 SpendWise")
    st.caption("Student money tracker. Everything is saved on this device only.")

    with st.sidebar:
        page = st.radio("Go to", PAGES, label_visibility="collapsed")
        with st.expander("➕ Add expense"):
            with st.form("add_exp", clear_on_submit=True):
                amount = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0)
                desc = st.text_input("Description", placeholder="College lunch")
                cat = st.selectbox("Category", list(CATS), format_func=lambda c: f"{CATS[c]} {c}")
                typ = st.selectbox("Type", ["need", "want"])
                day = st.date_input("Date", value=dt.date.today())
                pay = st.selectbox("Payment", ["UPI", "Cash", "Card"])
                if st.form_submit_button("Save expense"):
                    if desc.strip():
                        add_expense(con, amount, desc.strip(), cat, typ, day, pay)
                        st.success("Saved")
                    else:
                        st.warning("Add a description.")
        if st.button("Load sample data"):
            t = dt.date.today()
            for d, a, ds, c, ty in [(0, 120, "College lunch", "Food", "need"), (1, 40, "Bus pass top-up", "Travel", "need"),
                                    (2, 450, "Notebooks and pens", "Education", "need"), (3, 299, "Movie night", "Entertainment", "want"),
                                    (4, 800, "New sneakers", "Shopping", "want"), (5, 90, "Chai and snacks", "Food", "want")]:
                add_expense(con, a, ds, c, ty, t - dt.timedelta(days=d), "UPI")
            st.success("Sample data added")
        with st.expander("Reset all student data"):
            if st.checkbox("Yes, delete everything") and st.button("Delete all"):
                for tbl in ("expenses", "goals", "settings"):
                    con.execute(f"DELETE FROM {tbl}")
                con.commit()
                st.rerun()

    df = pd.read_sql_query("SELECT * FROM expenses", con)
    row = con.execute("SELECT value FROM settings WHERE key='budget'").fetchone()
    budget = float(row[0]) if row else 5000.0
    month = dt.date.today().strftime("%Y-%m")
    mdf = df[df["date"].astype(str).str[:7] == month]
    spent = float(mdf["amount"].sum())

    if page == PAGES[0]:
        pct = spent / budget if budget > 0 else 0.0
        c = st.columns(4)
        c[0].metric("Monthly budget", rs(budget))
        c[1].metric("Spent this month", rs(spent))
        c[2].metric("Remaining", rs(max(0, budget - spent)))
        c[3].metric("Daily average", rs(spent / max(1, dt.date.today().day)))
        st.progress(min(pct, 1.0), text=f"{pct * 100:.0f}% of your monthly budget used")
        if pct >= 1:
            st.error("⚠️ You have exceeded your budget.")
        elif pct >= 0.8:
            st.warning("⚠️ You have used more than 80% of your budget.")
        with st.expander("Edit budget"):
            nb = st.number_input("Monthly budget (₹)", min_value=1.0, value=budget, step=500.0)
            if st.button("Save budget"):
                con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('budget',?)", (float(nb),))
                con.commit()
                st.rerun()
        left, right = st.columns(2)
        with left:
            st.subheader("Need vs want")
            needs = float(mdf.loc[mdf["type"] == "need", "amount"].sum())
            wants = spent - needs
            st.write(f"Needs **{rs(needs)}**  ·  Wants **{rs(wants)}**")
            if spent > 0:
                st.progress(needs / spent, text=f"{needs / spent * 100:.0f}% needs")
            else:
                st.info("No expenses this month yet.")
        with right:
            st.subheader("Spending by category")
            if mdf.empty:
                st.info("No expenses this month yet.")
            else:
                st.bar_chart(mdf.groupby("category")["amount"].sum())
        st.subheader("Recent expenses")
        st.dataframe(df.sort_values("date", ascending=False).head(5).drop(columns=["id"]), hide_index=True)

    elif page == PAGES[1]:
        q = st.text_input("🔎 Search expenses")
        c1, c2 = st.columns(2)
        fc = c1.selectbox("Category", ["All"] + list(CATS))
        ft = c2.selectbox("Type", ["All", "need", "want"])
        v = df[df["description"].str.lower().str.contains(q.lower(), regex=False)] if q else df
        if fc != "All":
            v = v[v["category"] == fc]
        if ft != "All":
            v = v[v["type"] == ft]
        v = v.sort_values("date", ascending=False)
        st.dataframe(v.drop(columns=["id"]), hide_index=True)
        if not v.empty:
            lab = {int(r.id): f"{r.date} · {r.description} · {rs(r.amount)}" for r in v.itertuples()}
            pick = st.selectbox("Delete an expense", list(lab), format_func=lambda i: lab[i])
            if st.button("🗑 Delete selected"):
                con.execute("DELETE FROM expenses WHERE id=?", (int(pick),))
                con.commit()
                st.rerun()

    elif page == PAGES[2]:
        if df.empty:
            st.info("Add some expenses first (or load the sample data).")
        else:
            cats = df.groupby("category")["amount"].sum().sort_values(ascending=False)
            a, b = st.columns(2)
            a.subheader("Category distribution")
            a.bar_chart(cats)
            days = pd.date_range(end=pd.Timestamp.today().normalize(), periods=7)
            by = df.groupby("date")["amount"].sum()
            b.subheader("7-day spending")
            b.line_chart(pd.Series([float(by.get(d.strftime("%Y-%m-%d"), 0)) for d in days], index=days))
            wants = float(df.loc[df["type"] == "want", "amount"].sum())
            i = st.columns(3)
            i[0].metric("🔥 Highest category", f"{cats.index[0]}", rs(cats.iloc[0]), delta_color="off")
            i[1].metric("💰 Potential savings", rs(wants * 0.25), "25% of wants", delta_color="off")
            i[2].metric("📊 Average expense", rs(df["amount"].mean()))

    else:
        with st.form("add_goal", clear_on_submit=True):
            st.subheader("Create a savings goal")
            name = st.text_input("Goal name", placeholder="New laptop")
            target = st.number_input("Target (₹)", min_value=1.0, value=10000.0, step=500.0)
            saved = st.number_input("Already saved (₹)", min_value=0.0, value=0.0, step=100.0)
            if st.form_submit_button("Create goal") and name.strip():
                con.execute("INSERT INTO goals(name,target,saved) VALUES (?,?,?)", (name.strip(), float(target), float(saved)))
                con.commit()
                st.rerun()
        goals = con.execute("SELECT id,name,target,saved FROM goals ORDER BY id DESC").fetchall()
        if not goals:
            st.info("No savings goals yet.")
        for gid, gname, gt, gs in goals:
            with st.container(key=f"card_goal_{gid}"):
                st.markdown(f"**🎯 {gname}**: {rs(gs)} of {rs(gt)} ({rs(max(0, gt - gs))} left)")
                st.progress(min(1.0, gs / gt) if gt > 0 else 0.0)
                c1, c2, c3 = st.columns([2, 1, 1])
                add = c1.number_input("Add savings (₹)", min_value=0.0, value=0.0, step=100.0, key=f"add{gid}")
                if c2.button("Add", key=f"a{gid}") and add > 0:
                    con.execute("UPDATE goals SET saved=saved+? WHERE id=?", (float(add), gid))
                    con.commit()
                    st.rerun()
                if c3.button("Delete", key=f"d{gid}"):
                    con.execute("DELETE FROM goals WHERE id=?", (gid,))
                    con.commit()
                    st.rerun()
