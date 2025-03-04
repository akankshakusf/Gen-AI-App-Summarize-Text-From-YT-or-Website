## import packages and libraries 
import os 
import streamlit as st
import validators
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.documents import Document  # Import to fix YouTube transcript issue
import certifi  # Import certifi

#this is helper code for youtube transcript extraction
from youtube_transcript_helper import get_youtube_transcript

## Set SSL certificate file path using certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

###---------------###  Setting up the Streamlit app ###---------------###

st.set_page_config(page_title="Langchain: Summarize Text from YT or Website", page_icon="🦜") 
st.title("🦜 LangChain: Summarize Text From YT or Website") 
st.subheader("Summarize URL")

## Get the Groq API key and URL (YT or Website) to be summarized

# Read API key from Streamlit secrets

groq_api_key = st.secrets["GROQ_API_KEY"] #comment this when running on VS code

with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", value=groq_api_key, type="password")  # api key added
    #groq_api_key = st.text_input("Groq API Key", value="", type="password")  #uncomment this when running on VS code

generic_url = st.text_input("URL", label_visibility="collapsed")  # Input for URL

#------------------ LLM Handling START ------------------# 

## Instantiate the LLM Model using Groq API
llm = ChatGroq(model="Gemma2-9b-it", groq_api_key=groq_api_key)

# Structured prompt for LLM
prompt_template = """
Summarize the following content in **clear, well-structured paragraphs**.
- Avoid repetitive phrases.
- Ensure key insights are included without unnecessary details.
- Structure the summary in a **logical** and **coherent** manner.

Content:
{text}

Provide a structured summary below:
"""


prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

#------------------ LLM Handling END ------------------# 

if st.button("Summarize the Context from YT or Website"):

    ## Validate input
    if not groq_api_key.strip() or not generic_url.strip():
        st.error("Please provide the API key and a URL to summarize.")
    elif not validators.url(generic_url):
        st.error("Invalid URL. Please provide a valid YouTube or Website URL.")

    else:
        try:
            with st.spinner("Waiting..."):
                docs = []  # Initialize empty list for storing extracted content
                
                               
                ## Loading the website data (YouTube or Others)
                if "youtube.com" in generic_url :
                    st.write("Loading YouTube Video Summary...")   
                                                           
                    # Get video transcript
                    transcript_text = get_youtube_transcript(generic_url)

                    if transcript_text.startswith("Error"):
                        st.error("Could not fetch transcript. The video may not have subtitles.")
                    else:
                        docs = [Document(page_content=transcript_text)]
                        st.write("Summary Extracted Successfully!")                 

                else:
                    st.write("Loading website content...")
                    loader = UnstructuredURLLoader(urls=[generic_url], ssl_verify=False,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                    )
                    docs = loader.load()
                    st.write("Summary Content Successfully!")  # Debugging step

                ## Process with LLM if content was extracted
                if docs:
                    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                    output_summary = chain.invoke(docs)["output_text"]  # Corrected way to get summary
                    st.success(output_summary)  # Display the summary
                else:
                    st.error("No valid content extracted for summarization. Please check the input URL.")

        except Exception as e:
            st.exception(f"Exception:{e}")
