"""import streamlit as st
from google import genai
from google.genai import types

Client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

configurator_context = """
"""You are Senior Oracle Configurator technical expert with deep hands on experienceAssistant.
Topics you cover:Model structure,CZ schema, Oracle Configurator rules,
BOM structures, UI masters, effectivity and model building, and you know all Oracle configurator guides available.
Always give detailed, technical if user asks otherwise give.
short or summarized answers.
Prompt users if they want to see examples if they say yes then only provide."""
"""

st.title("Oracle Configurator Assistant")

if "messages" not in st.session_state:
    st.session_state.messages=[]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question:= st.chat_input("Ask a configurator question...."):
    st.session_state.messages.append({"role":"user","content": question})
    st.chat_message("user").write(question)

    response = Client.models.generate_content(
        model = "gemini-2.5-flash",
        contents=question,
        config = types.GenerateContentConfig(system_instruction=configurator_context,
                                             temperature=0.3,
                                             max_output_tokens=5000)
    )

    answer = response.text
    st.session_state.messages.append({"role":"assistant","content":answer})
    st.chat_message("assistant").write(answer)"""

import streamlit as st
from google import genai
from google.genai import types
import pypdf
import os

# Define a permanent storage path on your local machine/server
SAVED_REPORT_PATH = "model_context.txt"

# Initialize the Gemini Client
Client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

BASE_CONTEXT = """
You are Senior Oracle Configurator technical expert with deep hands on experienceAssistant.
Topics you cover:Model structure,CZ schema, Oracle Configurator rules,
BOM structures, UI masters, effectivity and model building, and you know all Oracle configurator guides available.
Always give detailed, technical if user asks otherwise give.
short or summarized answers.
Prompt users if they want to see examples if they say yes then only provide.
"""

st.title("Oracle Configurator Assistant")

# --- PERSISTENT FILE STORAGE LOGIC ---
# Check if a saved report already exists on disk when the app runs
if "report_text" not in st.session_state:
    if os.path.exists(SAVED_REPORT_PATH):
        with open(SAVED_REPORT_PATH, "r", encoding="utf-8") as f:
            st.session_state.report_text = f.read()
    else:
        st.session_state.report_text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar UI
st.sidebar.title("Model Memory Management")

# Display current status of the permanent memory
if st.session_state.report_text:
    st.sidebar.success("✅ Permanent Model Report Loaded!")
    st.sidebar.caption(f"Memory size: {len(st.session_state.report_text)} characters")
    
    # Button to let you overwrite or delete the current saved report
    if st.sidebar.button("Clear Saved Model Memory"):
        if os.path.exists(SAVED_REPORT_PATH):
            os.remove(SAVED_REPORT_PATH)
        st.session_state.report_text = ""
        st.rerun()
else:
    st.sidebar.warning("⚠️ No model report saved in memory.")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a report to save permanently", 
        type=["pdf", "txt"]
    )
    
    # Process and permanently save the file if uploaded
    if uploaded_file is not None:
        with st.sidebar.spinner("Saving report to permanent memory..."):
            extracted_text = ""
            if uploaded_file.type == "application/pdf":
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
            elif uploaded_file.type == "text/plain":
                extracted_text = str(uploaded_file.read(), "utf-8")
            
            # Save to disk so it persists across restarts
            with open(SAVED_REPORT_PATH, "w", encoding="utf-8") as f:
                f.write(extracted_text)
                
            st.session_state.report_text = extracted_text
            st.sidebar.success("Saved successfully!")
            st.rerun()

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle Chat Input
if question := st.chat_input("Ask a configurator question...."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    # Format history for Gemini
    formatted_contents = []
    for msg in st.session_state.messages:
        role = "model" if msg["role"] == "assistant" else "user"
        formatted_contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Inject stored file text dynamically
    dynamic_context = BASE_CONTEXT
    if st.session_state.report_text:
        dynamic_context += f"\n\n[CRITICAL REFERENTIAL CONTEXT]\nUse this specific structural configuration text to address queries accurately:\n### START OF REPORT ###\n{st.session_state.report_text}\n### END OF REPORT ###"

    # Call Gemini API
    response = Client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted_contents,
        config=types.GenerateContentConfig(
            system_instruction=dynamic_context,
            temperature=0.3,
            max_output_tokens=5000
        )
    )

    answer = response.text
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

