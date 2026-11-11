from datetime import date, datetime, timedelta
import hashlib
import time
import extra_streamlit_components as stx
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import streamlit as st
import streamlit.components.v1 as components

# 1. Konfiguracja strony
st.set_page_config(
    page_title="Mieszkanie Babci — Panel Inwestycji",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Ikony wektorowe SVG
SVG_HOME = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
SVG_WALLET = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>'
SVG_GAUGE = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>'
SVG_WRENCH = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>'
SVG_CHART = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>'
SVG_CLOCK = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px; vertical-align:-1px;"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
SVG_ARROW_UP = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>'
SVG_ARROW_DOWN = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>'

# 3. Styl CSS
st.markdown(
    """
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #0b0f19 !important;
    color: #f8fafc !important;
}

.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 720px;
}

@keyframes float-up {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-2.5px); }
}

@keyframes float-down {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(2.5px); }
}

@keyframes pulse-dot {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

@keyframes pulse-dot-red {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 7px rgba(239, 68, 68, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.header-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 4px;
}

.header-title {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 1.55rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 0;
    line-height: 1.2;
    letter-spacing: -0.02em;
}

.admin-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 2px 8px;
    border-radius: 6px;
    margin-top: 4px;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 14px 0 12px 0;
    letter-spacing: -0.01em;
}

.status-pill-rented {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34d399;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 999px;
}

.status-pill-empty {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #f87171;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 999px;
}

.dot-green {
    width: 8px;
    height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot 2s infinite;
}

.dot-red {
    width: 8px;
    height: 8px;
    background-color: #ef4444;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-dot-red 2s infinite;
}

.fin-card {
    background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease;
}

.fin-card:hover {
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

.fin-title {
    color: #94a3b8;
    font-size: 0.76rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}

.fin-value {
    color: #f8fafc;
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 14px;
}

.fin-badge-green {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background-color: rgba(16, 185, 129, 0.14);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34d399;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
}

.fin-badge-red {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background-color: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #f87171;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
}

.fin-arrow-up {
    display: inline-flex;
    align-items: center;
    animation: float-up 1.5s infinite ease-in-out;
}

.fin-arrow-down {
    display: inline-flex;
    align-items: center;
    animation: float-down 1.5s infinite ease-in-out;
}

.fin-date {
    display: flex;
    align-items: center;
    color: #64748b;
    font-size: 0.73rem;
    margin-top: 9px;
}

.prio-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 2px 8px;
    border-radius: 5px;
    margin-right: 8px;
}
.prio-high { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }
.prio-med { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); }
.prio-low { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }
</style>
""",
    unsafe_allow_html=True,
)


# 4. Połączenie z bazą Supabase
@st.cache_resource
def get_engine():
    return create_engine(st.secrets["DATABASE_URL"], pool_pre_ping=True)


engine = get_engine()

with engine.begin() as conn:
    conn.execute(
        text(
            "ALTER TABLE settings ADD COLUMN IF NOT EXISTS total_renovations NUMERIC(10, 2) DEFAULT 0;"
        )
    )
    conn.execute(
        text(
            "ALTER TABLE settings ADD COLUMN IF NOT EXISTS is_rented BOOLEAN DEFAULT TRUE;"
        )
    )
    conn.execute(
        text(
            "ALTER TABLE settings ADD COLUMN IF NOT EXISTS earned_interest NUMERIC(10, 2) DEFAULT 0;"
        )
    )

# 5. Obsługa ciasteczek (zapamiętywanie logowania na 30 dni) i sesji
cookie_manager = stx.CookieManager(key="mieszkanie_cookies")

valid_user_viewer = str(st.secrets.get("USER_RODZINA", "rodzina")).strip().lower()
valid_user_admin = str(st.secrets.get("USER_ADMIN", "admin")).strip().lower()

# Bezpieczne tokeny (hasło nie jest zapisywane jawnie w przeglądarce)
token_viewer = hashlib.sha256(
    f"{valid_user_viewer}_{st.secrets['PASS_RODZINA']}".encode()
).hexdigest()
token_admin = hashlib.sha256(
    f"{valid_user_admin}_{st.secrets['PASS_ADMIN']}".encode()
).hexdigest()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = None

if "logout_clicked" not in st.session_state:
    st.session_state.logout_clicked = False

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Sprawdzenie czy w przeglądarce jest już ważne ciasteczko
saved_token = cookie_manager.get(cookie="auth_token")
if (
    not st.session_state.logged_in
    and not st.session_state.logout_clicked
    and saved_token
):
    if saved_token == token_admin:
        st.session_state.logged_in = True
        st.session_state.role = "admin"
        st.session_state.user_name = "Administrator"
    elif saved_token == token_viewer:
        st.session_state.logged_in = True
        st.session_state.role = "viewer"
        st.session_state.user_name = "Rodzina"

if not st.session_state.logged_in:
    st.markdown(
        f"<div style='text-align: center; margin-bottom: 6px;'>{SVG_HOME}</div>"
        "<h2 style='text-align: center; margin-bottom: 4px; color: #f8fafc; font-weight: 800;'>Mieszkanie Babci</h2>"
        "<p style='text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;'>Autoryzacja dostępu do panelu inwestycji</p>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        user = st.text_input("Login").strip().lower()
        pwd = st.text_input("Hasło", type="password")
        remember = st.checkbox("Zapamiętaj mnie na tym urządzeniu (30 dni)", value=True)

        if st.form_submit_button(
            "Zaloguj się",
            icon=":material/login:",
            use_container_width=True,
            type="primary",
        ):
            if user == valid_user_viewer and pwd == st.secrets["PASS_RODZINA"]:
                st.session_state.logged_in = True
                st.session_state.logout_clicked = False
                st.session_state.role = "viewer"
                st.session_state.user_name = "Rodzina"
                if remember:
                    cookie_manager.set(
                        "auth_token",
                        token_viewer,
                        expires_at=datetime.now() + timedelta(days=30),
                    )
                    time.sleep(0.3)
                st.rerun()
            elif user == valid_user_admin and pwd == st.secrets["PASS_ADMIN"]:
                st.session_state.logged_in = True
                st.session_state.logout_clicked = False
                st.session_state.role = "admin"
                st.session_state.user_name = "Administrator"
                if remember:
                    cookie_manager.set(
                        "auth_token",
                        token_admin,
                        expires_at=datetime.now() + timedelta(days=30),
                    )
                    time.sleep(0.3)
                st.rerun()
            else:
                st.error("Nieprawidłowy login lub hasło.")
    st.stop()

is_admin = st.session_state.role == "admin"

# --- POBRANIE DANYCH Z BAZY ---
with engine.connect() as conn:
    s = conn.execute(text("SELECT * FROM settings WHERE id = 1")).mappings().fetchone()
    df_tasks = pd.read_sql(
        text(
            "SELECT id, title, priority, status, estimated_cost, assigned_to FROM"
            " renovations ORDER BY CASE WHEN status='Do zrobienia' THEN 1 WHEN"
            " status='W trakcie' THEN 2 ELSE 3 END, id DESC"
        ),
        conn,
    )
    df_meters = pd.read_sql(
        text(
            "SELECT id, reading_date, meter_type, value, note FROM meters ORDER"
            " BY reading_date DESC, id DESC"
        ),
        conn,
    )


def get_val(key, default=0.0):
    return float(s[key]) if s and s.get(key) is not None else default


def get_dt(key):
    return (
        s[key].strftime("%d.%m.%Y %H:%M")
        if s and s.get(key) is not None
        else "Brak zmian"
    )


is_rented = bool(s["is_rented"]) if s and s.get("is_rented") is not None else True

# --- GÓRNY PASEK (Informacja o trybie widoczna TYLKO dla Admina) ---
top1, top2 = st.columns([3, 1])
with top1:
    if is_rented:
        badge_html = '<span class="status-pill-rented"><span class="dot-green"></span>Wynajmowane</span>'
    else:
        badge_html = '<span class="status-pill-empty"><span class="dot-red"></span>Niewynajmowane</span>'

    admin_tag_html = (
        '<div class="admin-badge">Tryb: Administrator</div>' if is_admin else ""
    )

    st.markdown(
        f'<div class="header-wrap"><span class="header-title">{SVG_HOME} Mieszkanie Babci</span>{badge_html}</div>{admin_tag_html}',
        unsafe_allow_html=True,
    )

with top2:
    if st.button("Wyloguj", icon=":material/logout:", use_container_width=True):
        try:
            cookie_manager.delete("auth_token")
        except Exception:
            pass
        st.session_state.logged_in = False
        st.session_state.logout_clicked = True
        time.sleep(0.3)
        st.rerun()

# Przełącznik statusu wynajmu (Tylko Admin) + Przycisk nawigacji
if is_admin:
    nav1, nav2 = st.columns([2, 1])
    with nav1:
        if st.session_state.page == "dashboard":
            if st.button(
                "Analiza Oszczędności (2030 / 2035)",
                icon=":material/trending_up:",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.page = "compound"
                st.rerun()
        else:
            if st.button(
                "Powrót do głównego panelu",
                icon=":material/arrow_back:",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.page = "dashboard"
                st.rerun()
    with nav2:
        toggle_label = "Ustaw: Wolne" if is_rented else "Ustaw: Wynajmowane"
        if st.button(toggle_label, icon=":material/sync:", use_container_width=True):
            with engine.begin() as conn:
                conn.execute(
                    text("UPDATE settings SET is_rented = :r WHERE id = 1"),
                    {"r": not is_rented},
                )
            st.rerun()
else:
    if st.session_state.page == "dashboard":
        if st.button(
            "Analiza Oszczędności i Prognoza (2030 / 2035)",
            icon=":material/trending_up:",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.page = "compound"
            st.rerun()
    else:
        if st.button(
            "Powrót do głównego panelu",
            icon=":material/arrow_back:",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.page = "dashboard"
            st.rerun()

st.markdown("---")

# Konfiguracja 5 kafelków finansowych
TILES = [
    {
        "key": "income",
        "title": "Przychód bez podatku",
        "col_val": "total_rent_income",
        "col_last": "last_income_netto",
        "col_date": "last_income_date",
        "val": get_val("total_rent_income"),
        "last": get_val("last_income_netto"),
        "date": get_dt("last_income_date"),
        "is_expense": False,
    },
    {
        "key": "tax",
        "title": "Podatek",
        "col_val": "total_tax_paid",
        "col_last": "last_tax",
        "col_date": "last_tax_date",
        "val": get_val("total_tax_paid"),
        "last": get_val("last_tax"),
        "date": get_dt("last_tax_date"),
        "is_expense": False,
    },
    {
        "key": "savings",
        "title": "Konto oszczędnościowe",
        "col_val": "total_savings",
        "col_last": "last_savings_add",
        "col_date": "last_savings_date",
        "val": get_val("total_savings"),
        "last": get_val("last_savings_add"),
        "date": get_dt("last_savings_date"),
        "is_expense": False,
    },
    {
        "key": "renovations",
        "title": "Wydane na remonty od pierwszego wynajmu",
        "col_val": "total_renovations",
        "col_last": "last_renovation_add",
        "col_date": "last_renovation_date",
        "val": get_val("total_renovations"),
        "last": get_val("last_renovation_add"),
        "date": get_dt("last_renovation_date"),
        "is_expense": True,
    },
    {
        "key": "other",
        "title": "Inne",
        "col_val": "other_funds",
        "col_last": "last_other_add",
        "col_date": "last_other_date",
        "val": get_val("other_funds"),
        "last": get_val("last_other_add"),
        "date": get_dt("last_other_date"),
        "is_expense": True,
    },
]


def render_tile(tile):
    val_str = f"{tile['val']:,.2f} zł".replace(",", " ")
    last_str = f"{tile['last']:,.2f} zł".replace(",", " ")

    if tile["is_expense"]:
        badge_class = "fin-badge-red"
        arrow_html = f'<span class="fin-arrow-down">{SVG_ARROW_DOWN}</span>'
        label_prefix = "Ostatni wydatek: -"
    else:
        badge_class = "fin-badge-green"
        arrow_html = f'<span class="fin-arrow-up">{SVG_ARROW_UP}</span>'
        label_prefix = "Ostatnia wpłata: +"

    html = (
        f'<div class="fin-card">'
        f'<div class="fin-title">{tile["title"]}</div>'
        f'<div class="fin-value"><span class="gsap-counter" data-target="{tile["val"]:.2f}" data-decimals="2" data-suffix=" zł">{val_str}</span></div>'
        f'<div class="{badge_class}">'
        f"{arrow_html} {label_prefix}{last_str}"
        f"</div>"
        f'<div class="fin-date">{SVG_CLOCK} Modyfikacja: {tile["date"]}</div>'
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

    if is_admin:
        with st.popover(
            f"Edytuj: {tile['title']}", icon=":material/edit:", use_container_width=True
        ):
            mode = st.radio(
                "Tryb zmiany:",
                ["Dodaj kwotę do obecnej wartości", "Ustaw nową kwotę całkowitą"],
                key=f"m_{tile['key']}",
            )
            amount = st.number_input(
                "Kwota (zł)",
                min_value=0.0,
                value=100.0,
                step=50.0,
                key=f"a_{tile['key']}",
            )
            if st.button(
                "Zapisz zmiany",
                icon=":material/check:",
                key=f"b_{tile['key']}",
                use_container_width=True,
                type="primary",
            ):
                new_total = (tile["val"] + amount) if "Dodaj" in mode else amount
                now_ts = datetime.now()
                with engine.begin() as conn:
                    q = text(
                        f"UPDATE settings SET {tile['col_val']} = :v, {tile['col_last']}"
                        f" = :l, {tile['col_date']} = :d WHERE id = 1"
                    )
                    conn.execute(q, {"v": new_total, "l": amount, "d": now_ts})
                st.rerun()


def format_priority_badge(prio_raw):
    p = str(prio_raw).lower()
    if "pilne" in p or "1" in p:
        return '<span class="prio-tag prio-high">Pilne</span>'
    elif "standard" in p:
        return '<span class="prio-tag prio-med">Standard</span>'
    else:
        return '<span class="prio-tag prio-low">Drobiazg</span>'


# =========================================================
# WIDOK 1: WSZYSTKO NA JEDNEJ STRONIE (DASHBOARD GŁÓWNY)
# =========================================================
if st.session_state.page == "dashboard":
    st.markdown(
        f'<div class="section-header">{SVG_WALLET} <span>Podsumowanie finansowe</span></div>',
        unsafe_allow_html=True,
    )

    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        render_tile(TILES[0])
    with r1_c2:
        render_tile(TILES[1])

    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        render_tile(TILES[2])
    with r2_c2:
        render_tile(TILES[3])

    r3_c1, _ = st.columns(2)
    with r3_c1:
        render_tile(TILES[4])

    st.markdown("---")

    # 2. Sekcja Liczników
    st.markdown(
        f'<div class="section-header">{SVG_GAUGE} <span>Stany liczników (Prąd, Woda zimna, Gaz)</span></div>',
        unsafe_allow_html=True,
    )

    meter_types = ["Prąd (kWh)", "Woda zimna (m³)", "Gaz (m³)"]
    m_cols = st.columns(3)

    for idx, m_name in enumerate(meter_types):
        sub = (
            df_meters[df_meters["meter_type"] == m_name]
            if not df_meters.empty
            else pd.DataFrame()
        )
        with m_cols[idx]:
            if not sub.empty:
                val = float(sub.iloc[0]["value"])
                date_m = sub.iloc[0]["reading_date"]
                diff_str = "Odczyt bazowy"
                if len(sub) > 1:
                    diff = val - float(sub.iloc[1]["value"])
                    diff_str = f"Zużycie: {diff:+.1f}"
                st.markdown(
                    f'<div class="fin-card" style="padding: 14px;">'
                    f'<div class="fin-title">{m_name}</div>'
                    f'<div class="fin-value" style="font-size: 1.35rem; margin-bottom: 8px;"><span class="gsap-counter" data-target="{val:.2f}" data-decimals="2" data-suffix="">{val:.2f}</span></div>'
                    f'<div class="fin-badge-green">{diff_str}</div>'
                    f'<div class="fin-date">{SVG_CLOCK} {date_m}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="fin-card" style="padding: 14px;">'
                    f'<div class="fin-title">{m_name}</div>'
                    f'<div class="fin-value" style="font-size: 1.1rem; color: #64748b;">Brak danych</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

    if is_admin:
        with st.expander(
            "Dodaj nowy odczyt licznika", icon=":material/add_circle:", expanded=False
        ):
            with st.form("meter_f", clear_on_submit=True):
                m_date = st.date_input("Data odczytu", value=date.today())
                m_type = st.selectbox("Licznik", meter_types)
                m_val = st.number_input(
                    "Wskazanie licznika", min_value=0.0, step=0.1, format="%.2f"
                )
                m_note = st.text_input("Notatka (opcjonalnie)")

                if st.form_submit_button(
                    "Zapisz odczyt",
                    icon=":material/save:",
                    use_container_width=True,
                    type="primary",
                ):
                    with engine.begin() as conn:
                        conn.execute(
                            text(
                                "INSERT INTO meters (reading_date, meter_type, value, note)"
                                " VALUES (:d, :t, :v, :n)"
                            ),
                            {"d": m_date, "t": m_type, "v": m_val, "n": m_note},
                        )
                    st.rerun()

    with st.expander("Historia pomiarów", icon=":material/history:"):
        df_filtered_meters = (
            df_meters[df_meters["meter_type"].isin(meter_types)]
            if not df_meters.empty
            else pd.DataFrame()
        )
        if not df_filtered_meters.empty:
            for _, row in df_filtered_meters.iterrows():
                with st.container(border=True):
                    c_m1, c_m2 = st.columns([3, 1])
                    c_m1.markdown(
                        f"**{row['meter_type']}** — Stan: **{row['value']:.2f}**"
                    )
                    c_m1.caption(
                        f"Data: {row['reading_date']} | {row['note'] or 'Brak notatki'}"
                    )
                    if is_admin:
                        if c_m2.button(
                            "Usuń",
                            icon=":material/delete:",
                            key=f"del_m_{row['id']}",
                            use_container_width=True,
                        ):
                            with engine.begin() as conn:
                                conn.execute(
                                    text("DELETE FROM meters WHERE id=:id"),
                                    {"id": row["id"]},
                                )
                            st.rerun()
        else:
            st.info("Brak zapisanych odczytów.")

    st.markdown("---")

    # 3. Sekcja Remontów i Zadań
    st.markdown(
        f'<div class="section-header">{SVG_WRENCH} <span>Plan remontów i zadań</span></div>',
        unsafe_allow_html=True,
    )

    if is_admin:
        with st.expander(
            "Dodaj nowe zadanie remontowe", icon=":material/add_task:", expanded=False
        ):
            with st.form("task_f", clear_on_submit=True):
                t_title = st.text_input("Opis zadania lub zakupu")
                t_prio = st.selectbox(
                    "Priorytet",
                    ["Pilne", "Standard", "Drobiazg"],
                )
                t_cost = st.number_input(
                    "Szacowany koszt (zł)", min_value=0.0, step=50.0
                )
                t_who = st.text_input(
                    "Osoba odpowiedzialna", placeholder="np. Hubert / Hydraulik"
                )

                if (
                    st.form_submit_button(
                        "Dodaj zadanie",
                        icon=":material/check:",
                        use_container_width=True,
                        type="primary",
                    )
                    and t_title
                ):
                    with engine.begin() as conn:
                        conn.execute(
                            text(
                                "INSERT INTO renovations (title, priority, status,"
                                " estimated_cost, assigned_to) VALUES (:t, :p, 'Do"
                                " zrobienia', :c, :w)"
                            ),
                            {"t": t_title, "p": t_prio, "c": t_cost, "w": t_who},
                        )
                    st.rerun()

    if not df_tasks.empty:
        for _, row in df_tasks.iterrows():
            with st.container(border=True):
                prio_badge = format_priority_badge(row["priority"])
                st.markdown(
                    f"{prio_badge} <strong style='color:#f8fafc; font-size:0.95rem;'>{row['title']}</strong>",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"Status: **{row['status']}** | Koszt: **{row['estimated_cost']:.0f} zł** | Wykonawca: **{row['assigned_to'] or '-'}**"
                )
                if is_admin:
                    b1, b2, b3 = st.columns(3)
                    if row["status"] != "W trakcie":
                        if b1.button(
                            "W trakcie",
                            icon=":material/pending:",
                            key=f"p_{row['id']}",
                            use_container_width=True,
                        ):
                            with engine.begin() as conn:
                                conn.execute(
                                    text(
                                        "UPDATE renovations SET status='W trakcie' WHERE id=:id"
                                    ),
                                    {"id": row["id"]},
                                )
                            st.rerun()
                    if row["status"] != "Zrobione":
                        if b2.button(
                            "Zrobione",
                            icon=":material/task_alt:",
                            key=f"d_{row['id']}",
                            use_container_width=True,
                        ):
                            with engine.begin() as conn:
                                conn.execute(
                                    text(
                                        "UPDATE renovations SET status='Zrobione' WHERE id=:id"
                                    ),
                                    {"id": row["id"]},
                                )
                            st.rerun()
                    if b3.button(
                        "Usuń",
                        icon=":material/delete:",
                        key=f"del_{row['id']}",
                        use_container_width=True,
                    ):
                        with engine.begin() as conn:
                            conn.execute(
                                text("DELETE FROM renovations WHERE id=:id"),
                                {"id": row["id"]},
                            )
                        st.rerun()
    else:
        st.info("Brak zadań na liście.")


# =========================================================
# WIDOK 2: STRONA OSZCZĘDNOŚCI I PROCENTU SKŁADANEGO
# =========================================================
elif st.session_state.page == "compound":
    st.markdown(
        f'<div class="section-header">{SVG_CHART} <span>Stan konta oszczędnościowego i prognoza</span></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Wyliczenia opierają się na aktualnym saldzie oszczędności oraz uwzględniają 19% podatku od zysków kapitałowych."
    )

    current_savings = TILES[2]["val"]
    earned_interest = get_val("earned_interest", 0.0)
    db_month = get_val("monthly_deposit", 1500.0)
    db_rate = get_val("interest_rate", 6.0)

    cur1, cur2 = st.columns(2)
    with cur1:
        st.markdown(
            f'<div class="fin-card" style="padding: 16px;">'
            f'<div class="fin-title">Aktualnie na koncie</div>'
            f'<div class="fin-value" style="font-size: 1.65rem; margin-bottom: 8px;"><span class="gsap-counter" data-target="{current_savings:.2f}" data-decimals="2" data-suffix=" zł">{current_savings:,.2f} zł</span></div>'.replace(
                ",", " "
            )
            + f'<div class="fin-badge-green">Stała dopłata: +{db_month:,.0f} zł / mies.</div>'.replace(
                ",", " "
            )
            + f'<div class="fin-date">{SVG_CLOCK} Oprocentowanie: {db_rate:.2f}% w skali roku</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cur2:
        st.markdown(
            f'<div class="fin-card" style="padding: 16px;">'
            f'<div class="fin-title">Dotychczas zarobione z odsetek</div>'
            f'<div class="fin-value" style="font-size: 1.65rem; color: #34d399; margin-bottom: 8px;">+<span class="gsap-counter" data-target="{earned_interest:.2f}" data-decimals="2" data-suffix=" zł">{earned_interest:,.2f} zł</span></div>'.replace(
                ",", " "
            )
            + f'<div class="fin-badge-green"><span class="fin-arrow-up">{SVG_ARROW_UP}</span> Zysk wypracowany do dziś</div>'
            f'<div class="fin-date">{SVG_CLOCK} Wkład własny: {max(0.0, current_savings - earned_interest):,.2f} zł</div>'.replace(
                ",", " "
            )
            + f"</div>",
            unsafe_allow_html=True,
        )

    if is_admin:
        with st.expander(
            "Konfiguracja parametrów oszczędności",
            icon=":material/settings:",
            expanded=False,
        ):
            with st.form("admin_savings_settings"):
                new_earned = st.number_input(
                    "Dotychczas wypracowane odsetki (zł)",
                    min_value=0.0,
                    value=earned_interest,
                    step=50.0,
                )
                new_month = st.number_input(
                    "Miesięczna dopłata z najmu (zł)",
                    min_value=0.0,
                    value=db_month,
                    step=100.0,
                )
                new_rate = st.number_input(
                    "Roczne oprocentowanie konta (%)",
                    min_value=0.1,
                    max_value=25.0,
                    value=db_rate,
                    step=0.25,
                )
                if st.form_submit_button(
                    "Zapisz parametry",
                    icon=":material/save:",
                    use_container_width=True,
                    type="primary",
                ):
                    with engine.begin() as conn:
                        conn.execute(
                            text(
                                "UPDATE settings SET earned_interest=:e, monthly_deposit=:m, interest_rate=:r WHERE id=1"
                            ),
                            {"e": new_earned, "m": new_month, "r": new_rate},
                        )
                    st.success("Zaktualizowano parametry oszczędności.")
                    st.rerun()

    # Obliczenia przychodu dziennego oraz prognozy na 2030 i 2035 r. (po odtrąceniu 19% Belki)
    daily_gross = current_savings * (db_rate / 100.0) / 365.0
    daily_net = daily_gross * 0.81
    monthly_interest_net = daily_net * 30.41

    today = date.today()
    months_to_2030 = max(1, (2030 - today.year) * 12 + (12 - today.month))
    months_to_2035 = max(1, (2035 - today.year) * 12 + (12 - today.month))

    eff_monthly_rate_net = ((db_rate * 0.81) / 100.0) / 12.0

    def calc_future_net(months_count):
        b, c = current_savings, current_savings
        for _ in range(months_count):
            b += (b * eff_monthly_rate_net) + db_month
            c += db_month
        return round(b, 2), round(b - c, 2)

    val_2030, prof_2030 = calc_future_net(months_to_2030)
    val_2035, prof_2035 = calc_future_net(months_to_2035)

    st.markdown(
        f'<div class="section-header">{SVG_WALLET} <span>Prognoza kapitału i zysk dzienny (netto)</span></div>',
        unsafe_allow_html=True,
    )

    k_top1, k_top2, k_top3 = st.columns(3)
    with k_top1:
        st.markdown(
            f'<div class="fin-card" style="padding: 15px;">'
            f'<div class="fin-title">Dzienny przychód z konta</div>'
            f'<div class="fin-value" style="font-size: 1.4rem; margin-bottom: 8px;">+<span class="gsap-counter" data-target="{daily_net:.2f}" data-decimals="2" data-suffix=" zł">{daily_net:.2f} zł</span></div>'
            f'<div class="fin-badge-green">~{monthly_interest_net:.0f} zł / mies. netto</div>'
            f'<div class="fin-date">{SVG_CLOCK} Brutto: {daily_gross:.2f} zł / dzień</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with k_top2:
        st.markdown(
            f'<div class="fin-card" style="padding: 15px;">'
            f'<div class="fin-title">Kapitał na koniec 2030 r.</div>'
            f'<div class="fin-value" style="font-size: 1.4rem; margin-bottom: 8px;"><span class="gsap-counter" data-target="{val_2030:.0f}" data-decimals="0" data-suffix=" zł">{val_2030:,.0f} zł</span></div>'.replace(
                ",", " "
            )
            + f'<div class="fin-badge-green">+{prof_2030:,.0f} zł odsetek netto</div>'.replace(
                ",", " "
            )
            + f'<div class="fin-date">{SVG_CLOCK} Za {months_to_2030} mies.</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with k_top3:
        st.markdown(
            f'<div class="fin-card" style="padding: 15px;">'
            f'<div class="fin-title">Kapitał na koniec 2035 r.</div>'
            f'<div class="fin-value" style="font-size: 1.4rem; margin-bottom: 8px;"><span class="gsap-counter" data-target="{val_2035:.0f}" data-decimals="0" data-suffix=" zł">{val_2035:,.0f} zł</span></div>'.replace(
                ",", " "
            )
            + f'<div class="fin-badge-green">+{prof_2035:,.0f} zł odsetek netto</div>'.replace(
                ",", " "
            )
            + f'<div class="fin-date">{SVG_CLOCK} Za {months_to_2035} mies.</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # 3. Stały wykres i tabela na 10 lat
    history = []
    bal, con = current_savings, current_savings

    for m in range(1, (10 * 12) + 1):
        bal += (bal * eff_monthly_rate_net) + db_month
        con += db_month
        if m % 12 == 0:
            yr = int(m / 12)
            history.append(
                {
                    "Rok": yr,
                    "Okres": f"{yr} l. ({today.year + yr})",
                    "Wpłacony kapitał (zł)": round(con),
                    "Przyszłe odsetki netto (zł)": round(bal - con),
                    "Kapitał końcowy netto (zł)": round(bal),
                }
            )

    df_c = pd.DataFrame(history)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_c["Okres"],
            y=df_c["Wpłacony kapitał (zł)"],
            name="Wpłacony kapitał",
            marker_color="#3b82f6",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_c["Okres"],
            y=df_c["Przyszłe odsetki netto (zł)"],
            name="Zysk netto (po podatku)",
            marker_color="#10b981",
        )
    )
    fig.update_layout(
        barmode="stack",
        height=330,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        f'<div class="section-header">{SVG_CHART} <span>Projekcja 10-letnia (rok po roku)</span></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        df_c.set_index("Rok"),
        use_container_width=True,
    )

# =========================================================
# ANIMACJA GSAP (ŁADOWANIE CYFEREK OD ZERA)
# =========================================================
components.html(
    """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script>
    function runGsapCounters() {
        const parentDoc = window.parent.document;
        const counters = parentDoc.querySelectorAll('.gsap-counter');
        counters.forEach(el => {
            const target = parseFloat(el.getAttribute('data-target') || '0');
            const decimals = parseInt(el.getAttribute('data-decimals') || '2', 10);
            const suffix = el.getAttribute('data-suffix') || '';
            const obj = { val: 0 };
            gsap.to(obj, {
                val: target,
                duration: 1.4,
                ease: "power2.out",
                onUpdate: function() {
                    const parts = obj.val.toFixed(decimals).split('.');
                    parts[0] = parts[0].replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ");
                    el.innerText = parts.join('.') + suffix;
                }
            });
        });
    }
    setTimeout(runGsapCounters, 80);
    </script>
    """,
    height=0,
)
