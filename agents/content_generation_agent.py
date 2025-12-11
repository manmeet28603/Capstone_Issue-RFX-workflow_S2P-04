"""
AutoGen-based Content Generation Agent
Generates RFX documents using AutoGen framework
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ContentGenerationAgentAutogen:
    """
    Content Generation Agent using AutoGen framework
    """
    
    def __init__(self, base_path: str, llm_config: Dict[str, Any]):
        """
        Initialize Content Generation Agent
        
        Args:
            base_path: Base path to workflow data
            llm_config: LLM configuration for AutoGen
        """
        self.base_path = Path(base_path)
        self.agent_id = "Content_Generation_Agent"
        self.llm_config = llm_config
        
        # Load data
        self.company_profile = self._load_company_profile()
        self.sap_fields = self._load_sap_fields()
    
    def _load_company_profile(self) -> Dict[str, Any]:
        """Load company profile"""
        profile_path = self.base_path / "company_profile.json"
        with open(profile_path, 'r') as f:
            return json.load(f)
    
    def _load_sap_fields(self) -> Dict[str, Any]:
        """Load SAP field dictionary"""
        sap_path = self.base_path / "sap_field_dictionary.json"
        with open(sap_path, 'r') as f:
            return json.load(f)
    
    def _load_customized_template(self) -> Dict[str, Any]:
        """Load customized template from Template Builder"""
        template_path = self.base_path / "Content_Generation_Agent/Inputs/customized_template_from_TBA.json"
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute RFX document generation
        
        Returns:
            Result with drafted RFX document
        """
        print(f"\n→ {self.agent_id}: Generating RFX document...")
        
        try:
            # Load template
            template = self._load_customized_template()
            rfx_id = template.get('rfx_id')
            requirements = template.get('requirements', {})
            
            # Generate SAP header
            header = {
                "BUKRS": "2000",  # Company Code
                "EKORG": "PG01",  # Purchasing Organization
                "EKGRP": "CHE",   # Purchasing Group
                "BSART": "AN",    # Document Type (RFP)
                "WAERS": "USD",   # Currency
                "rfx_id": rfx_id
            }
            
            # Generate line items
            items = [
                {
                    "item_number": "00010",
                    "MATNR": requirements.get('MATNR', 'GLYC-USP-001'),
                    "description": f"{requirements.get('material', 'Material')} - {requirements.get('grade', 'Grade')}",
                    "MENGE": str(requirements.get('annual_volume_mt', 6000) / 12),
                    "MEINS": "MT",
                    "delivery_plant": requirements.get('plants', ['US01'])[0],
                    "INCO1": "DDP",
                    "INCO2": "Cincinnati"
                }
            ]
            
            # Generate sections
            sections = {
                "Scope of Work": f"Supply of {requirements.get('material', 'Material')} as per specifications.",
                "Technical Specifications": f"Grade: {requirements.get('grade', 'N/A')}, Purity: {requirements.get('purity', 'N/A')}%",
                "Quality & Compliance": f"Must comply with: {', '.join(requirements.get('compliance', []))}",
                "Delivery Terms": requirements.get('delivery_schedule', 'As per contract'),
                "Pricing Structure": "Please provide unit pricing in USD per MT",
                "Payment Terms": "Net 60 days from invoice date"
            }
            
            # Create RFX document
            rfx_document = {
                "rfx_id": rfx_id,
                "header": header,
                "items": items,
                "sections": sections,
                "requirements": requirements,
                "generated_timestamp": datetime.now().isoformat(),
                "docx_path": "Content_Generation_Agent/Outputs/drafted_rfx_document.docx"
            }
            
            # Save output
            output_path = self.base_path / "Content_Generation_Agent/Outputs/drafted_rfx_document.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(rfx_document, f, indent=2)
            
            print(f"  ✓ RFX document generated: {rfx_id}")
            print(f"  ✓ {len(items)} line items, {len(sections)} sections")
            
            return {
                "status": "success",
                "rfx_id": rfx_id,
                "message": "RFX document drafted successfully",
                "data": rfx_document
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Content generation failed: {str(e)}"
            }


def create_content_generation_function(base_path: str, llm_config: Dict[str, Any]):
    """
    Create function for AutoGen agent to call
    
    Args:
        base_path: Base path to workflow data
        llm_config: LLM configuration
    
    Returns:
        Function that executes content generation
    """
    agent = ContentGenerationAgentAutogen(base_path, llm_config)
    
    def generate_content() -> str:
        """Generate RFX document content"""
        result = agent.execute()
        return json.dumps(result, indent=2)
    
    return generate_content
