import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_proceedings():
    # URL of the proceedings page
    url = "https://dl.acm.org/doi/proceedings/10.1145/3706598?tocHeading=heading36"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Send HTTP request to the URL
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        print(f"Failed to retrieve the page. Status code: {response.text}")
        return
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize list to store all papers
    all_papers = []
    
    # Find all session titles and papers
    current_session = ""
    
    # Look for session headers and papers <a id="heading2" href="/doi/proceedings/10.1145/3706598?tocHeading=heading2" class="section__title accordion-tabbed__control left-bordered-title" aria-expanded="false">SESSION: AI Ethics and Concerns</a>
    for element in soup.find_all(['h2', 'div'], class_=['section__title', 'issue-item']):
        # Check if it's a session header
        if 'section__title' in element.get('class', []):
            current_session = element.text.strip()
        
        # Check if it's a paper entry
        elif 'issue-item' in element.get('class', []):
            # Extract paper title
            title_elem = element.find('h5', class_='issue-item__title')
            if title_elem:
                paper_title = title_elem.text.strip()
            else:
                continue  # Skip if no title found
            
            # Extract authors and affiliations
            authors_info = []
            authors_elem = element.find('ul', class_='rlist--inline loa')
            
            if authors_elem:
                for author_elem in authors_elem.find_all('li'):
                    author_name = author_elem.find('a', class_='author-name').text.strip() if author_elem.find('a', class_='author-name') else ""
                    
                    # Extract affiliation
                    affiliation = ""
                    affil_elem = author_elem.find('a', class_='author-info')
                    if affil_elem and 'title' in affil_elem.attrs:
                        affiliation = affil_elem['title'].strip()
                    
                    if author_name:  # Only add if we found a name
                        authors_info.append({
                            'name': author_name,
                            'affiliation': affiliation
                        })
            
            # Add to the list of papers
            if authors_info:  # Only add papers that have authors
                for author in authors_info:
                    all_papers.append({
                        'session': current_session,
                        'paper_title': paper_title,
                        'author_name': author['name'],
                        'author_affiliation': author['affiliation']
                    })
    
    # Save to CSV
    with open('acm_proceedings.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['session', 'paper_title', 'author_name', 'author_affiliation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for paper in all_papers:
            writer.writerow(paper)
    
    print(f"Successfully scraped {len(all_papers)} author entries from {len(set(paper['paper_title'] for paper in all_papers))} papers.")

if __name__ == "__main__":
    scrape_proceedings()