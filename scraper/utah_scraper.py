"""
Utah Procurement Scraper
Monitors Utah Public Procurement Place (U3P) for new bids matching CMT criteria
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
UTAH_BID_URL = "https://utah.bonfirehub.com"
CMT_KEYWORDS = [
    "materials testing",
    "soils testing",
    "concrete inspection",
    "compaction testing",
    "asphalt testing",
    "geotechnical",
    "special inspection",
    "laboratory analysis",
    "field testing"
]

def scrape_utah_bids(limit=50):
    """
    Scrape recent bids from Utah Public Procurement Place
    Returns list of bids matching CMT keywords
    """
    try:
        # This is a placeholder - actual implementation depends on U3P API/structure
        # For now, returns example data structure
        example_bids = [
            {
                "id": "UTAH-2026-001",
                "title": "Road Rehabilitation Project - Materials Testing Services",
                "agency": "Salt Lake County Public Works",
                "deadline": "2026-06-15",
                "estimated_value": "$150,000",
                "url": "https://utah.bonfirehub.com/opportunities/detail/...",
                "posted_date": datetime.now().isoformat()
            }
        ]
        return example_bids
    except Exception as e:
        print(f"Error scraping bids: {e}")
        return []

def filter_bids(bids):
    """
    Filter bids for CMT-relevant keywords
    """
    relevant_bids = []
    for bid in bids:
        title_lower = bid.get("title", "").lower()
        description_lower = bid.get("description", "").lower()
        
        for keyword in CMT_KEYWORDS:
            if keyword in title_lower or keyword in description_lower:
                relevant_bids.append(bid)
                break
    
    return relevant_bids

def load_seen_bids():
    """Load previously seen bids to avoid duplicate alerts"""
    if os.path.exists("scraper/seen_bids.json"):
        with open("scraper/seen_bids.json", "r") as f:
            return json.load(f)
    return []

def save_seen_bids(bids):
    """Save seen bids to avoid duplicates"""
    os.makedirs("scraper", exist_ok=True)
    with open("scraper/seen_bids.json", "w") as f:
        json.dump(bids, f, indent=2)

def send_alert(bid, email=None):
    """
    Send alert for new bid (placeholder for email integration)
    """
    email = email or os.getenv("ALERT_EMAIL")
    print(f"\n🎯 NEW BID ALERT!")
    print(f"Title: {bid.get('title')}")
    print(f"Agency: {bid.get('agency')}")
    print(f"Deadline: {bid.get('deadline')}")
    print(f"Value: {bid.get('estimated_value')}")
    print(f"Link: {bid.get('url')}")
    print(f"Posted: {bid.get('posted_date')}")
    
    # TODO: Integrate with email service (Resend, SendGrid, etc.)
    if email:
        print(f"Alert would be sent to: {email}")

def main():
    """Main scraper loop"""
    print("Starting Utah Procurement Scraper...")
    print(f"Monitoring for CMT keywords: {', '.join(CMT_KEYWORDS[:3])}...")
    
    # Scrape bids
    bids = scrape_utah_bids()
    print(f"Found {len(bids)} bids")
    
    # Filter for CMT relevance
    relevant = filter_bids(bids)
    print(f"Filtered to {len(relevant)} relevant bids")
    
    # Check against seen bids
    seen_ids = load_seen_bids()
    new_bids = [b for b in relevant if b.get("id") not in seen_ids]
    
    # Alert on new bids
    for bid in new_bids:
        send_alert(bid)
    
    # Update seen list
    updated_seen = seen_ids + [b.get("id") for b in new_bids]
    save_seen_bids(updated_seen)
    
    print(f"\n✅ Found {len(new_bids)} new bids")

if __name__ == "__main__":
    main()
