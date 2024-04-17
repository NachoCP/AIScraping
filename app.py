import streamlit as st
from src.json_to_pydantic import create_pydantic_model_from_schema, model_to_dict, AllowedTypes
from src.url import extract_html_from_url
from src.llm import configure_chain
import json
from dotenv import load_dotenv
import requests

load_dotenv()

# Don't show the setting sidebar
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "collapsed"

st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state)

# Title of the application
st.title("🤖🌐AI Scraper🌐🤖")
st.markdown("""
*<small>Made with [LangChain](https://python.langchain.com/en/latest/index.html) 🦜⛓️ and a sprinkle of magic dust ✨</small>*

🚀 Get ready to launch your digital adventure! Transform unstructured data from your favorite websites into structured treasure troves 🏴‍☠️. 

Don't just surf the web, dive into it! 🏄‍♂️🌊 Whether you're hunting for golden data nuggets or just curious to see what lies beneath the 'inspect' button,
we've got the tools you need to navigate the digital seas. 🧭💻
            """, unsafe_allow_html=True)

# How it works section
how_it_works = st.expander(label="How it works")
with how_it_works:
    st.write(
        """
        Embark on a data adventure in just a few steps! Here's how you can turn the web's chaos into your own structured symphony 🎼:

1. **Craft Your Model** 📝: Begin by defining your Pydantic model in Table format.
Ensure each attribute is carefully described, weaving the type and description into a spell that reveals what you seek.
2. **Mark the Spot** 🗺️: Next, provide the URL of the uncharted digital lands where your desired data dwells.
3. **Summon the Data** 🧙‍♂️: Hit the magical button to summon the data that matches your model from the depths of the web.
4. **Treasure Awaits** 💎: Watch as your screen fills with the objects that fit your model. But that's not all - you can claim your digital treasure by downloading the information in a JSON file, ready for whatever adventures lie ahead.
        """
    )

def validate_rows(rows):
    return all(row["name"] and row["type"] for row in rows)

if 'rows' not in st.session_state:
    st.session_state['rows'] = [{"name": "", "type": AllowedTypes.string, "description": ""}]

def render_rows():
    for index, row in enumerate(st.session_state['rows']):
        cols = st.columns([3, 3, 3, 0.5])
        
        if index != 0:
            visibility = "hidden"
        else:
            visibility = "visible"
            
        with cols[0]:
            row["name"] = st.text_input("Name", value=row["name"], key=f"name_{index}", label_visibility=visibility)
        with cols[1]:
            row["type"] = st.selectbox("Type", options=[e.value for e in AllowedTypes], index=[e.value for e in AllowedTypes].index(row["type"]), key=f"type_{index}", label_visibility=visibility)
        with cols[2]:
            row["description"] = st.text_input("Description", value=row["description"], key=f"description_{index}", label_visibility=visibility)
        with cols[3]:
            if st.button("❌", key=f"remove_{index}"):
                st.session_state['rows'].pop(index)
                st.rerun()

def add_row():
    st.session_state['rows'].append({"name": "", "type": AllowedTypes.string, "description": ""})

def generate_json():
    dict_data = {}
    for row in st.session_state['rows']:
        dict_data[row["name"]] = {
            "type": row["type"],
            "description": row["description"]
        }
    return dict_data

render_rows()

col1, col2 = st.columns(2)
with col1:
    if st.button('Add Row'):
        add_row()
with col2:
    if st.button("Validate Model"):
        if validate_rows(st.session_state["rows"]):
            try:
                scrape_object = create_pydantic_model_from_schema("ScrapeObject", generate_json())
                st.success("Model created successfully.")
            except Exception as e:
                st.error(f"Error creating model: {e}")
        else:
            st.error("Please fill out 'Name' and 'Type' for all rows before generating JSON.")


# Input for URL
url_input = st.text_input("Enter a URL to scrape:")

if st.button("Generate Pydantic Model and Scrape"):
    if validate_rows(st.session_state["rows"]):
        try:
            scrape_object = create_pydantic_model_from_schema("ScrapeObject", generate_json())
        except Exception as e:
            st.error(f"Error creating model: {e}")
    else:
        st.error("Please fill out 'Name' and 'Type' for all rows before generating JSON.")
    if scrape_object and url_input:
        # Example of dynamically creating a model from JSON schema (simplified)
        try:
            html_text = extract_html_from_url(url_input)
            # Here you would integrate LangChain scraping logic based on the dynamic model and URL
            chain = configure_chain(scrape_object)
            response = chain.invoke(input={
                "html_text": html_text
            })
            json_to_download = json.dumps(model_to_dict(response.objects), indent=4)
    
            # Create a download button and provide the JSON string as the file to download
            st.download_button(
                label="Download Data as JSON",
                data=json_to_download,
                file_name="downloaded_data.json",
                mime="application/json"
            )
            st.json(json_to_download, expanded=False)
            
        except Exception as e:
            st.error(f"Error creating model: {e}")
    else:
        st.warning("Please provide both a JSON schema and a URL.")
