import math
import streamlit as st

st.set_page_config(
    page_title="Calculator",
    page_icon="🧮",
    layout="centered",
)

# ----- Visual theme -----
C = {
    "bg0": "#07161A",
    "bg1": "#0E2A30",
    "bg2": "#143840",
    "panel": "#0B2228",
    "panel_edge": "#1E4A52",
    "display": "#041014",
    "display_edge": "#2A6B74",
    "mint": "#7EF0D8",
    "mint_dim": "#3A9E8E",
    "coral": "#FF6B4A",
    "coral_hot": "#FF8A70",
    "ink": "#E7F6F4",
    "muted": "#6A9AA0",
    "key": "#164048",
    "op": "#1A5C58",
    "op_on": "#7EF0D8",
}

st.markdown(
    f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at 20% 15%, rgba(58,158,142,.20), transparent 25%),
            radial-gradient(circle at 82% 72%, rgba(255,107,74,.10), transparent 25%),
            linear-gradient(145deg, {C["bg0"]}, {C["bg2"]});
        color: {C["ink"]};
    }}

    .block-container {{
        max-width: 430px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    .calc-panel {{
        background: linear-gradient(145deg, {C["panel"]}, {C["bg1"]});
        border: 2px solid {C["panel_edge"]};
        border-radius: 30px;
        padding: 22px;
        box-shadow: 0 15px 40px rgba(0,0,0,.35);
    }}

    .display {{
        background: {C["display"]};
        border: 2px solid {C["display_edge"]};
        border-radius: 24px;
        padding: 16px 18px;
        text-align: right;
        margin-bottom: 18px;
    }}

    .expression {{
        color: {C["muted"]};
        min-height: 25px;
        font-family: monospace;
        font-size: 14px;
    }}

    .value {{
        color: {C["mint"]};
        font-size: 42px;
        font-weight: 700;
        overflow-x: auto;
        white-space: nowrap;
    }}

    div.stButton > button {{
        width: 100%;
        height: 58px;
        border-radius: 18px;
        border: 1px solid {C["panel_edge"]};
        background: {C["key"]};
        color: {C["ink"]};
        font-size: 20px;
        font-weight: 700;
    }}

    div.stButton > button:hover {{
        border-color: {C["mint"]};
        color: {C["mint"]};
    }}

    div[data-testid="column"]:has(button[kind="secondary"]) {{
        min-width: 0;
    }}

    .op button {{
        background: {C["op"]} !important;
        color: {C["mint"]} !important;
    }}

    .eq button {{
        background: {C["coral"]} !important;
        color: white !important;
    }}

    .func button {{
        background: #243B42 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----- State -----
defaults = {
    "expression": "",
    "current": "0",
    "operator": None,
    "left": None,
    "reset_next": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def fmt(num):
    if abs(num - int(num)) < 1e-12:
        return str(int(num))
    return f"{num:.10g}"


def calc(left, right, op):
    a, b = float(left), float(right)

    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ZeroDivisionError
        return a / b

    raise ValueError(op)


def clear():
    st.session_state.expression = ""
    st.session_state.current = "0"
    st.session_state.operator = None
    st.session_state.left = None
    st.session_state.reset_next = False


def error():
    st.session_state.expression = ""
    st.session_state.current = "Error"
    st.session_state.operator = None
    st.session_state.left = None
    st.session_state.reset_next = True


def delete_one():
    text = st.session_state.current

    if text in ("0", "Error", "") or len(text) == 1:
        st.session_state.current = "0"
        return

    if text.startswith("-") and len(text) == 2:
        st.session_state.current = "0"
        return

    st.session_state.current = text[:-1]

    if st.session_state.current in ("", "-"):
        st.session_state.current = "0"


def on_press(key):
    s = st.session_state

    if s.current == "Error" and key != "A/C":
        clear()

    if key == "A/C":
        clear()
        return

    if key == "DEL":
        if s.reset_next and s.operator is not None:
            s.current = s.left if s.left is not None else "0"
            s.left = None
            s.operator = None
            s.expression = ""
            s.reset_next = False
            return

        if s.reset_next:
            s.reset_next = False
            s.expression = ""

        delete_one()
        return

    if key == "%":
        try:
            s.current = fmt(float(s.current) / 100)
            s.reset_next = True
        except ValueError:
            error()
        return

    if key == "x2":
        try:
            s.current = fmt(float(s.current) ** 2)
            s.reset_next = True
        except ValueError:
            error()
        return

    if key in ("+", "-", "*", "/"):
        if s.left is not None and s.operator is not None and not s.reset_next:
            try:
                s.current = fmt(calc(s.left, s.current, s.operator))
            except ZeroDivisionError:
                error()
                return

        s.left = s.current
        s.operator = key
        s.expression = f"{s.current} {key}"
        s.reset_next = True
        return

    if key == "=":
        if s.operator is None or s.left is None:
            return

        try:
            right = s.current
            result = calc(s.left, right, s.operator)
            s.expression = f"{s.left} {s.operator} {right} ="
            s.current = fmt(result)
            s.left = None
            s.operator = None
            s.reset_next = True
        except ZeroDivisionError:
            error()
        return

    if key == ".":
        if s.reset_next:
            s.current = "0."
            s.reset_next = False
        elif "." not in s.current:
            s.current += "."
        return

    if key in "0123456789":
        if s.reset_next or s.current == "0":
            s.current = key
            s.reset_next = False
        else:
            digits = s.current.replace("-", "").replace(".", "")
            if len(digits) < 14:
                s.current += key


# ----- UI -----
st.markdown('<div class="calc-panel">', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="display">
        <div class="expression">{st.session_state.expression or "ready"}</div>
        <div class="value">{st.session_state.current}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

layout = [
    [("A/C", "func"), ("DEL", "func"), ("%", "func"), ("/", "op")],
    [("7", "num"), ("8", "num"), ("9", "num"), ("*", "op")],
    [("4", "num"), ("5", "num"), ("6", "num"), ("-", "op")],
    [("1", "num"), ("2", "num"), ("3", "num"), ("+", "op")],
    [("0", "num"), (".", "num"), ("x2", "num"), ("=", "eq")],
]

for row in layout:
    cols = st.columns(4, gap="small")

    for col, (label, kind) in zip(cols, row):
        with col:
            clicked = st.button(
                {"*": "×", "/": "÷", "-": "−", "x2": "x²"}.get(label, label),
                key=f"key_{label}",
                use_container_width=True,
            )

            if clicked:
                on_press(label)
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
