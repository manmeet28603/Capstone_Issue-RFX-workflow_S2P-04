"""
Utility functions for RFX workflow agents
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file with error handling
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation level
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)


def validate_sap_field(field_name: str, field_value: Any, 
                       sap_dictionary: Dict[str, str]) -> bool:
    """
    Validate SAP field against dictionary
    
    Args:
        field_name: SAP field name
        field_value: Field value
        sap_dictionary: SAP field dictionary
        
    Returns:
        True if field is valid
    """
    if field_name not in sap_dictionary:
        return False
    
    if field_value is None or field_value == "":
        return False
    
    return True


def generate_rfx_id(company_code: str, material_code: str, 
                    doc_type: str = "RFP") -> str:
    """
    Generate RFX identifier
    
    Args:
        company_code: Company/BUKRS code
        material_code: Material code
        doc_type: Document type (RFP, RFQ, RFI)
        
    Returns:
        Generated RFX ID
    """
    year = datetime.now().year
    day_of_year = datetime.now().strftime('%j')
    
    # Format: COMPANY-MATERIAL-YEAR-TYPE-DAY
    rfx_id = f"{company_code}-{material_code[:4]}-{year}-{doc_type}-{day_of_year[:3]}"
    
    return rfx_id


def format_timestamp(iso_timestamp: str = None) -> str:
    """
    Format timestamp for display
    
    Args:
        iso_timestamp: ISO format timestamp (optional)
        
    Returns:
        Formatted timestamp string
    """
    if iso_timestamp:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    else:
        dt = datetime.now()
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_success_rate(total: int, successful: int) -> float:
    """
    Calculate success rate percentage
    
    Args:
        total: Total count
        successful: Successful count
        
    Returns:
        Success rate as percentage
    """
    if total == 0:
        return 0.0
    
    return round((successful / total) * 100, 2)


def merge_validation_results(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple validation results
    
    Args:
        validations: List of validation dictionaries
        
    Returns:
        Merged validation result
    """
    all_passed = all(v.get('validation_status') == 'pass' for v in validations)
    
    merged = {
        'validation_status': 'pass' if all_passed else 'fail',
        'total_validations': len(validations),
        'passed': sum(1 for v in validations if v.get('validation_status') == 'pass'),
        'failed': sum(1 for v in validations if v.get('validation_status') == 'fail'),
        'details': validations
    }
    
    return merged


def extract_material_category(material_code: str) -> str:
    """
    Extract material category from material code
    
    Args:
        material_code: Material code (e.g., GLYC-USP-001)
        
    Returns:
        Material category
    """
    parts = material_code.split('-')
    return parts[0] if parts else 'UNKNOWN'


def validate_incoterms(incoterm: str) -> bool:
    """
    Validate Incoterms code
    
    Args:
        incoterm: Incoterms code
        
    Returns:
        True if valid
    """
    valid_incoterms = [
        'EXW', 'FCA', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP',
        'FAS', 'FOB', 'CFR', 'CIF'
    ]
    
    return incoterm.upper() in valid_incoterms


def validate_currency(currency: str) -> bool:
    """
    Validate currency code
    
    Args:
        currency: Currency code
        
    Returns:
        True if valid
    """
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR']
    
    return currency.upper() in valid_currencies


class WorkflowLogger:
    """Simple logger for workflow events"""
    
    def __init__(self, log_file: str = None):
        """
        Initialize logger
        
        Args:
            log_file: Path to log file (optional)
        """
        self.log_file = log_file
        self.logs = []
    
    def log(self, level: str, message: str, agent_id: str = None):
        """
        Log a message
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: Log message
            agent_id: Agent identifier (optional)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'agent_id': agent_id
        }
        
        self.logs.append(log_entry)
        
        # Print to console
        timestamp = format_timestamp()
        agent_str = f"[{agent_id}]" if agent_id else ""
        print(f"{timestamp} [{level}] {agent_str} {message}")
        
        # Save to file if configured
        if self.log_file:
            self.save_logs()
    
    def info(self, message: str, agent_id: str = None):
        """Log info message"""
        self.log('INFO', message, agent_id)
    
    def warning(self, message: str, agent_id: str = None):
        """Log warning message"""
        self.log('WARNING', message, agent_id)
    
    def error(self, message: str, agent_id: str = None):
        """Log error message"""
        self.log('ERROR', message, agent_id)
    
    def save_logs(self):
        """Save logs to file"""
        if self.log_file:
            save_json_file({'logs': self.logs}, self.log_file)


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test RFX ID generation
    rfx_id = generate_rfx_id("PG", "GLYC-USP-001", "RFP")
    print(f"Generated RFX ID: {rfx_id}")
    
    # Test timestamp formatting
    timestamp = format_timestamp()
    print(f"Formatted timestamp: {timestamp}")
    
    # Test success rate calculation
    rate = calculate_success_rate(100, 95)
    print(f"Success rate: {rate}%")
    
    # Test Incoterms validation
    print(f"DDP valid: {validate_incoterms('DDP')}")
    print(f"XXX valid: {validate_incoterms('XXX')}")
    
    print("\n✓ All utility tests completed")
