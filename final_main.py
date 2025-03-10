import requests
import os
import json
import asyncio
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, validator
from typing import Optional, List
from dotenv import load_dotenv
from groq import Groq
from googleapiclient.errors import HttpError
from langchain_community.document_loaders import WebBaseLoader
import google_sheets
import arxiv 
import re 
import streamlit as st
import asyncio
import json
import google_sheets  # ensure this is imported to access sheet_id
import streamlit.components.v1 as components


#Custom output class
#Custom output class
class Output(BaseModel):
    Post_Link : Optional[str]
    Title : Optional[str] 
    Description : Optional[str] 
    resource_type : Optional[List[str]] = None
    platform : Optional[str]  
    Resource_link : Optional[List[str]] = None
    Resource_description : Optional[List[str]] = None
    Account : Optional[str] = None

    @validator('resource_type', pre=True, always=True)
    def validate_resource_type(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    @validator('Resource_link', pre=True, always=True)
    def validate_resource_link(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    @validator('Resource_description', pre=True, always=True)
    def validate_resource_description(cls, v):
        if isinstance(v, str):
            return [v]
        return v



#functions list.
def get_linkedin_post(url_link):
    url = "https://linkedin-api8.p.rapidapi.com/get-post"

    querystring = {"url": url_link}

    headers = {
        "x-rapidapi-key": "61f38c7348msh0f0b1448d4616fep1e5c55jsn9e6131a31ffb",
        "x-rapidapi-host": "linkedin-api8.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    return response.json()

def get_insta(url_link):
    url = "https://social-media-video-downloader.p.rapidapi.com/smvd/get/instagram"

    querystring = {"url": url_link}

    headers = {
	"x-rapidapi-key": "61f38c7348msh0f0b1448d4616fep1e5c55jsn9e6131a31ffb",
	"x-rapidapi-host": "social-media-video-downloader.p.rapidapi.com"
}

    response = requests.get(url, headers=headers, params=querystring)

    print("Response generated")

    return response.json()


def get_arxiv(url_link):

    client = arxiv.Client()

    pattern = r'\d+\.\d+'
    match = re.search(pattern, url_link)
    if match:
        id = match.group()
        search_by_id = arxiv.Search(id_list=[id])
        results = client.results(search_by_id)
    
    else:
        Print("Invalid URL")

    json_result = { 'Title' : first_result.title, 'Authors' : first_result.authors, 'Abstract' : first_result.summary, 'url' : [first_result.pdf_url, first_result.links], 'categories' : first_result.categories } 

    return json_result

def get_using_link(url_link): 

    loader = WebBaseLoader(url_link)

    docs = loader.load()

    return docs[0].metadata

def generate_response(context):
    if not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = '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'

    llm = init_chat_model("deepseek-r1-distill-llama-70b", model_provider="groq")

    structured_llm = llm.with_structured_output(Output)

    response = structured_llm.invoke(f"you are serving me as an assistant, whose task is to Analyze the content : {context}, and provide me result in provided format and keep the relevant information only")

    return response

async def write_to_sheet(data_dict):
    """Write the LLM agent results to Google Sheets with proper headers"""
    try:
        # Get the sheet service using our utility function
        sheet = google_sheets.get_sheets_service()
        print("Successfully got Google Sheets service")
        
        # Check if sheet already has data
        result = sheet.values().get(
            spreadsheetId=google_sheets.sheet_id,
            range='Sheet1'
        ).execute()
        values = result.get('values', [])
        
        # If sheet is empty or has no headers, add them
        if not values:
            # Define headers based on Output model fields
            headers = ["Post_Link", "Title", "Description", "resource_type", 
                      "platform", "Resource_link", "Resource_Description", "Account"]
            
            sheet.values().update(
                spreadsheetId=google_sheets.sheet_id,
                range='Sheet1!A1',
                valueInputOption='USER_ENTERED',
                body={'values': [headers]}
            ).execute()
            print("Added headers to sheet")
        
        # Prepare data row from dictionary
        row_data = [
            data_dict.get('Post_Link', ''),
            data_dict.get('Title', ''),
            data_dict.get('Description', ''),
            ', '.join([str(item) for item in (data_dict.get('resource_type') if isinstance(data_dict.get('resource_type'), list) else [data_dict.get('resource_type')]) if item is not None]),
            data_dict.get('platform', ''),
            ', '.join([str(item) for item in (data_dict.get('Resource_link') if isinstance(data_dict.get('Resource_link'), list) else [data_dict.get('Resource_link')]) if item is not None]),
            ', '.join([str(item) for item in (data_dict.get('Resource_description') if isinstance(data_dict.get('Resource_description'), list) else [data_dict.get('Resource_description')]) if item is not None]),
            data_dict.get('Account', '')
        ]
        
        print("Appending data to sheet...")
        # Append data to the next available row
        result = sheet.values().append(
            spreadsheetId=google_sheets.sheet_id,
            range='Sheet1',
            valueInputOption='USER_ENTERED',
            body={'values': [row_data]}
        ).execute()
        
        print(f"{result.get('updates').get('updatedCells')} cells updated.")
        sheet_url = f"https://docs.google.com/spreadsheets/d/{google_sheets.sheet_id}/edit"
        print(f"View your sheet at: {sheet_url}")
        return True
        
    except HttpError as err:
        print(f"An error occurred with the API: {err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    st.title("ResourceX - Assistant to Analyze and Store Resources")
    st.write("This app helps you analyze and store resources from various platforms.")
    link = st.text_input("Enter URL")
    resource_option = st.selectbox("Select resource type", ["linkedin", "Insta", "arxiv", "default"])

    if st.button("Submit"):
        if not link:
            st.error("Please enter a link.")
        else:
            st.info("Processing input...")
            # Call the appropriate function based on selection.
            if resource_option == "linkedin":
                result = get_linkedin_post(link)
            elif resource_option == "Insta":
                result = get_insta(link)
            elif resource_option == "arxiv":
                result = get_arxiv(link)
            else:
                result = get_using_link(link)
            
            # Convert result to string context
            context = json.dumps(result, indent=2) if not isinstance(result, str) else result
            st.write("API Result:", context)
            
            # Generate response using LLM
            response = generate_response(context)
            st.write("Generated Response:", response)
            
            # Convert response to dictionary
            response_dict = response.dict()
            
            # Save the generated response using async call
            sheet_written = asyncio.run(write_to_sheet(response_dict))
            if sheet_written:
                st.success("Data saved to Google Sheets successfully.")
            else:
                st.error("Failed to save data to Google Sheets.")
            
            # Create and display the sheet link
            sheet_url = f"https://docs.google.com/spreadsheets/d/{google_sheets.sheet_id}/edit"
            st.write("View your sheet:", sheet_url)
            # Embed the sheet using an iframe
            components.iframe(sheet_url, height=600, scrolling=True)

if __name__ == "__main__":
    main()