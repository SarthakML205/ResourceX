from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Controller
from pydantic import BaseModel
from typing import Optional, List
from pydantic import SecretStr
import os
import json
import asyncio
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
import google_sheets

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Custom output class
class Output(BaseModel):
    Post_Link : str
    Title : str
    Description : str
    resoure_type : Optional[List[str]] = None
    platform : str
    Resource_link : Optional[List[str]] = None
    Resoure_description : Optional[List[str]] = None
    Account : str

class LLM_Agent:
    def __init__(self):
        pass

    async def get_agent(self, link):
        task = f''' 
        you are going to serve me as a assitant that is going to help me manage the information about the resource i look for.
        i will provide you a {link} to a post, from that you need to extract the following information:
        1. Link of the post
        2. Title of the post
        3. Description of the post
        4. Type of resource
        5. Platform
        6. Link of the resource
        7. Description of the resource
        8. Account
        
        there can be multiple resources mentioned in the post, no need to explore the link of all of them just get link, description, resource type for all the resources mentioned.  do not click on the link of any resource mentioned in the post.
        
        Login instructions:
        1. for general login use this google account: sarthakpandey2810@gmail.com password: sarthak@2810

        2. if it is Linkedin account login in using this account: sarthakpandey2810@gmail.com password: Linkedin@2810

        3. if it is a instagram login in using this account: sarthak_4602 password: sarthak@4602

        4. if given a link for a research paper, in resource try to get its pdf link.

        do only this instruction and provide me the information i asked for.

        '''

        llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))
        controller = Controller(output_model=Output)
        agent = Agent(task=task, llm=llm, controller=controller)
        return agent



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
            headers = ["Post_Link", "Title", "Description", "resoure_type", 
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
            ' , '.join(data_dict.get('resoure_type', [])),
            data_dict.get('platform', ''),
            ' , '.join(data_dict.get('Resource_link', [])),
            ' , '.join(
                data_dict.get('Resoure_description', [])
            ) if 'Resoure_description' in data_dict else '',
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

async def main():
    # Ensure Google authentication is set up
    if not google_sheets.main():
        print("Failed to authenticate with Google Sheets. Exiting.")
        return
    
    # Initialize the model
    X = LLM_Agent()
    
    # You can replace this URL with any URL you want to process
    url = "https://www.linkedin.com/feed/update/urn:li:activity:7303259960421847040/"
    agent = await X.get_agent(url)

    result = await agent.run()
    print(result)
    
    # Extract the data from the agent output
    data_dict = None
    try:
        # Accessing the done dictionary from all_model_outputs list
        data_dict = result.action_results()
        last_extracted_content = next(
    (result.extracted_content for result in reversed(data_dict) if result.extracted_content), 
    None)
        data_dict = json.loads(last_extracted_content)
        await write_to_sheet(data_dict)

        
            
    except (AttributeError, IndexError) as e:
        print(f"Error extracting data from agent output: {e}")
        print("Agent output structure:", result)
    
if __name__ == '__main__':
    asyncio.run(main())
