from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import List

def configure_chain(DynamicObjectModel: BaseModel):
    
    class ObjectsToScrape(BaseModel):
        objects: List[DynamicObjectModel]

    llm = ChatOpenAI(temperature=0)
    output_parser = PydanticOutputParser(pydantic_object = ObjectsToScrape)

    prompt_template = """
    You are an expert making web scrapping and analyzing HTML raw code.
    If there is no explicit information don't make any assumption.
    Extract all objects that matched the instructions from the following html
    {html_text}
    Provide them in a list, also if there is a next page link remember to add it to the object.
    Please, follow carefulling the following instructions.
    If there is a value that it is not possible to scrape put a "" or 0 depending on the data type
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["html_text"],
        partial_variables={"format_instructions": output_parser.get_format_instructions}
    )

    chain = prompt | llm | output_parser
    return chain
