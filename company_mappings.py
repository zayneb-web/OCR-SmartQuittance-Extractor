#!/usr/bin/env python3
"""
Company to Format Mappings Configuration
Add your company mappings here for automatic format detection
"""

# Company name to format mapping
COMPANY_FORMAT_MAPPING = {
    
    # CARTE ASSURANCES company - uses hp0012_custom format
    "carte assurances": "hp0012_custom",
    "CARTE ASSURANCES": "hp0012_custom",
    "carteassurances": "hp0012_custom",
    "carte": "hp0012_custom",
    "CARTE": "hp0012_custom",
    
    # Maghrebia company - use hp0012_custom format (based on your successful extraction)
    "maghrebia": "format_1",
    "Maghrebia": "format_1",
    
    # Add more companies here as needed
    # "company_name": "format_name",
}

def get_format_for_company(company_name):
    """
    Get the appropriate format for a given company name.
    Returns the format name or 'format_1' as default.
    """
    if not company_name:
        return "format_1"
    
    company_name_lower = company_name.lower().strip()
    
    # Check for exact matches first
    for company_key, format_name in COMPANY_FORMAT_MAPPING.items():
        if company_key.lower() == company_name_lower:
            return format_name
    
    # Check for partial matches
    for company_key, format_name in COMPANY_FORMAT_MAPPING.items():
        if company_key.lower() in company_name_lower:
            return format_name
    
    # Default format if no match found
    return "format_1"

def add_company_mapping(company_name, format_name):
    """
    Add a new company mapping.
    """
    COMPANY_FORMAT_MAPPING[company_name] = format_name
    print(f"Added mapping: '{company_name}' -> '{format_name}'")

def list_all_mappings():
    """
    List all current company mappings.
    """
    print("Current Company Mappings:")
    print("=" * 50)
    for company, format_name in COMPANY_FORMAT_MAPPING.items():
        print(f"'{company}' -> '{format_name}'")
    print("=" * 50)

if __name__ == "__main__":
    # Example usage
    print("Company Format Mappings Configuration")
    print("=" * 50)
    
    # List current mappings
    list_all_mappings()
    
    # Test some mappings
    test_companies = ["ipteur", "CARTE ASSURANCES", "Assurance Tunisie", "Unknown Company"]
    
    print("\nTesting Company Format Detection:")
    print("-" * 40)
    for company in test_companies:
        format_name = get_format_for_company(company)
        print(f"'{company}' -> '{format_name}'")
    
    # Example of adding a new mapping
    print("\nAdding new mapping example:")
    add_company_mapping("New Insurance Co", "format_1")
    list_all_mappings() 