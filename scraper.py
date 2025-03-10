import requests
from bs4 import BeautifulSoup

def scrape_linkedin_profile(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    profile_data = {}
    
    # Example: Extracting the profile name
    name_tag = soup.find('h1', {'class': 'top-card-layout__title'})
    if name_tag:
        profile_data['name'] = name_tag.get_text(strip=True)
    
    # Add more fields to scrape as needed
    
    return profile_data

if __name__ == "__main__":
    linkedin_url = 'www.linkedin.com/in/sarthak-pandey-28oct?'
    profile_data = scrape_linkedin_profile(linkedin_url)
    if profile_data:
        print(profile_data)