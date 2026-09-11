from __future__ import annotations

import streamlit as st
from sqlalchemy import func

from app.database.database import SessionLocal
from app.database.models import Email, ReplyDraft


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Email Command Center",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PREMIUM FUTURISTIC CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background-color: #070a0f !important;
        color: #f5f7ff !important;

        background-image:
            radial-gradient(
                circle at 10% 10%,
                rgba(92, 72, 220, 0.14),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(0, 180, 255, 0.09),
                transparent 30%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(130, 60, 255, 0.08),
                transparent 35%
            );

        background-size:
            140% 140%,
            150% 150%,
            160% 160%;

        animation:
            commandCenterGlow
            18s
            ease-in-out
            infinite
            alternate;
    }


    @keyframes commandCenterGlow {

        0% {
            background-position:
                0% 0%,
                100% 0%,
                50% 100%;
        }

        25% {
            background-position:
                20% 15%,
                85% 20%,
                40% 85%;
        }

        50% {
            background-position:
                40% 30%,
                65% 40%,
                30% 65%;
        }

        75% {
            background-position:
                65% 45%,
                35% 60%,
                65% 40%;
        }

        100% {
            background-position:
                80% 60%,
                10% 80%,
                80% 20%;
        }
    }


    /* ========================================================
       MAIN CONTENT
       ======================================================== */

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* ========================================================
       NORMAL TEXT
       ======================================================== */

    .stApp p {
        color: #c7cfdd !important;
    }

    .stApp label {
        color: #c7cfdd !important;
    }


    /* ========================================================
       HEADINGS
       ======================================================== */

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4 {
        color: #ffffff !important;
    }


    /* ========================================================
       HERO TITLE
       ======================================================== */

    .hero-title {
        color: #ffffff !important;
        font-size: 42px !important;
        font-weight: 800 !important;
        letter-spacing: -1.2px;
        line-height: 1.1;
    }


    .hero-subtitle {
        color: #8f9bb3 !important;
        font-size: 13px !important;
        letter-spacing: 1.4px;
    }


    /* ========================================================
       SECTION HEADINGS
       ======================================================== */

    .section-heading {
        color: #ffffff !important;
        font-size: 21px !important;
        font-weight: 700 !important;
    }


    .section-description {
        color: #7f8ba1 !important;
        font-size: 13px !important;
    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    div[data-testid="stMetric"] {
        background: rgba(15, 19, 28, 0.90) !important;

        border: 1px solid
            rgba(255, 255, 255, 0.09) !important;

        border-radius: 18px !important;

        padding: 20px !important;

        box-shadow:
            0 10px 30px
            rgba(0, 0, 0, 0.28) !important;

        transition:
            transform 0.25s ease,
            border-color 0.25s ease,
            box-shadow 0.25s ease;
    }


    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);

        border-color:
            rgba(130, 150, 255, 0.32) !important;

        box-shadow:
            0 16px 38px
            rgba(0, 0, 0, 0.38) !important;
    }


    div[data-testid="stMetric"] label {
        color: #7f8ba1 !important;
        font-size: 11px !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }


    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }


    div[data-testid="stMetricDelta"] {
        color: #aeb8ca !important;
    }


    /* ========================================================
       NATIVE BORDERED CONTAINERS
       ======================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(12, 16, 24, 0.86) !important;

        border: 1px solid
            rgba(255, 255, 255, 0.075) !important;

        border-radius: 18px !important;

        box-shadow:
            0 10px 30px
            rgba(0, 0, 0, 0.22) !important;

        transition:
            transform 0.22s ease,
            border-color 0.22s ease;
    }


    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color:
            rgba(120, 145, 255, 0.24) !important;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    div[data-testid="stExpander"] {
        background: rgba(12, 16, 24, 0.90) !important;

        border: 1px solid
            rgba(255, 255, 255, 0.075) !important;

        border-radius: 15px !important;

        margin-bottom: 10px;
    }


    div[data-testid="stExpander"] summary {
        color: #ffffff !important;
    }


    div[data-testid="stExpander"] summary span {
        color: #ffffff !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        background: rgba(255, 255, 255, 0.045) !important;

        color: #ffffff !important;

        border: 1px solid
            rgba(255, 255, 255, 0.11) !important;

        border-radius: 12px !important;

        font-weight: 600 !important;

        transition:
            all 0.2s ease;
    }


    .stButton > button:hover {
        background:
            rgba(100, 120, 255, 0.12) !important;

        border-color:
            rgba(130, 150, 255, 0.42) !important;

        color: #ffffff !important;

        transform:
            translateY(-2px);
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {
        color: #7f8ba1 !important;
        font-weight: 600 !important;
    }


    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
    }


    /* ========================================================
       TEXT AREAS
       ======================================================== */

    textarea {
        background-color: #0d1118 !important;
        color: #ffffff !important;

        border-color:
            rgba(255, 255, 255, 0.10) !important;
    }


    textarea::placeholder {
        color: #657187 !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #080b11 !important;

        border-right:
            1px solid
            rgba(255, 255, 255, 0.07);
    }


    section[data-testid="stSidebar"] p {
        color: #c7cfdd !important;
    }


    section[data-testid="stSidebar"] label {
        color: #b8c2d2 !important;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    .stAlert {
        border-radius: 14px !important;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color:
            rgba(255, 255, 255, 0.065) !important;
    }


    /* ========================================================
       PROGRESS
       ======================================================== */

    div[data-testid="stProgress"] {
        border-radius: 20px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        color: #68748b !important;

        text-align: center;

        padding: 30px 0;

        font-size: 12px;
    }


    /* ========================================================
       SCROLLBAR
       ======================================================== */

    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }


    ::-webkit-scrollbar-track {
        background: #070a0f;
    }


    ::-webkit-scrollbar-thumb {
        background:
            rgba(130, 145, 180, 0.25);

        border-radius: 10px;
    }


    ::-webkit-scrollbar-thumb:hover {
        background:
            rgba(130, 145, 180, 0.40);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_dashboard_stats():
    db = SessionLocal()

    try:
        total_emails = (
            db.query(func.count(Email.id))
            .scalar()
            or 0
        )

        analyzed_emails = (
            db.query(func.count(Email.id))
            .filter(
                Email.category.is_not(None)
            )
            .scalar()
            or 0
        )

        pending_analysis = (
            db.query(func.count(Email.id))
            .filter(
                Email.category.is_(None)
            )
            .scalar()
            or 0
        )

        pending_drafts = (
            db.query(func.count(ReplyDraft.id))
            .filter(
                ReplyDraft.status == "pending"
            )
            .scalar()
            or 0
        )

        approved_drafts = (
            db.query(func.count(ReplyDraft.id))
            .filter(
                ReplyDraft.status == "approved"
            )
            .scalar()
            or 0
        )

        sent_drafts = (
            db.query(func.count(ReplyDraft.id))
            .filter(
                ReplyDraft.status == "sent"
            )
            .scalar()
            or 0
        )

        follow_ups = (
            db.query(func.count(ReplyDraft.id))
            .filter(
                ReplyDraft.follow_up_status.in_(
                    [
                        "pending",
                        "due",
                        "follow_up_required",
                    ]
                )
            )
            .scalar()
            or 0
        )

        return {
            "total": total_emails,
            "analyzed": analyzed_emails,
            "pending_analysis": pending_analysis,
            "pending_drafts": pending_drafts,
            "approved": approved_drafts,
            "sent": sent_drafts,
            "follow_ups": follow_ups,
        }

    finally:
        db.close()


def get_recent_emails(limit=8):
    db = SessionLocal()

    try:
        return (
            db.query(Email)
            .order_by(Email.id.desc())
            .limit(limit)
            .all()
        )

    finally:
        db.close()


def get_all_emails():
    db = SessionLocal()

    try:
        return (
            db.query(Email)
            .order_by(Email.id.desc())
            .all()
        )

    finally:
        db.close()


def get_reply_drafts():
    db = SessionLocal()

    try:
        return (
            db.query(ReplyDraft)
            .order_by(ReplyDraft.id.desc())
            .all()
        )

    finally:
        db.close()


def get_follow_up_drafts():
    db = SessionLocal()

    try:
        return (
            db.query(ReplyDraft)
            .filter(
                ReplyDraft.follow_up_status.in_(
                    [
                        "pending",
                        "due",
                        "follow_up_required",
                        "replied",
                    ]
                )
            )
            .order_by(
                ReplyDraft.follow_up_at.asc()
            )
            .all()
        )

    finally:
        db.close()


def get_category_counts():
    db = SessionLocal()

    try:
        rows = (
            db.query(
                Email.category,
                func.count(Email.id),
            )
            .filter(
                Email.category.is_not(None)
            )
            .group_by(Email.category)
            .order_by(
                func.count(Email.id).desc()
            )
            .all()
        )

        return [
            {
                "category": category or "Unknown",
                "count": count,
            }
            for category, count in rows
        ]

    finally:
        db.close()


# ============================================================
# SMALL UI HELPERS
# ============================================================

def show_priority(priority):
    if priority == "URGENT":
        return "🔴 URGENT"

    if priority == "HIGH":
        return "🟠 HIGH"

    if priority == "MEDIUM":
        return "🟡 MEDIUM"

    if priority == "LOW":
        return "🟢 LOW"

    return "⚪ UNKNOWN"


def show_status(status):
    status_map = {
        "received": "📥 RECEIVED",
        "replied": "↩️ REPLIED",
        "pending": "⏳ PENDING",
        "approved": "✅ APPROVED",
        "sent": "📤 SENT",
        "due": "⚠️ DUE",
        "follow_up_required": "🔔 FOLLOW-UP REQUIRED",
        "replied": "💬 CUSTOMER REPLIED",
    }

    return status_map.get(
        status,
        f"⚪ {status.upper()}",
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown(
            "## ✦ AI Command Center"
        )

        st.caption(
            "INTELLIGENT EMAIL AUTOMATION SYSTEM"
        )

        st.divider()

        st.success(
            "● SYSTEM ONLINE"
        )

        st.divider()

        st.markdown(
            "**NAVIGATION**"
        )

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Inbox",
                "AI Analysis",
                "Reply Drafts",
                "Follow-ups",
                "Analytics",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        st.markdown(
            "**AUTOMATION CORE**"
        )

        st.caption(
            "✦ Gemini AI\n\n"
            "✉ Gmail API\n\n"
            "◷ Scheduler"
        )

        st.divider()

        st.caption(
            "AI Email Automation Agent\n"
            "Development Mode"
        )

    return page


# ============================================================
# DASHBOARD PAGE
# ============================================================

def render_dashboard():

    stats = get_dashboard_stats()

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        '<div class="hero-title">'
        'AI Email Command Center'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'INTELLIGENT EMAIL PROCESSING • '
        'AI ANALYSIS • HUMAN APPROVAL • AUTOMATION'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    st.success(
        "● AUTOMATION CORE ONLINE"
    )

    st.write("")

    # --------------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-heading">'
        'System Overview'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Real-time intelligence from your automation database'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "TOTAL EMAILS",
            stats["total"],
        )

    with col2:
        st.metric(
            "AI ANALYZED",
            stats["analyzed"],
        )

    with col3:
        st.metric(
            "PENDING DRAFTS",
            stats["pending_drafts"],
        )

    with col4:
        st.metric(
            "FOLLOW-UPS",
            stats["follow_ups"],
        )

    st.write("")

    # --------------------------------------------------------
    # AUTOMATION CORE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-heading">'
        'Automation Core'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Connected infrastructure and processing services'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        with st.container(border=True):

            st.subheader(
                "✦ Gemini AI Engine"
            )

            st.success(
                "ONLINE"
            )

            st.caption(
                "Email classification, summarization, "
                "intent detection and reply generation."
            )

    with col2:

        with st.container(border=True):

            st.subheader(
                "✉ Gmail Integration"
            )

            st.success(
                "CONNECTED"
            )

            st.caption(
                "Email fetching, attachment processing "
                "and secure Gmail API communication."
            )

    with col3:

        with st.container(border=True):

            st.subheader(
                "◷ Automation Scheduler"
            )

            st.success(
                "READY"
            )

            st.caption(
                "Automated email processing and "
                "follow-up monitoring."
            )

    st.write("")

    # --------------------------------------------------------
    # PROCESSING HEALTH
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-heading">'
        'Processing Health'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Current state of the AI processing pipeline'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "ANALYZED",
            stats["analyzed"],
        )

    with col2:
        st.metric(
            "WAITING FOR AI",
            stats["pending_analysis"],
        )

    with col3:
        st.metric(
            "APPROVED",
            stats["approved"],
        )

    with col4:
        st.metric(
            "SENT",
            stats["sent"],
        )

    # --------------------------------------------------------
    # ANALYSIS PROGRESS
    # --------------------------------------------------------

    if stats["total"] > 0:

        percentage = (
            stats["analyzed"]
            / stats["total"]
        )

        st.write("")

        st.caption(
            f"AI processing completion: "
            f"{percentage * 100:.1f}%"
        )

        st.progress(
            percentage
        )

    st.write("")

    # --------------------------------------------------------
    # RECENT INTELLIGENCE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-heading">'
        'Recent Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Latest emails processed by the automation engine'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    emails = get_recent_emails(8)

    if not emails:

        st.info(
            "No emails found in the database yet."
        )

    else:

        for email in emails:

            subject = (
                email.subject.strip()
                if email.subject
                else "(No subject)"
            )

            with st.expander(
                f"✉ {subject}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.caption("FROM")
                    st.write(
                        email.sender or "Unknown"
                    )

                with col2:
                    st.caption("CATEGORY")
                    st.write(
                        email.category
                        or "Pending AI analysis"
                    )

                with col3:
                    st.caption("PRIORITY")
                    st.write(
                        show_priority(
                            email.priority
                        )
                    )

                st.divider()

                col1, col2 = st.columns(2)

                with col1:
                    st.caption("STATUS")
                    st.write(
                        show_status(
                            email.status
                        )
                    )

                with col2:
                    st.caption("EMAIL ID")
                    st.write(
                        email.id
                    )

                st.divider()

                st.caption("SUMMARY")

                st.write(
                    email.summary
                    or "No AI summary available."
                )

    st.write("")

    st.caption(
        "AI Email Automation Agent • "
        "Command Center"
    )


# ============================================================
# INBOX PAGE
# ============================================================

def render_inbox():

    st.title(
        "📥 Inbox"
    )

    st.caption(
        "All emails currently stored in the automation database."
    )

    emails = get_all_emails()

    if not emails:

        st.info(
            "No emails available."
        )
        return

    st.write(
        f"**{len(emails)} emails**"
    )

    for email in emails:

        subject = (
            email.subject.strip()
            if email.subject
            else "(No subject)"
        )

        with st.expander(
            f"✉ {subject}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.caption("FROM")

                st.write(
                    email.sender
                    or "Unknown"
                )

                st.caption("TO")

                st.write(
                    email.recipient
                    or "Unknown"
                )

                st.caption("CATEGORY")

                st.write(
                    email.category
                    or "Pending"
                )

            with col2:

                st.caption("PRIORITY")

                st.write(
                    show_priority(
                        email.priority
                    )
                )

                st.caption("STATUS")

                st.write(
                    show_status(
                        email.status
                    )
                )

                st.caption("EMAIL ID")

                st.write(
                    email.id
                )

            st.divider()

            st.caption("EMAIL BODY")

            if email.body:
                st.text(
                    email.body
                )
            else:
                st.info(
                    "No email body available."
                )


# ============================================================
# AI ANALYSIS PAGE
# ============================================================

def render_ai_analysis():

    st.title(
        "🧠 AI Analysis"
    )

    st.caption(
        "Classification, priority, intent and summaries generated by Gemini."
    )

    emails = get_all_emails()

    analyzed = [
        email
        for email in emails
        if email.category
    ]

    if not analyzed:

        st.info(
            "No analyzed emails available."
        )
        return

    for email in analyzed:

        subject = (
            email.subject.strip()
            if email.subject
            else "(No subject)"
        )

        with st.expander(
            f"✦ {subject}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "EMAIL ID",
                    email.id,
                )

            with col2:

                st.metric(
                    "CATEGORY",
                    email.category,
                )

            with col3:

                st.metric(
                    "PRIORITY",
                    email.priority,
                )

            st.divider()

            st.caption("REQUIRES REPLY")

            if email.requires_reply:

                st.success(
                    "YES — Reply required"
                )

            else:

                st.info(
                    "NO — Reply not required"
                )

            st.caption("INTENT")

            st.write(
                email.intent
                or "No intent available."
            )

            st.caption("AI SUMMARY")

            st.write(
                email.summary
                or "No summary available."
            )


# ============================================================
# REPLY DRAFTS PAGE
# ============================================================

def render_reply_drafts():

    st.title(
        "✍ Reply Drafts"
    )

    st.caption(
        "AI-generated replies waiting for human approval or already processed."
    )

    drafts = get_reply_drafts()

    if not drafts:

        st.info(
            "No reply drafts found."
        )
        return

    for draft in drafts:

        status_text = show_status(
            draft.status
        )

        with st.expander(
            f"Draft #{draft.id} • "
            f"Email #{draft.email_id} • "
            f"{status_text}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "DRAFT ID",
                    draft.id,
                )

            with col2:

                st.metric(
                    "EMAIL ID",
                    draft.email_id,
                )

            with col3:

                st.metric(
                    "STATUS",
                    draft.status.upper(),
                )

            st.divider()

            st.caption(
                "AI GENERATED REPLY"
            )

            st.text_area(
                "Draft",
                value=draft.draft_text,
                height=220,
                disabled=True,
                key=f"draft_view_{draft.id}",
                label_visibility="collapsed",
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.caption(
                    "FOLLOW-UP STATUS"
                )

                st.write(
                    draft.follow_up_status
                    or "not_required"
                )

            with col2:

                st.caption(
                    "FOLLOW-UP DATE"
                )

                st.write(
                    str(
                        draft.follow_up_at
                    )
                    if draft.follow_up_at
                    else "Not scheduled"
                )


# ============================================================
# FOLLOW-UP PAGE
# ============================================================

def render_follow_ups():

    st.title(
        "🔔 Follow-ups"
    )

    st.caption(
        "Customer replies and pending follow-up workflow."
    )

    drafts = get_follow_up_drafts()

    if not drafts:

        st.success(
            "No active follow-ups."
        )
        return

    for draft in drafts:

        with st.expander(
            f"Follow-up • Draft #{draft.id} • "
            f"Email #{draft.email_id}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "DRAFT",
                    draft.id,
                )

            with col2:

                st.metric(
                    "EMAIL",
                    draft.email_id,
                )

            with col3:

                st.metric(
                    "STATUS",
                    (
                        draft.follow_up_status
                        or "unknown"
                    ).upper(),
                )

            st.divider()

            st.caption(
                "FOLLOW-UP SCHEDULE"
            )

            if draft.follow_up_at:

                st.write(
                    str(
                        draft.follow_up_at
                    )
                )

            else:

                st.write(
                    "No follow-up date."
                )

            st.caption(
                "REPLY STATUS"
            )

            status = (
                draft.follow_up_status
                or "not_required"
            )

            if status == "replied":

                st.success(
                    "Customer has replied."
                )

            elif status in (
                "due",
                "follow_up_required",
            ):

                st.warning(
                    "Follow-up required."
                )

            elif status == "pending":

                st.info(
                    "Follow-up is scheduled."
                )

            else:

                st.write(
                    status
                )


# ============================================================
# ANALYTICS PAGE
# ============================================================

def render_analytics():

    st.title(
        "📊 Analytics"
    )

    st.caption(
        "Email processing and AI classification statistics."
    )

    stats = get_dashboard_stats()

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    tab1, tab2 = st.tabs(
        [
            "Overview",
            "Categories",
        ]
    )

    with tab1:

        st.subheader(
            "Processing Overview"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "TOTAL",
                stats["total"],
            )

        with col2:

            st.metric(
                "ANALYZED",
                stats["analyzed"],
            )

        with col3:

            st.metric(
                "PENDING ANALYSIS",
                stats["pending_analysis"],
            )

        with col4:

            st.metric(
                "SENT",
                stats["sent"],
            )

        st.write("")

        if stats["total"] > 0:

            analysis_rate = (
                stats["analyzed"]
                / stats["total"]
            )

            st.caption(
                f"AI Analysis Completion — "
                f"{analysis_rate * 100:.1f}%"
            )

            st.progress(
                analysis_rate
            )

        st.write("")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "PENDING DRAFTS",
                stats["pending_drafts"],
            )

        with col2:

            st.metric(
                "APPROVED",
                stats["approved"],
            )

        with col3:

            st.metric(
                "FOLLOW-UPS",
                stats["follow_ups"],
            )

    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    with tab2:

        st.subheader(
            "Email Categories"
        )

        categories = get_category_counts()

        if not categories:

            st.info(
                "No category data available."
            )

        else:

            total = sum(
                item["count"]
                for item in categories
            )

            for item in categories:

                category = item["category"]
                count = item["count"]

                percentage = (
                    count / total
                    if total
                    else 0
                )

                with st.container(
                    border=True
                ):

                    col1, col2 = st.columns(
                        [4, 1]
                    )

                    with col1:

                        st.write(
                            f"**{category}**"
                        )

                        st.progress(
                            percentage
                        )

                    with col2:

                        st.metric(
                            "EMAILS",
                            count,
                        )


# ============================================================
# MAIN
# ============================================================

def main():

    page = render_sidebar()

    if page == "Dashboard":

        render_dashboard()

    elif page == "Inbox":

        render_inbox()

    elif page == "AI Analysis":

        render_ai_analysis()

    elif page == "Reply Drafts":

        render_reply_drafts()

    elif page == "Follow-ups":

        render_follow_ups()

    elif page == "Analytics":

        render_analytics()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()