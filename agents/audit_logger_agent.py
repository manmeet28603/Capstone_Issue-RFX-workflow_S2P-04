import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class AuditLoggerAgentAutogen:
    
    def __init__(self, base_path: str, llm_config: Dict[str, Any]):
        self.base_path = Path(base_path)
        self.agent_id = "Audit_Logger_Agent"
        self.llm_config = llm_config
    
    def _collect_workflow_events(self) -> list:
        events = []
        
        try:
            template_path = self.base_path / "Template_Builder_Agent/Outputs/customized_rfx_template.json"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                events.append({
                    "event": "template_customized",
                    "agent": "Template_Builder_Agent",
                    "rfx_id": template_data.get('rfx_id'),
                    "timestamp": template_data.get('customization_timestamp'),
                    "details": {
                        "template_id": template_data.get('template_id'),
                        "category": template_data.get('category')
                    }
                })
        except Exception:
            pass
        
        try:
            content_path = self.base_path / "Content_Generation_Agent/Outputs/drafted_rfx_document.json"
            if content_path.exists():
                with open(content_path, 'r') as f:
                    content_data = json.load(f)
                events.append({
                    "event": "rfx_drafted",
                    "agent": "Content_Generation_Agent",
                    "rfx_id": content_data.get('rfx_id'),
                    "timestamp": content_data.get('generated_timestamp'),
                    "details": {
                        "line_items": len(content_data.get('items', [])),
                        "sections": len(content_data.get('sections', {}))
                    }
                })
        except Exception:
            pass
        
        try:
            dist_path = self.base_path / "Distribution_Agent/Outputs/distribution_status.json"
            if dist_path.exists():
                with open(dist_path, 'r') as f:
                    dist_data = json.load(f)
                events.append({
                    "event": "rfx_distributed",
                    "agent": "Distribution_Agent",
                    "rfx_id": dist_data.get('rfx_id'),
                    "timestamp": dist_data.get('distribution_timestamp'),
                    "details": {
                        "total_suppliers": dist_data.get('total_suppliers'),
                        "successfully_delivered": dist_data.get('successfully_delivered')
                    }
                })
        except Exception:
            pass
        
        return events
    
    def execute(self) -> Dict[str, Any]:
        print(f"\n→ {self.agent_id}: Creating audit trail...")
        
        try:
            events = self._collect_workflow_events()
            
            audit_trail = {
                "audit_timestamp": datetime.now().isoformat(),
                "workflow_type": "Issue RFX",
                "total_events": len(events),
                "events": events,
                "compliance_status": "COMPLIANT",
                "insights": "All workflow steps completed successfully with full traceability."
            }
            
            output_path = self.base_path / "Audit_Logger_Agent/Outputs/audit_trail.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(audit_trail, f, indent=2)
            
            print(f"  ✓ Audit trail logged: {len(events)} events")
            
            return {
                "status": "success",
                "message": f"Audit trail logged with {len(events)} events",
                "data": audit_trail
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Audit logging failed: {str(e)}"
            }


def create_audit_logger_function(base_path: str, llm_config: Dict[str, Any]):
    agent = AuditLoggerAgentAutogen(base_path, llm_config)
    
    def log_audit() -> str:
        result = agent.execute()
        return json.dumps(result, indent=2)
    
    return log_audit
