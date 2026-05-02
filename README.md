"""
BidRadar - AI Bid Generator
Uses Claude to read an RFP and generate a professional bid proposal.
"""

import anthropic
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_bid(
    rfp_text: str,
    company_name: str,
    company_profile: dict,
    output_format: str = "text"
) -> str:
    """
    Generate a bid proposal from an RFP.
    
    company_profile example:
    {
        "industry": "Construction Materials Testing",
        "services": ["Soils Testing", "Concrete Inspection", "Compaction Testing"],
        "certifications": ["ACI Certified", "AASHTO Accredited", "ICC Special Inspector"],
        "years_experience": 15,
        "contact_name": "John Smith",
        "contact_email": "john@company.com",
        "contact_phone": "801-555-0100",
        "license_number": "UT-CMT-12345"
    }
    """
    
    system_prompt = f"""You are an expert bid writer specializing in government procurement 
for construction and materials testing companies. You write clear, professional, 
compliant bid proposals that win contracts.

You are writing on behalf of {company_name}, a {company_profile.get('industry')} company.

Company details:
- Services: {', '.join(company_profile.get('services', []))}
- Certifications: {', '.join(company_profile.get('certifications', []))}
- Years in business: {company_profile.get('years_experience', 'N/A')}
- Contact: {company_profile.get('contact_name')} | {company_profile.get('contact_email')} | {company_profile.get('contact_phone')}
- License: {company_profile.get('license_number', 'N/A')}

When writing bids:
1. Address every requirement mentioned in the RFP directly
2. Use professional, confident language
3. Include relevant certifications and qualifications
4. Provide a clear scope of work
5. Include a pricing section with line items (use placeholder rates if not specified)
6. Add a qualifications section highlighting relevant experience
7. Close with a strong statement of capability
8. Format clearly with numbered sections"""

    user_prompt = f"""Please write a complete bid proposal for the following RFP.

RFP DETAILS:
{rfp_text}

Generate a professional bid proposal with these sections:
1. Cover Letter / Executive Summary
2. Understanding of the Project
3. Scope of Work / Approach
4. Qualifications & Certifications
5. Proposed Schedule
6. Fee Proposal / Pricing
7. References (placeholder)
8. Signature Block

Today's date: {datetime.now().strftime('%B %d, %Y')}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    return response.content[0].text


def extract_requirements(rfp_text: str) -> dict:
    """Extract key requirements from an RFP for quick review."""
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Extract the key requirements from this RFP and return as JSON:

RFP TEXT:
{rfp_text}

Return JSON with these fields:
{{
  "project_title": "",
  "agency": "",
  "deadline": "",
  "estimated_value": "",
  "key_requirements": [],
  "certifications_required": [],
  "insurance_required": "",
  "bond_required": "",
  "contact_person": "",
  "submission_method": ""
}}

Return only the JSON, no other text."""
        }]
    )
    
    import json
    try:
        return json.loads(response.content[0].text)
    except Exception:
        return {"raw": response.content[0].text}


# ── Example usage ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    
    # Example RFP text (in real use, this comes from the scraper)
    sample_rfp = """
    REQUEST FOR PROPOSALS
    Agency: Salt Lake County Public Works
    Project: Materials Testing Services for Road Rehabilitation Project 2026
    
    The County seeks qualified firms to provide construction materials testing 
    and inspection services including:
    - Soils compaction testing
    - Concrete strength testing  
    - Asphalt pavement testing
    - Laboratory analysis
    
    Requirements:
    - AASHTO accredited laboratory
    - ACI certified technicians
    - Minimum 5 years experience on public works projects
    - General liability insurance $2M/$5M
    - Must be registered in Utah
    
    Proposals due: June 15, 2026
    Submit to: procurement@slco.org
    Estimated budget: $150,000
    """
    
    # Example company profile
    profile = {
        "industry": "Construction Materials Testing & Inspection",
        "services": [
            "Soils & Compaction Testing",
            "Concrete Testing & Inspection", 
            "Asphalt Testing",
            "Special Inspection Services",
            "Geotechnical Investigation"
        ],
        "certifications": [
            "AASHTO Accredited Laboratory",
            "ACI Certified Field Testing Technicians",
            "ICC Special Inspector Certified",
            "Utah Licensed Engineering Firm"
        ],
        "years_experience": 12,
        "contact_name": "Jane Doe, P.E.",
        "contact_email": "jane@acmecmt.com",
        "contact_phone": "801-555-0100",
        "license_number": "UT-PE-123456"
    }
    
    print("Extracting RFP requirements...")
    requirements = extract_requirements(sample_rfp)
    print(f"Project: {requirements.get('project_title', 'N/A')}")
    print(f"Deadline: {requirements.get('deadline', 'N/A')}")
    print(f"Value: {requirements.get('estimated_value', 'N/A')}")
    
    print("\nGenerating bid proposal...")
    bid = generate_bid(sample_rfp, "Acme CMT Services LLC", profile)
    
    # Save to file
    filename = f"bid_proposal_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, "w") as f:
        f.write(bid)
    
    print(f"\nBid saved to: {filename}")
    print("\nPreview (first 500 chars):")
    print(bid[:500] + "...")
