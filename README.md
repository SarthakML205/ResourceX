# ResourceX - Assistant for Analyzing and Storing Resources

## Overview
ResourceX leverages modern LLM and API integrations to analyze content from various platforms (LinkedIn, Instagram, arXiv, etc.) and stores the processed data into Google Sheets. The project features an interactive Streamlit web app and supports browser-based usage.

## Project Structure
- **final_main.py**: Main application integrating API calls, LLM processing, and Google Sheets.
- **browser-use/main.py**: Alternative module for browser-based operations.
- **t.txt**: File for experimental snippets and logs.
- **test.ipynb**: Jupyter Notebook for testing and experimentation.
- **resourcex-452811-52e509439f34.json**: Google service account credentials.
- **.env**: Environment configuration (API keys, credentials path).
- **.gitignore**: Specifies files and directories to ignore in version control.

## Setup Instructions
1. **Install Dependencies**  
   Run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Google API Credentials**  
   - For OAuth, follow the instructions in [Google Cloud Console](https://console.cloud.google.com/).
   - For Service Accounts, set `GOOGLE_CREDS_PATH` in your `.env` file to the service account JSON file.

3. **Environment Variables**  
   Ensure your `.env` file includes:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_CREDS_PATH=path_to_google_creds.json
   GOOGLE_SPREADSHEET_NAME=ResourceX_Data
   ```

4. **Run the Application**  
   Launch the Streamlit app:
   ```bash
   streamlit run final_main.py
   ```
   Or run directly:
   ```bash
   python final_main.py
   ```

5. **Interactive Testing**  
   Open `test.ipynb` in Jupyter Notebook for experiments and visualizations.

## Contribution
Feel free to fork the repository and submit pull requests. Any improvements or bug fixes are welcome.

## License
This project is licensed under the MIT License.
