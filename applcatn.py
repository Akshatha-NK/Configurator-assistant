import streamlit as st
from google import genai
from google.genai import types

Client = genai.Client(api_key="AIzaSyDZCIYEOjoqT1EvFUsRJEssiYd6gDNJbxs")

configurator_context = """
You are Oracle Configurator expert Assistant.
Answer questions about Oracle Configurator rules,
BOM structures, UI masters, effectivity and model building.
Be specific and technical.
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
                                             max_output_tokens=1024)
    )

    answer = response.text
    st.session_state.messages.append({"role":"assistant","content":answer})
    st.chat_message("assistant").write(answer)
