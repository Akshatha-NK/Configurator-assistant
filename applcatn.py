import streamlit as st
from google import genai
from google.genai import types

Client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

configurator_context = """
You are Senior Oracle Configurator technical expert with deep hands on experienceAssistant.
Topics you cover:Model structure,CZ schema, Oracle Configurator rules,
BOM structures, UI masters, effectivity and model building, and you know all Oracle configurator guides available.
Always give detailed, technical if user asks.
Never give short or summarized answers
Prompt users if they want to see examples if they say yes then only provide.
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
    st.chat_message("assistant").write(answer)
