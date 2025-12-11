"""
AutoGen-based Template Builder Agent
Selects and customizes RFX templates using AutoGen framework
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class TemplateBuilderAgentAutogen:
    """
    Template Builder Agent using AutoGen framework
    """
    
    def __init__(self, base_path: str, llm_config: Dict[str, Any]):
        """
        Initialize Template Builder Agent
        
        Args:
            base_path: Base path to workflow data
            llm_config: LLM configuration for AutoGen
        """
        self.base_path = Path(base_path)
        self.agent_id = "Template_Builder_Agent"
        self.llm_config = llm_config
        
        # Load data
        self.requirements = self._load_requirements()
        self.templates = self._load_templates()
        
    def _load_requirements(self) -> Dict[str, Any]:
        """Load procurement requirements"""
        req_path = self.base_path / "Template_Builder_Agent/Inputs/detailed_requirements_from_procurement.json"
        with open(req_path, 'r') as f:
            return json.load(f)
    
    def _load_templates(self) -> list:
        """Load template library"""
        template_path = self.base_path / "Template_Builder_Agent/Data_Sources/historical_templates/historical_rfx_templates_index.json"
        with open(template_path, 'r') as f:
            data = json.load(f)
            return data.get('templates', [])
    
    def _generate_rfx_id(self) -> str:
        """Generate unique RFX ID"""
        bukrs = "2000"
        material_code = self.requirements.get('MATNR', 'GLYC')[:4].upper()
        year = datetime.now().year
        doc_type = "RFP"
        seq = random.randint(100, 999)
        return f"{bukrs}-{material_code}-{year}-{doc_type}-{seq}"
    
    def select_template(self) -> Dict[str, Any]:
        """
        Select best template for requirements
        
        Returns:
            Selected template data
        """
        # Use rule-based selection or LLM if available
        category = self.requirements.get('category', 'Chemical')
        material = self.requirements.get('material', '').lower()
        
        # Find matching template
        selected_template = None
        for template in self.templates:
            template_title = template.get('title', '').lower()
            template_category = template.get('category', '')
            
            if category in template_category and material in template_title:
                selected_template = template
                break
        
        if not selected_template and self.templates:
            selected_template = self.templates[0]
        
        return selected_template
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute template selection and customization
        
        Returns:
            Result with customized template
        """
        print(f"\n→ {self.agent_id}: Selecting template...")
        
        # Select template
        selected_template = self.select_template()
        
        if not selected_template:
            return {
                "status": "error",
                "message": "No suitable template found"
            }
        
        # Generate RFX ID
        rfx_id = self._generate_rfx_id()
        
        # Customize template
        customized_template = {
            "rfx_id": rfx_id,
            "template_id": selected_template.get('template_id'),
            "title": selected_template.get('title'),
            "category": selected_template.get('category'),
            "sections": selected_template.get('mandatory_sections', []),
            "requirements": self.requirements,
            "customization_timestamp": datetime.now().isoformat()
        }
        
        # Save output
        output_path = self.base_path / "Template_Builder_Agent/Outputs/customized_rfx_template.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(customized_template, f, indent=2)
        
        print(f"  ✓ Template selected: {selected_template.get('title')}")
        print(f"  ✓ RFX ID: {rfx_id}")
        
        return {
            "status": "success",
            "rfx_id": rfx_id,
            "template_id": selected_template.get('template_id'),
            "message": f"Template customized successfully",
            "data": customized_template
        }


def create_template_builder_function(base_path: str, llm_config: Dict[str, Any]):
    """
    Create function for AutoGen agent to call
    
    Args:
        base_path: Base path to workflow data
        llm_config: LLM configuration
    
    Returns:
        Function that executes template building
    """
    agent = TemplateBuilderAgentAutogen(base_path, llm_config)
    
    def build_template() -> str:
        """Select and customize RFX template"""
        result = agent.execute()
        return json.dumps(result, indent=2)
    
    return build_template
