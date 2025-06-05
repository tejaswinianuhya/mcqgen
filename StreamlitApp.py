import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain

load_dotenv()

with open('/config/workspace/Response.json', 'r') as file:
    response_json = json.load(file)

st.title("MCQ Generator App")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or Text file", type=["pdf", "txt"])
    mcq_count = st.number_input("Number of MCQs to generate", min_value=3, max_value=50)
    subject = st.text_input("Subject", max_chars= 20)
    tone = st.text_input("COmplexity Level of Questions", max_chars=20, placeholder = "Simple")
    button = st.form_submit_button("Generate MCQs")

if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("Processing..."):
        try:
            text = read_file(uploaded_file)
            logging.info("File read successfully")
            
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    {
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(response_json)
                    }
                )
            
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error(f"An error occurred: {e}")

        else:
            print(f"Total Tokens Used: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost: ${cb.total_cost:.6f}")
            if isinstance(response, dict):
                quiz = response.get("quiz", None)
                
                if quiz is not None:
                    table_data = get_table_data(quiz)
                    if table_data:
                        df = pd.DataFrame(table_data)
                        df.index += 1
                        st.table(df)
                        st.text_area(label = "Review", value=response.get("review", ""))
                    else:
                        st.error("Failed to extract quiz data.")

            else:
                st.write(response)