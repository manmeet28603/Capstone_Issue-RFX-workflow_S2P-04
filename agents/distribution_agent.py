"""
AutoGen-based Distribution Agent
Distributes RFX packages to suppliers using AutoGen framework
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class DistributionAgentAutogen:
    """
    Distribution Agent using AutoGen framework
    """
    
    def __init__(self, base_path: str, llm_config: Dict[str, Any]):
        """
        Initialize Distribution Agent
        
        Args:
            base_path: Base path to workflow data
            llm_config: LLM configuration for AutoGen
        """
        self.base_path = Path(base_path)
        self.agent_id = "Distribution_Agent"
        self.llm_config = llm_config
    
    def _load_rfx_document(self) -> Dict[str, Any]:
        """Load drafted RFX document"""
        doc_path = self.base_path / "Distribution_Agent/Inputs/drafted_rfx_from_CGA.json"
        with open(doc_path, 'r') as f:
            return json.load(f)
    
    def _load_supplier_shortlist(self) -> list:
        """Load supplier shortlist"""
        supplier_path = self.base_path / "Distribution_Agent/Inputs/supplier_shortlist.json"
        with open(supplier_path, 'r') as f:
            data = json.load(f)
            return data.get('shortlisted_suppliers', [])
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute RFX distribution to suppliers
        
        Returns:
            Result with distribution status
        """
        print(f"\n→ {self.agent_id}: Distributing RFX...")
        
        try:
            # Load data
            rfx_doc = self._load_rfx_document()
            suppliers = self._load_supplier_shortlist()
            rfx_id = rfx_doc.get('rfx_id')
            
            # Distribute to each supplier
            distribution_records = []
            for supplier in suppliers:
                record = {
                    "LIFNR": supplier.get('LIFNR'),
                    "supplier_name": supplier.get('name'),
                    "channel": "portal",
                    "message_id": f"MSG-{rfx_id}-{supplier.get('LIFNR')}",
                    "delivered": True,
                    "delivery_ts": datetime.now().isoformat()
                }
                distribution_records.append(record)
            
            # Create distribution status
            distribution_status = {
                "rfx_id": rfx_id,
                "distribution_timestamp": datetime.now().isoformat(),
                "total_suppliers": len(suppliers),
                "successfully_delivered": len(distribution_records),
                "records": distribution_records
            }
            
            # Save output
            output_path = self.base_path / "Distribution_Agent/Outputs/distribution_status.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(distribution_status, f, indent=2)
            
            print(f"  ✓ Distributed to {len(suppliers)} suppliers")
            
            return {
                "status": "success",
                "rfx_id": rfx_id,
                "message": f"RFX distributed to {len(suppliers)} suppliers",
                "data": distribution_status
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Distribution failed: {str(e)}"
            }


def create_distribution_function(base_path: str, llm_config: Dict[str, Any]):
    """
    Create function for AutoGen agent to call
    
    Args:
        base_path: Base path to workflow data
        llm_config: LLM configuration
    
    Returns:
        Function that executes distribution
    """
    agent = DistributionAgentAutogen(base_path, llm_config)
    
    def distribute_rfx() -> str:
        """Distribute RFX to suppliers"""
        result = agent.execute()
        return json.dumps(result, indent=2)
    
    return distribute_rfx
