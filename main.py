# Copyright (c) 2025 victor256sd
# All rights reserved.

import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
import re

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Definitive CSS selectors for Streamlit 1.45.1+
st.markdown("""
<style>
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # # Initialize chat history.
    # if "ai_response" not in st.session_state:
    #     st.session_state.ai_response = []
    
    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    MODEL_LIST = ["gpt-4o-mini"] #, "gpt-4.1-nano", "gpt-4.1", "o4-mini"] "gpt-5-nano"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABotUK4eMTSYMWjAo1ace6KlYPR7Q0SrgZXwGayQNrlYPLhN22fQJpHcTGC9gmTU7MDPgSr6y4leLH7pvuvLCVZws_a2McYqtEfSZ7fZVkEL8bITf1T_iI9C-5ZeIEct2v5Af7WWzBBManWT7ApWo68MwfJaPR646D-s3N54Mr-GRcKZ2iT-5WjKaIC-dNOMboQEU7WDJ-6FFY2Ac-vBOpPUBPtW1FKZEgM3hb3JujhfXOP4N9Un-CvPlGiOClJh26RepssP_iFA8gJUgs5dW-xAde-tmkt_TyBovOgIo28FlE-I3FP2aJPAwKGLeOz8bSmglinvcc7jbLWoYBdBqDvVLPnhRpSKnPnfiSvZjl_o8FiMtwfpnw-WAhnW77JjPiCHd4rcTrAYUR1GZqLFFkAp5wrv3abXW9UhVeATS_cgGwi5BQbl9eHe5Q_Vep1_y7fu9jEPQTlXPXBZ4QvISgg0q5WpPaUiERb1Me9kW5ucc9kntgGmDGqMHtRl6SekjH6tdRPAvJ9RY4A2Izvao7bC2_8cZBoFxqgUjtwwIOChmwKwJwHIX_vee5lc5t4Hs8Hh1m9KVXZZoMly9txdf37Uhlxv0nAROBSArAciLnSgZCEWsxO316TuhYsxSUV_QaEd0x2iVCge6c62exvyK4zCf3z1i4YOPvXvpSqRl1aQXiGZ6bvXVly6tqqyrD6W-9jwrYXPJlF-zg8ZH6vqMk514fOk6bpEZ4c0Zj7wFOKRPDTZLZptx_c28d4binc-TxMOc3YtJE8s-lpYcQQb6h49VTIx2Cdkg7WQlyNRsI1GZxGoMcu2ZxoA-m7eYEO5K0ytYDKz7ZgXxyrc_2edoKt-qjWhbkz1lm_Q7LHrLNcg-Ghg3FsBSOjqdQuhJpwwnKlUAngwlwW-YmZZger5OOPRtul0vINnlu4n6H0N5ANhr-Yw3vaKhm5wKSOaVG58vx3cpohuyO9NARP7D1nk60L17bB-dHzCVEJTDNpguSQNfZ8T16f9uM2XhRaGNeGuwhk7pB-evcXFqO1VlEnUaCnJD9Fm9SAgx-MseLUtdrDcNKJQ_1ye_nw6b8MARddOoAepO9w46MhVYEJlFf4eKgI8Dx90SwlA2LZXW8pmC5zYTutj7xXRALhE7LcdFrkyiTgJQDHENz7GOapvnFJPZGD6aR6nid50-Jbp6kDTMxM0tgSWwVUR3hiv1LG1D0R0wdV-SomR40RpheZKiAehaWUUnviIHmzx55FKrrXayeoiZOOunuEZaRaSCPQ-XIa3Z5hk-BY6HdQ-33rkrK4IxWTJ6FcV5aZnMk-qs32IVHEM4-HgdlDv2pWJGzumGawAtborJOm4C7uZygvrRlu2ZcEA-_Yj_WgqrocBnRj80ohRSdrrHCkjly2mlWa2Hq5kGzz0x8RTkeoQ8hqVxe9rQM-TJoNSSf_lfSH9QfiZxNCRDFJgs-aeQmJrX_ynnZH54BSviPxv_iZ4qBpfPOF6DwzvFGRazykev_tsgEpM_OBRrFvo5S2BODYGgOFfEoBFx7BI_aJKw7XN4Lg4JPyrR958ZjSPVfASylmh0Wh1AGgimJ9JBMZYEHLdTIY8fpam99fgV0OKO0WX54L-33EV1vgBGN2Btpjb4zfCSUPDMotYqH8ulBIKYOk_kaajRiqVyl6iIomD3WB8X7brlkoHt9OdlRfynCSPU9vT2M-PFg0m4a5_fRbD6xSncUQxbgzfjdzGF7ghOdLePI4vYNJUpEpLp_n3ZViN9wq5ijFcpjae9SpnM3glPzx-jLFxqkxlkHdp0pxZUn-8bGCqQP_izX_JKEB-A9XnAZdwtoDinSQyS4NcugPB2HGpXA1FycqCZUFJtIS0Km-N_j7D9KkLEWvm0KVL3eGhfHtZIlswBnb1M1tbBjrwOr5drRpTGvp6hJdc11IxdTgssfpMsNdA_9he1qK_QptI7V6NDnGrtW7Wj07Gq2FikwDpptQKweZd_IBIDYB44DOiOszqUl6Fx2kkzukU31kd4ruXlQUEaQwehCW8z-XchUYFQAmq7FzCvGvFnROCgtbsj9Bk8WyWiUXpVmHPefC9aAj_QaZOek7IavksCNS6v-E9hYLfydGbuXU6uVR8t3m8kIQyKv-JvNBLBb1DszYSKhU_q1krfHUPxBwpPgt6JwPqPapgxazNX9RCUxaZphzT9pSoZWGfDCdLSkcQFkhSmxtswmWwT6IJbKWrVbe30-mfZxPr7hK2iAipgXANnmjokcN0ENtyBuLbsquULf3hPcmDom3G6oaeKcLLUNnZuZmpFLQeQd-f1zjAOrLqJIqNm9RnF1uarjSdtiU5_7mHkP2GwjNeSA4ctdL-tG1oJlODeJJCjoeRDziFEr3b06VaBIS6y3iCgFP9-JBPZhyO2BP3Nm7q8GAVsGzLUWUKdMIdWhfZn7hRphtB-SRj-Lt4jMCHYHaZVNTwy6NeO-Qd6ALqdWh4vfmKi4Q7owAvQog7qxBKsSpaGQqT_dl0JPRangAzSxinK8V4VXbBwforabFEueSQnFiLzNTsnves425GP3rrGOq1DsOzS78ux5ShPV3eSQvg1RYHfSA6L2We4cgwD6FVHN-nshLDExLC9pKk9U3sm93Fcxt6Ze4zp_7pMbJuMp4CvjHg5d7MBJxhLfggvVm2YGgEcmsO9Y1Evo1SRyIqc4HOCXk80xP1A9y3eKfbeVC4V4wdmWV8kXkll2aaJIHRfLXXRkkm5HBZdxJFEQRlKIkAVrqtEH3QGHDqXTGr7ZwLbJKUmofzsLUCX4vOYpAiVcHWe60gbl113AiwgvDQuUUggsy4mVp46q5c5exC8EWypjsKBYTWvlQQwZKU15Kjop2qzB8b33VSI2OOjoS14lCZHGzErWId7UmQj9QhmkVaYkU4kq3F_lj-KdjL4UZQsAJfxP6-dPUxlcBBSzCQmpefQa2ko3uFGNoiUPL4i26_7aIpbC9jhb-AWnEo2tKSZmzQ5x5ojPA8H6qv7M33MoCWda0gEB7-GVsTi86qcA_xIcZKLLu4855K--O1UUU5Xnp62dQykNCCO14CDJ0uD9J81-aFLbHjaPjFSDFQQ_40ImJ0jhTXJkSvN_Ue-E4izqk77rR7UUI7jmMtn0X35qc6Nxm2kISu33cX8BIT0Gi6iqI6KJGILnXz2W3hxD55B0kWkNpzoiEqHA0E-R7e7OMEMGN-9sMLLzT-EolbqlA8Wv_M2zuze2oUzjmMgofZsapKmEv7aXSUlXWMDzElQJn_gQwTfUjMa3EMMQdAM8GcLUieI7bOsT8QbIbS8pVvE1vNzduCcb_j7WAhogetKKgvjB0Od1uSB6O0qS0Yh28Vx0r91mBrcVBR46hQcSD9b3WLeCOOPZSa2262c3zXrL35lNph8kzLOs-W-xUQcGoz6_a_2pvS_e2mNjOVfKyYc4e6_94HPVnz9ylcGObKmzWUEy9oPs0cVefMdap6vD350HK4Kta6Ua1oK-wP466PxNc-lCrpVbIodAbWRWNNMPnZ8k-BFZx2ID5TEwdK7g7mo_VoQUZgQGYaP2ol5Ck1OBScgy2rQ4='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="HR Bot", page_icon=":notebook:", layout="wide")
    st.header(":notebook: HR Bot")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
    
    # Create new form to search aitam library vector store.    
    with st.form(key="qa_form", clear_on_submit=False, height=300):
        query = st.text_area("**Ask about HR policies and procedures:**", height="stretch")
        submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question to search HR policies!")
            st.stop()            
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = INSTRUCTION,
                input = query,
                model = model,
                temperature = 0.6,
                # text={
                #     "verbosity": "low"
                # },
                tools = [{
                            "type": "file_search",
                            "vector_store_ids": [VECTOR_STORE_ID],
                }],
                include=["output[*].file_search_call.search_results"]
            )
        # Write response to the answer column.    
        # with answer_col:
        try:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output_text) #output[1].content[0].text)
        except:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)
        st.markdown("#### Response")
        st.markdown(cleaned_response)

        st.markdown("#### Sources")
        # Extract annotations from the response, and print source files.
        annotations = response2.output[1].content[0].annotations
        retrieved_files = set([response2.filename for response2 in annotations])
        file_list_str = ", ".join(retrieved_files)
        st.markdown(f"**File(s):** {file_list_str}")

        # st.session_state.ai_response = cleaned_response
        # Write files used to generate the answer.
        # with sources_col:
        #     st.markdown("#### Sources")
        #     # Extract annotations from the response, and print source files.
        #     annotations = response2.output[1].content[0].annotations
        #     retrieved_files = set([response2.filename for response2 in annotations])
        #     file_list_str = ", ".join(retrieved_files)
        #     st.markdown(f"**File(s):** {file_list_str}")

            # st.markdown("#### Token Usage")
            # input_tokens = response2.usage.input_tokens
            # output_tokens = response2.usage.output_tokens
            # total_tokens = input_tokens + output_tokens
            # input_tokens_str = f"{input_tokens:,}"
            # output_tokens_str = f"{output_tokens:,}"
            # total_tokens_str = f"{total_tokens:,}"

            # st.markdown(
            #     f"""
            #     <p style="margin-bottom:0;">Input Tokens: {input_tokens_str}</p>
            #     <p style="margin-bottom:0;">Output Tokens: {output_tokens_str}</p>
            #     """,
            #     unsafe_allow_html=True
            # )
            # st.markdown(f"Total Tokens: {total_tokens_str}")

            # if model == "gpt-4.1-nano":
            #     input_token_cost = .1/1000000
            #     output_token_cost = .4/1000000
            # elif model == "gpt-4o-mini":
            #     input_token_cost = .15/1000000
            #     output_token_cost = .6/1000000
            # elif model == "gpt-4.1":
            #     input_token_cost = 2.00/1000000
            #     output_token_cost = 8.00/1000000
            # elif model == "o4-mini":
            #     input_token_cost = 1.10/1000000
            #     output_token_cost = 4.40/1000000

            # cost = input_tokens*input_token_cost + output_tokens*output_token_cost
            # formatted_cost = "${:,.4f}".format(cost)
            
            # st.markdown(f"**Total Cost:** {formatted_cost}")

    # elif not submit:
    #         st.markdown("#### Response")
    #         st.markdown(st.session_state.ai_response)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
