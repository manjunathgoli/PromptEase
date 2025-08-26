import streamlit as st
import sqlite3
import requests

# =========================
# DATABASE (SQLite)
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

def create_usertable():
    # Ensure table exists
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    try:
        c.execute("ALTER TABLE users ADD COLUMN api_key TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    conn.commit()

def add_userdata(username, password, api_key):
    c.execute('INSERT INTO users(username,password,api_key) VALUES (?,?,?)', (username, password, api_key))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    data = c.fetchone()
    return data


# =========================
# AI APP FUNCTIONS
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_openrouter_response(model, prompt, **kwargs):
    try:
        if model == "ChatGPT":
            model = kwargs.get("model", "openai/gpt-oss-20b:free")
        elif model == "Gemini":
            model = kwargs.get("model", "google/gemma-3-27b-it:free")
        elif model == "mistral":
            model = kwargs.get("model", "z-ai/glm-4.5-air:free")
        elif model == "LLaMA":
            model = kwargs.get("model", "meta-llama/llama-3.3-70b-instruct:free")
        elif model == "DeepSeek":
            model = kwargs.get("model", "deepseek/deepseek-r1-0528-qwen3-8b:free")
        elif model == "nvidia":
            model = kwargs.get("model", "nvidia/llama-3.1-nemotron-ultra-253b-v1:free")

        headers = {
            "Authorization": f"Bearer {st.session_state.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Middleware Helper",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": f"Task={kwargs.get('task')} | Tone={kwargs.get('tone')} | mode = {kwargs.get('mode')} | style = {kwargs.get('style')} | persona = {kwargs.get('persona')} | depth = {kwargs.get('depth')} | format = {kwargs.get('format_type')} | language = {kwargs.get('language')} | bias = {kwargs.get('bias_filter')} | speed = {kwargs.get('speed_quality')} | memory = {kwargs.get('memory')}"},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        message = result["choices"][0]["message"]["content"]
        return f" Response: {message}"

    except Exception as e:
        return f" Error: {str(e)}"


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="AI Middleware Advanced", layout="wide")

create_usertable()

# Show login/signup only if NOT authenticated
if not st.session_state.authenticated:
    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox("🔑 Menu", menu)

    if choice == "Signup":
        st.subheader("📝 Create New Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        new_OpenRouter_api = st.text_input("OpenRouter API Key")
        st.markdown(
        "<a href='https://openrouter.ai/keys' target='_blank'>🔗 Get Key</a>", 
        unsafe_allow_html=True
    )

        if st.button("Signup"):
            if new_user and new_pass and new_OpenRouter_api:
                add_userdata(new_user, new_pass, new_OpenRouter_api)
                st.success("✅ Account created successfully! Go to Login.")
            else:
                st.warning("⚠️ Please enter all fields")

    elif choice == "Login":
        st.subheader("🔓 Login to your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            result = login_user(username, password)
            if result:
                st.success(f"Welcome {username} 🎉")
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.api_key = result[2]   # <-- load API key from DB
                st.rerun()  # 🔄 Refresh page so login/signup hides
            else:
                st.error("❌ Invalid username or password")

# =========================
# MAIN APP (AFTER LOGIN)
# =========================
if st.session_state.authenticated:
    st.sidebar.markdown(f"👤 Logged in as **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.api_key = None
        st.rerun()

    st.sidebar.title("⚙️ Parameters")

    model = st.sidebar.selectbox("Models", ["ChatGPT", "Gemini", "mistral", "LLaMA", "DeepSeek", "nvidia"])
    task = st.sidebar.selectbox("Tasks", ["Explain", "Translate", "Summarize", "Solve", "Tutor", "Generate code", "Research mode"])
    mode = st.sidebar.selectbox("Mode", ["Stepwise", "Direct", "Analogy", "Visual", "Comparative"])
    style = st.sidebar.selectbox("Style", ["Formal", "Conversational", "Beginner", "Expert"])
    persona = st.sidebar.selectbox("Persona", ["Student", "Doctor", "Engineer", "Lawyer", "Teacher"])
    depth = st.sidebar.selectbox("Depth", ["Short", "Medium", "Long", "Exhaustive"])
    format_type = st.sidebar.selectbox("Format", ["Text", "Table", "JSON", "Markdown", "Diagram"])
    language = st.sidebar.multiselect("Language", ["English", "Hindi", "Telugu", "French", "German", "Spanish", "Chinese", "Japanese"])
    tone = st.sidebar.selectbox("Tone", ["Neutral", "Fun", "Critical", "Polite"])
    domain = st.sidebar.selectbox("Domain", ["Science", "Tech", "Finance", "Medicine", "General", "Law"])
    creativity = st.sidebar.slider("Creativity", 0.0, 1.0, 0.5, 0.1)
    bias_filter = st.sidebar.selectbox("Bias Filter", ["Neutral", "Optimistic", "Skeptical", "Enterprise-friendly", "Consumer-friendly"])
    speed_quality = st.sidebar.selectbox("Speed/Quality", ["Instant", "Balanced", "Deep"])
    memory = st.sidebar.radio("Memory", ["Stateless", "Session-based", "Persistent"])

    st.title("📝 PromptEase")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"🧑 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **{msg['model']}:** {msg['content']} \n")

    user_input = st.text_area("💡 Enter your idea/keywords:", placeholder="Example: Impact of AI in education")

    if st.button("🚀 Submit"):
        if user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = get_openrouter_response(model, user_input,
                                               task=task, mode=mode, style=style, persona=persona,
                                               depth=depth, format_type=format_type, language=language,
                                               tone=tone, domain=domain, creativity=creativity,
                                               bias_filter=bias_filter, speed_quality=speed_quality,
                                               memory=memory)
            st.session_state.messages.append({"role": "assistant", "model": model, "content": response})
        else:
            st.warning("⚠️ Please enter some text before submitting.")

