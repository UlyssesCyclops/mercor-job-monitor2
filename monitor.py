#!/usr/bin/env python3
"""
Mercor Job Monitor
Scrapes job listings from Mercor and sends email notifications for new postings.
"""

import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright --break-system-packages")
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright


JOBS_FILE = "seen_jobs.json"
CONFIG_FILE = "config.json"


def load_config():
    """Load configuration from config.json"""
    if not Path(CONFIG_FILE).exists():
        print(f"Error: {CONFIG_FILE} not found. Please create it with your email settings.")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def load_seen_jobs():
    """Load previously seen job IDs"""
    if Path(JOBS_FILE).exists():
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_seen_jobs(jobs):
    """Save seen job IDs to file"""
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)


def scrape_jobs():
    """Scrape job listings from Mercor using Playwright"""
    print(f"[{datetime.now()}] Scraping Mercor jobs...")
    
    jobs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Load the Mercor jobs page
            page.goto("https://work.mercor.com/explore", wait_until="networkidle", timeout=30000)
            
            # Wait for job listings to load
            page.wait_for_selector('a[href*="/jobs/list_"]', timeout=60000)
            
            # Extract job information
            job_elements = page.query_selector_all('a[href*="/jobs/list_"]')
            
            for element in job_elements:
                try:
                    # Get the job URL/ID
                    href = element.get_attribute('href')
                    job_id = href.split('list_')[1] if 'list_' in href else href
                    
                    # Get job title
                    title_elem = element.query_selector('h3')
                    title = title_elem.inner_text() if title_elem else "Unknown Title"
                    
                    # Get pay rate
                    pay_elem = element.query_selector('text=/\\$.*\\/hr/')
                    pay = pay_elem.inner_text() if pay_elem else "Pay not listed"
                    
                    # Get hired count
                    hired_elem = element.query_selector('text=/hired recently/')
                    hired = hired_elem.inner_text() if hired_elem else ""
                    
                    jobs.append({
                        'id': job_id,
                        'title': title.strip(),
                        'pay': pay.strip(),
                        'hired': hired.strip(),
                        'url': f"https://work.mercor.com{href}",
                        'found_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Error parsing job element: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping jobs: {e}")
        finally:
            browser.close()
    
    print(f"Found {len(jobs)} total jobs")
    return jobs


def send_email(config, new_jobs):
    """Send email notification about new jobs"""
    recipient = config['email']
    
    # Create email content
    subject = f"🚨 {len(new_jobs)} New Mercor Job{'s' if len(new_jobs) != 1 else ''} Available!"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .job {{ 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 15px 0; 
                background: #f9f9f9;
            }}
            .job-title {{ 
                color: #2c3e50; 
                font-size: 18px; 
                font-weight: bold; 
                margin-bottom: 8px;
            }}
            .job-pay {{ 
                color: #27ae60; 
                font-size: 16px; 
                font-weight: bold;
            }}
            .job-link {{ 
                display: inline-block;
                margin-top: 10px;
                padding: 8px 16px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }}
            .timestamp {{ color: #7f8c8d; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h2>New Jobs on Mercor</h2>
        <p>Found {len(new_jobs)} new job posting{'s' if len(new_jobs) != 1 else ''}:</p>
    """
    
    for job in new_jobs:
        html_body += f"""
        <div class="job">
            <div class="job-title">{job['title']}</div>
            <div class="job-pay">{job['pay']}</div>
            <div>{job['hired']}</div>
            <a href="{job['url']}" class="job-link">Apply Now</a>
            <div class="timestamp">Found: {job['found_at']}</div>
        </div>
        """
    
    html_body += """
        <hr>
        <p style="color: #7f8c8d; font-size: 12px;">
            This is an automated notification from your Mercor Job Monitor.
        </p>
    </body>
    </html>
    """
    
    # Send via Gmail SMTP
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config.get('smtp_from', recipient)
        msg['To'] = recipient
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Use Gmail SMTP with app password from GitHub Secrets
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not smtp_password:
            print("Warning: SMTP_PASSWORD not set. Skipping email.")
            return
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config.get('smtp_user', recipient), smtp_password)
            server.send_message(msg)
        
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    """Main function"""
    config = load_config()
    seen_jobs = load_seen_jobs()
    
    # Scrape current jobs
    current_jobs = scrape_jobs()
    
    if not current_jobs:
        print("No jobs found. The page might have changed or failed to load.")
        return
    
    # Find new jobs
    seen_ids = set(seen_jobs)
    new_jobs = [job for job in current_jobs if job['id'] not in seen_ids]
    
    if new_jobs:
        print(f"Found {len(new_jobs)} new job(s)!")
        for job in new_jobs:
            print(f"  - {job['title']} ({job['pay']})")
        
        # Send notification
        send_email(config, new_jobs)
        
        # Update seen jobs
        all_job_ids = list(seen_ids) + [job['id'] for job in new_jobs]
        save_seen_jobs(all_job_ids)
    else:
        print("No new jobs found.")


if __name__ == "__main__":
    main()
