import re
import time
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

class EmailScraper:
    """Scrape email patterns from various sources."""
    
    def __init__(self, delay=1.0):
        """Initialize the scraper with a delay between requests to avoid rate limiting."""
        self.delay = delay
        self.logger = logging.getLogger(__name__)
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    def extract_emails_from_text(self, text):
        """Extract email addresses from text using regex."""
        if not text:
            return []
        return self.email_pattern.findall(text)
    
    def scrape_website(self, url):
        """Scrape a website for email addresses."""
        emails = []
        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract emails from text content
            text_content = soup.get_text()
            emails.extend(self.extract_emails_from_text(text_content))
            
            # Extract emails from mailto links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href[7:].split('?')[0]  # Remove 'mailto:' and any parameters
                    if '@' in email and self.email_pattern.match(email):
                        emails.append(email)
            
            # Remove duplicates
            emails = list(set(emails))
            
            self.logger.info(f"Found {len(emails)} email addresses on {url}")
            return emails
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return []
    
    def scrape_linkedin_people(self, company_name):
        """
        Note: This is a placeholder. Direct LinkedIn scraping violates their terms of service.
        In a real implementation, you would use their official API with proper authentication.
        """
        self.logger.warning("LinkedIn scraping requires API access. This is a placeholder.")
        return []
    
    def scrape_company_website(self, domain):
        """Scrape a company website for email patterns."""
        emails = []
        
        # Try common pages where emails might be found
        pages = [
            "",  # Homepage
            "contact",
            "about",
            "team",
            "about-us",
            "contact-us",
            "our-team",
            "leadership",
            "staff",
            "people"
        ]
        
        for page in pages:
            url = f"https://{domain}/{page}" if page else f"https://{domain}"
            self.logger.info(f"Scraping {url}")
            
            page_emails = self.scrape_website(url)
            emails.extend(page_emails)
            
            # Respect the site by waiting between requests
            time.sleep(self.delay)
        
        # Remove duplicates
        emails = list(set(emails))
        return emails
    
    def extract_patterns_from_emails(self, emails, storage):
        """Extract patterns from scraped emails and store them."""
        domain_emails = {}
        
        # Group emails by domain
        for email in emails:
            if '@' in email:
                local_part, domain = email.split('@', 1)
                if domain not in domain_emails:
                    domain_emails[domain] = []
                domain_emails[domain].append(email)
        
        # Process each domain
        for domain, domain_emails_list in domain_emails.items():
            self.logger.info(f"Processing {len(domain_emails_list)} emails for domain {domain}")
            
            # Try to infer patterns from the emails
            # This is simplified and would need more sophisticated logic in a real implementation
            for email in domain_emails_list:
                local_part = email.split('@')[0]
                
                # Try to guess the pattern
                # This is very basic and would need to be enhanced with name data
                if '.' in local_part:
                    pattern = "{first}.{last}@{domain}"
                elif '_' in local_part:
                    pattern = "{first}_{last}@{domain}"
                else:
                    pattern = "{first}{last}@{domain}"
                
                # Store the pattern
                storage.add_pattern(domain, pattern)
                self.logger.info(f"Added pattern {pattern} for domain {domain}") 