import argparse
import csv
import sys
import logging
from .pattern_generator import PatternGenerator
from .storage import Storage
from .verification import EmailVerifier
from .scraper import EmailScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description='Email Pattern Predictor')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict email addresses')
    predict_parser.add_argument('--first', required=True, help='First name')
    predict_parser.add_argument('--last', required=True, help='Last name')
    predict_parser.add_argument('--domain', required=True, help='Domain name')
    predict_parser.add_argument('--top', type=int, default=3, help='Number of top predictions to show')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train on known email patterns')
    train_parser.add_argument('--file', required=True, help='CSV file with known emails')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Process multiple contacts')
    batch_parser.add_argument('--file', required=True, help='CSV file with contacts')
    batch_parser.add_argument('--output', required=True, help='Output CSV file')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape email patterns from websites')
    scrape_parser.add_argument('--domain', required=True, help='Domain to scrape')
    scrape_parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    
    args = parser.parse_args()
    
    if args.command == 'predict':
        predict_email(args.first, args.last, args.domain, args.top)
    elif args.command == 'train':
        train_on_file(args.file)
    elif args.command == 'batch':
        batch_process(args.file, args.output)
    elif args.command == 'scrape':
        scrape_domain(args.domain, args.delay)
    else:
        parser.print_help()

def predict_email(first_name, last_name, domain, top_n=3):
    """Predict email addresses for a single contact."""
    generator = PatternGenerator()
    storage = Storage()
    verifier = EmailVerifier()
    
    print(f"Predicting email for {first_name} {last_name} at {domain}...")
    
    # Generate candidates
    candidates = generator.generate_candidates(first_name, last_name, domain)
    
    # Rank candidates
    ranked_candidates = verifier.rank_candidates(candidates, domain, storage)
    
    # Display results
    print("\nTop predictions:")
    for i, (email, confidence) in enumerate(ranked_candidates[:top_n], 1):
        print(f"{i}. {email} (Confidence: {confidence:.2f})")
    
    return ranked_candidates

def train_on_file(file_path):
    """Train the system on known email patterns."""
    storage = Storage()
    
    try:
        print(f"Training on file: {file_path}")
        storage.import_from_csv(file_path)
        print("Training completed successfully.")
    except Exception as e:
        print(f"Error during training: {e}")

def batch_process(input_file, output_file):
    """Process multiple contacts from a CSV file."""
    generator = PatternGenerator()
    storage = Storage()
    verifier = EmailVerifier()
    
    try:
        with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
            reader = csv.reader(f_in)
            writer = csv.writer(f_out)
            
            # Write header
            writer.writerow(['First Name', 'Last Name', 'Domain', 'Predicted Email', 'Confidence'])
            
            # Skip header in input file
            header = next(reader, None)
            
            # Process each row
            for row in reader:
                if len(row) >= 3:  # Expecting: first_name, last_name, domain
                    first_name, last_name, domain = row[0], row[1], row[2]
                    
                    # Generate and rank candidates
                    candidates = generator.generate_candidates(first_name, last_name, domain)
                    ranked_candidates = verifier.rank_candidates(candidates, domain, storage)
                    
                    # Write top prediction to output file
                    if ranked_candidates:
                        top_email, confidence = ranked_candidates[0]
                        writer.writerow([first_name, last_name, domain, top_email, f"{confidence:.2f}"])
                    else:
                        writer.writerow([first_name, last_name, domain, "No prediction", "0.00"])
                    
                    # Show progress
                    print(f"Processed: {first_name} {last_name} at {domain}")
        
        print(f"Batch processing completed. Results saved to {output_file}")
    except Exception as e:
        print(f"Error during batch processing: {e}")

def scrape_domain(domain, delay=1.0):
    """Scrape a domain for email patterns."""
    storage = Storage()
    scraper = EmailScraper(delay=delay)
    
    print(f"Scraping domain: {domain}")
    emails = scraper.scrape_company_website(domain)
    
    if emails:
        print(f"Found {len(emails)} email addresses:")
        for email in emails[:10]:  # Show first 10 emails
            print(f"  - {email}")
        
        if len(emails) > 10:
            print(f"  ... and {len(emails) - 10} more")
        
        # Extract patterns
        scraper.extract_patterns_from_emails(emails, storage)
        print("Extracted patterns have been stored in the database.")
    else:
        print("No email addresses found.")

if __name__ == "__main__":
    main() 