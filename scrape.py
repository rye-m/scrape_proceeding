import requests
from bs4 import BeautifulSoup
import csv
import time
import cloudscraper  # This is a specialized library for bypassing Cloudflare
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random

def scrape_with_cloudscraper():
    """Attempt to scrape using cloudscraper library"""
    print("Attempting to scrape with cloudscraper...")
    url = "https://dl.acm.org/doi/proceedings/10.1145/3706598"
    
    # Create a scraper instance
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        },
        delay=10  # Wait 10 seconds between requests
    )
    
    try:
        # Set proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://dl.acm.org/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Get the page
        response = scraper.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"Successfully retrieved page with cloudscraper: Status code {response.status_code}")
            return response.text
        else:
            print(f"Failed to retrieve page with cloudscraper: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error with cloudscraper: {str(e)}")
        return None

def scrape_with_selenium():
    """Use Selenium to scrape the page, which can bypass most protections"""
    print("Attempting to scrape with Selenium...")
    url = "https://dl.acm.org/doi/proceedings/10.1145/3706598"
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize the driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for Cloudflare to resolve (if present)
        time.sleep(10)
        
        # Get the page source
        page_source = driver.page_source
        
        # Close the driver
        driver.quit()
        
        print("Successfully retrieved page with Selenium")
        return page_source
    except Exception as e:
        print(f"Error with Selenium: {str(e)}")
        return None

def parse_and_save_data(html_content):
    """Parse the HTML and save data to CSV"""
    if not html_content:
        print("No HTML content to parse")
        return False
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize list for data
    papers_data = []
    
    # Find all session divs
    sections = soup.find_all('div', class_='section')
    
    if not sections:
        print("No sections found in the HTML")
        return False
    
    for section in sections:
        # Get session title
        session_title_elem = section.find('h2', class_='section__title')
        if not session_title_elem:
            continue
            
        session_title = session_title_elem.text.strip()
        print(f"Found session: {session_title}")
        
        # Find all papers in this session
        papers = section.find_all('div', class_='issue-item')
        
        for paper in papers:
            # Extract paper title
            title_elem = paper.find('h5', class_='issue-item__title')
            if not title_elem:
                continue
                
            paper_title = title_elem.text.strip()
            
            # Extract authors
            authors_section = paper.find('ul', class_='rlist--inline loa')
            if not authors_section:
                continue
                
            authors = authors_section.find_all('li')
            
            for author in authors:
                # Get author name
                author_name_elem = author.find('a', class_='author-name')
                if not author_name_elem:
                    continue
                    
                author_name = author_name_elem.text.strip()
                
                # Get author affiliation
                affiliation = ""
                institution_elem = author.find('a', class_='author-institution')
                if institution_elem and 'title' in institution_elem.attrs:
                    affiliation = institution_elem['title'].strip()
                
                # Add to dataset
                papers_data.append({
                    'session': session_title,
                    'paper_title': paper_title,
                    'author_name': author_name,
                    'author_affiliation': affiliation
                })
    
    # If we found data, save to CSV
    if papers_data:
        with open('acm_proceedings.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['session', 'paper_title', 'author_name', 'author_affiliation']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for paper in papers_data:
                writer.writerow(paper)
        
        print(f"Successfully scraped {len(papers_data)} author entries.")
        print(f"Total unique papers: {len(set(item['paper_title'] for item in papers_data))}")
        print(f"Saved data to acm_proceedings.csv")
        return True
    else:
        print("No paper data found")
        return False

def main():
    # First try with cloudscraper
    html_content = scrape_with_cloudscraper()
    
    # If cloudscraper failed, try with Selenium
    if not html_content or "Just a moment..." in html_content:
        print("Cloudscraper could not bypass protection, trying Selenium...")
        html_content = scrape_with_selenium()
    
    # Parse and save the data
    success = parse_and_save_data(html_content)
    
    if not success:
        print("All scraping methods failed. The website might have advanced protections.")
        print("Consider these alternatives:")
        print("1. Use the ACM Digital Library API if available")
        print("2. Check if the data is available in a more accessible format")
        print("3. Try scraping at different times or with different IP addresses")
        print("4. Contact the website administrators for legitimate access to the data")

if __name__ == "__main__":
    main()