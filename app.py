import streamlit as st    
import requests

if "messages" not in st.session_state:
    st.session_state.messages = []

OPENROUTER_API_KEY = "OPENROUTER_API_KEY"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_openrouter_response(model, prompt, **kwargs):
    """
    Sends a prompt + extra parameters to OpenRouter API and returns response
    """
    m_model = model
    try:
        if model == "ChatGPT":
            model = kwargs.get("model", "openai/gpt-oss-20b:free")
        elif model == "Gemini":
            model = kwargs.get("model", "google/gemma-3-27b-it:free")
        elif model == "mistral":
            model = kwargs.get("model", "mistralai/mistral-small-3.2-24b-instruct:free")
        elif model == "LLaMA":
            model = kwargs.get("model", "meta/meta-llama/llama-4-maverick:free")
        elif model == "DeepSeek":
            model = kwargs.get("model", "deepseek/deepseek-chat-v3-0324:free")
        elif model == "nvidia":
            model = kwargs.get("model", "nvidia/llama-3.1-nemotron-ultra-253b-v1:free")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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

        return f"[OpenRouter:{m_model}] Task={kwargs.get('task')} | Tone={kwargs.get('tone')} | Response: {message}"

    except Exception as e:
        return f"[OpenRouter] Error: {str(e)}"

    
def get_claude_response(prompt, **kwargs):
    return f"[Claude] Style={kwargs.get('style')} | Mode={kwargs.get('mode')} | Response to: {prompt}"

def get_llama_response(prompt, **kwargs):
    return f"[LLaMA] Domain={kwargs.get('domain')} | Creativity={kwargs.get('creativity')} | Response to: {prompt}"


st.set_page_config(page_title="AI Middleware Advanced", layout="wide")

st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background: #f7f7f7;
    }
    .css-1d391kg, .css-1cpxqw2, .stSelectbox, .stSlider, .stCheckbox {
        font-size: 13px !important;
    }
    .stSelectbox label, .stSlider label, .stRadio label {
        font-size: 13px !important;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Parameters")

model = st.sidebar.selectbox("Models", ["ChatGPT", "Gemini", "mistral", "LLaMA", "DeepSeek", "nvidia"])
task = st.sidebar.selectbox("Tasks", ["Summarize", "Translate", "Explain", "Solve", "Tutor", "Generate code", "Research mode"])
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

st.sidebar.markdown("### Extras")
extra_references = st.sidebar.checkbox("References")
extra_highlights = st.sidebar.checkbox("Key Highlights")
extra_examples = st.sidebar.checkbox("Examples")

memory = st.sidebar.radio("Memory", ["Stateless", "Session-based", "Persistent"])

params = {
    "task": task,
    "mode": mode,
    "style": style,
    "persona": persona,
    "depth": depth,
    "format_type": format_type,
    "language": language,
    "tone": tone,
    "domain": domain,
    "creativity": creativity,
    "bias_filter": bias_filter,
    "speed_quality": speed_quality,
    "references": extra_references,
    "highlights": extra_highlights,
    "examples": extra_examples,
    "memory": memory
}

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

        if model:
            response = get_openrouter_response(model,user_input, **params)
        else:
            response = "⚠️ Model not implemented"

        st.session_state.messages.append({"role": "assistant", "model": model, "content": response})


    else:
        st.warning("⚠️ Please enter some text before submitting.")