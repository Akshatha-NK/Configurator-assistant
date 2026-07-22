"""import streamlit as st
from google import genai
from google.genai import types

Client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

configurator_context = """
#You are Senior Oracle Configurator technical expert with deep hands on experienceAssistant.
#Topics you cover:Model structure,CZ schema, Oracle Configurator rules,
#BOM structures, UI masters, effectivity and model building, and you know all Oracle configurator guides available.
#Always give detailed, technical if user asks otherwise give.
#short or summarized answers.
#Prompt users if they want to see examples if they say yes then only provide."""
"""
"""

#st.title("Oracle Configurator Assistant")

#if "messages" not in st.session_state:
   # st.session_state.messages=[]

#for msg in st.session_state.messages:
   # st.chat_message(msg["role"]).write(msg["content"])

#if question:= st.chat_input("Ask a configurator question...."):
    #st.session_state.messages.append({"role":"user","content": question})
   # st.chat_message("user").write(question)

   # response = Client.models.generate_content(
        #model = "gemini-2.5-flash",
       # contents=question,
        #config = types.GenerateContentConfig(system_instruction=configurator_context,
                                           #  temperature=0.3,
                                        #     max_output_tokens=5000)
 #   )

    #answer = response.text
   # st.session_state.messages.append({"role":"assistant","content":answer})
    #st.chat_message("assistant").write(answer)
    

import streamlit as st
from google import genai
from google.genai import types
import pypdf
import os

# Define the file path for optional permanent storage
SAVED_REPORT_PATH = "model_context.txt"

# Initialize the Gemini Client
Client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

BASE_CONTEXT = """
You are a Senior Oracle Configurator Expert.
You know everything about oracle configurator developer and you have to search all oracle documentations online including all standard table details.
if any documentation upgrades look for updated version of that before answering.

When evaluating duplicate rules:

- Extract every rule from the supplied report.
- Compare each rule against all other rules.
- Identify:
  - Exact duplicates
  - Near duplicates
  - Rules with identical logic but different names
- Explain why they are duplicates.
- Never stop after finding one duplicate.
- Continue until all rules have been analyzed.
If the result exceeds the allowed response length:
- Continue from where you stopped.
- Number every finding.
- Do not summarize or omit results.
"""

st.title("Oracle Configurator Assistant")

# --- OPTIONAL PERSISTENT FILE STORAGE LOGIC ---
if "report_text" not in st.session_state:
    if os.path.exists(SAVED_REPORT_PATH):
        with open(SAVED_REPORT_PATH, "r", encoding="utf-8") as f:
            st.session_state.report_text = f.read()
    else:
        st.session_state.report_text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar UI
st.sidebar.title("Model Knowledge Base")

if st.session_state.report_text:
    st.sidebar.success("✅ Custom Model Report Active")
    st.sidebar.caption(f"Context size: {len(st.session_state.report_text)} characters")
    
    if st.sidebar.button("Remove Custom Model"):
        if os.path.exists(SAVED_REPORT_PATH):
            os.remove(SAVED_REPORT_PATH)
        st.session_state.report_text = ""
        st.rerun()
else:
    uploaded_file = st.sidebar.file_uploader(
        "Optional: Upload a Model Report to provide specific context", 
        type=["pdf", "txt"]
    )
    
    if uploaded_file is not None:
        with st.sidebar.spinner("Processing report..."):
            extracted_text = ""
            if uploaded_file.type == "application/pdf":
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
            elif uploaded_file.type == "text/plain":
                extracted_text = str(uploaded_file.read(), "utf-8")
            
            with open(SAVED_REPORT_PATH, "w", encoding="utf-8") as f:
                f.write(extracted_text)
                
            st.session_state.report_text = extracted_text
            st.rerun()

# --- NEW FEATURE: INTERACTIVE SAMPLE QUESTIONS ---
# Show helper prompts depending on whether a report is loaded or not
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Sample Questions to Try:**")

if st.session_state.report_text:
    samples = [
        "Summarize the BOM structure found in this report.",
        "Are there any specific configuration rules listed here?",
        "What are the main components inside this model?"
    ]
else:
    samples = [
        "Explain the difference between BOM Display Dependent and Independent rules.",
        "How does Oracle Configurator handle effective dating (Effectivity)?",
        "What is the purpose of the CZ_EXPRESSIONS table in the CZ schema?"
    ]

# Create tappable sample buttons in the sidebar
clicked_sample = None
for sample in samples:
    if st.sidebar.button(sample, use_container_width=True):
        clicked_sample = sample

# Display previous messages with knowledge-source indicators
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # If it's an assistant message with an source tag, display it cleanly
        if msg["role"] == "assistant" and "source" in msg:
            st.caption(msg["source"])

# Determine final input (either text input or sidebar click)
question = st.chat_input("Ask a configurator question....")
if clicked_sample:
    question = clicked_sample

# Handle Chat Processing
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

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

    # Inject stored file text dynamically ONLY if it exists
    dynamic_context = BASE_CONTEXT
    if st.session_state.report_text:
        dynamic_context += f"\n\n[CRITICAL REFERENTIAL CONTEXT]\nUse this specific structural configuration text to address queries accurately:\n### START OF REPORT ###\n{st.session_state.report_text}\n### END OF REPORT ###"
        source_label = "🔍 Source: Uploaded Model Report Context"
    else:
        dynamic_context += "\n\nNo specific model report has been uploaded. Answer using general Oracle Configurator best practices and guides."
        source_label = "📚 Source: General Oracle Configurator Core Knowledge"

    # Call Gemini API
    with st.spinner("Thinking..."):
        response = Client.models.generate_content(
            model="gemini-2.5-flash",
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=dynamic_context,
                temperature=0.3,
                max_output_tokens=16384
            )
        )

    answer = response.text
    
    # Save answer and its source label to state
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer, 
        "source": source_label
    })
    
    # Display the final answer with its source tag
    with st.chat_message("assistant"):
        st.write(answer)
        st.caption(source_label)
   
    # Force a rerun if a sidebar button was used to clean up the widget state
    if clicked_sample:
        st.rerun()
