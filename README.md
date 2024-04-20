# 🤖🌐 AI Scraper

Welcome to AI Scraper, a powerful tool built with Streamlit and the LangChain library, designed to transform unstructured web data into structured, actionable insights. This application makes it easy to scrape data from websites and automatically generate Pydantic models for structured data extraction.

Check this [article](article/article.md), If you wanted to know more about this project.

## Features

- **Model Definition:** Dynamically create Pydantic models based on user-defined schemas directly from the UI.
- **Data Extraction:** Enter a URL and scrape data according to the defined Pydantic model.
- **Data Download:** Export the scraped data in JSON format for ease of use in further applications.

## How It Works

AI Scraper operates in two main stages:

1. **Model Creation:**
   - Define your data model by specifying attributes such as name, type, and description.
   - Validate the model to ensure all fields are correctly filled out.
   - Automatically generate a Pydantic model to be used in the scraping process.

2. **Data Scraping:**
   - Enter the URL of the website from which you want to scrape data.
   - Execute the scraping process, which uses the previously defined Pydantic model to parse and structure the HTML content.
   - Download the structured data as a JSON file or view it directly within the app.

### How to Use

#### Craft Your Model
Start by defining your data model in the provided table format. Ensure each attribute is carefully described, specifying the type and a brief description.

#### Mark the Spot
Input the URL of the webpage you wish to scrape. The application supports various content types as long as they can be parsed into HTML.

#### Summon the Data
Click the 'Generate Pydantic Model and Scrape' button to start the extraction process. The data matching your model will be retrieved and displayed.

#### Treasure Awaits
Download the structured data in JSON format, or explore it directly within the application.

## Setup and Installation

1. Clone the Repository:
```bash
git clone https://yourrepositorylink.git
```

2. Create a venv and install all the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. You will need the following .env file
```bash
# OPENAI Key
OPENAI_API_KEY=<OPENAI_API_KEY>
```
4. To init the application run
   
```bash
streamlit run app.py
```

## Dependencies

Streamlit
LangChain
Pydantic
Requests
dotenv
json

## Contributing
Feel free to fork the repository, make changes, and submit pull requests. If you encounter any issues or have suggestions for improvement, please submit an issue.


## Acknowledgments

LangChain Library: For providing the tools to integrate AI capabilities seamlessly.
Streamlit: For making it possible to build interactive web applications quickly and easily.