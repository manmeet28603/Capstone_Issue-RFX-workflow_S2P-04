import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class OrchestrationAgent:
    
    def __init__(self, base_path: str, llm_config: Dict[str, Any] = None):
        self.base_path = Path(base_path)
        self.agent_id = "Orchestration_Agent"
        self.llm_config = llm_config or {}
        
        from agents.template_builder_agent import create_template_builder_function
        from agents.content_generation_agent import create_content_generation_function
        from agents.distribution_agent import create_distribution_function
        from agents.audit_logger_agent import create_audit_logger_function
        
        self.template_builder = create_template_builder_function(str(base_path), llm_config)
        self.content_generator = create_content_generation_function(str(base_path), llm_config)
        self.distributor = create_distribution_function(str(base_path), llm_config)
        self.audit_logger = create_audit_logger_function(str(base_path), llm_config)
        
        self.workflow_results = []
        self.exceptions = []
        self.stakeholder_requests = []
    
    def validate_inputs(self) -> Dict[str, Any]:
        required_files = [
            self.base_path / "company_profile.json",
            self.base_path / "sap_field_dictionary.json",
            self.base_path / "Template_Builder_Agent/Inputs/detailed_requirements_from_procurement.json",
            self.base_path / "Template_Builder_Agent/Data_Sources/historical_templates/historical_rfx_templates_index.json",
            self.base_path / "Distribution_Agent/Data_Sources/supplier_master_data.csv"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        return {
            'valid': len(missing_files) == 0,
            'missing_files': missing_files,
            'message': 'All inputs valid' if len(missing_files) == 0 else f'Missing {len(missing_files)} required files'
        }
    
    def validate_template_output(self, template_result: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        
        if template_result.get('status') != 'success':
            issues.append('Template building failed')
        
        if not template_result.get('rfx_id'):
            issues.append('Missing RFX ID')
        
        data = template_result.get('data', {})
        if not data.get('sections'):
            issues.append('Missing mandatory sections in template')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'requires_stakeholder': len(issues) > 0
        }
    
    def validate_content_output(self, content_result: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        
        if content_result.get('status') != 'success':
            issues.append('Content generation failed')
        
        data = content_result.get('data', {})
        header = data.get('header', {})
        
        mandatory_fields = ['BUKRS', 'EKORG', 'EKGRP', 'BSART']
        for field in mandatory_fields:
            if field not in header or not header[field]:
                issues.append(f'Missing mandatory SAP field: {field}')
        
        if not data.get('items'):
            issues.append('No line items generated')
        
        if not data.get('sections'):
            issues.append('Missing content sections')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'requires_stakeholder': len(issues) > 0
        }
    
    def validate_distribution_output(self, dist_result: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        
        if dist_result.get('status') != 'success':
            issues.append('Distribution failed')
        
        data = dist_result.get('data', {})
        if data.get('total_suppliers', 0) == 0:
            issues.append('No suppliers in distribution list')
        
        if data.get('successfully_delivered', 0) != data.get('total_suppliers', 0):
            issues.append('Some deliveries failed')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'requires_stakeholder': False
        }
    
    def request_stakeholder_clarification(self, agent_id: str, issues: List[str]) -> Dict[str, Any]:
        request = {
            'request_id': f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'issues': issues,
            'status': 'pending',
            'resolution': None
        }
        
        self.stakeholder_requests.append(request)
        
        print(f"\n⚠ EXCEPTION DETECTED - {agent_id}")
        print("-" * 70)
        print(f"Request ID: {request['request_id']}")
        print(f"Issues found:")
        for idx, issue in enumerate(issues, 1):
            print(f"  {idx}. {issue}")
        print("\n→ Stakeholder clarification required")
        print(f"→ Request logged for compliance")
        print("-" * 70)
        
        return request
    
    def handle_exception(self, agent_id: str, result: Dict[str, Any], 
                        validation: Dict[str, Any]) -> Dict[str, Any]:
        exception_record = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'error': {
                'message': result.get('message', 'Unknown error'),
                'issues': validation.get('issues', [])
            },
            'resolution_status': 'pending'
        }
        
        self.exceptions.append(exception_record)
        
        if validation.get('requires_stakeholder'):
            request = self.request_stakeholder_clarification(
                agent_id, 
                validation.get('issues', [])
            )
            exception_record['stakeholder_request'] = request['request_id']
            exception_record['resolution_status'] = 'awaiting_stakeholder'
        else:
            exception_record['resolution_status'] = 'auto_resolved'
        
        return exception_record
    
    def copy_data_between_agents(self):
        
        # Template Builder → Content Generator
        source = self.base_path / "Template_Builder_Agent/Outputs/customized_rfx_template.json"
        target = self.base_path / "Content_Generation_Agent/Inputs/customized_template_from_TBA.json"
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(source, 'r') as f:
                data = json.load(f)
            with open(target, 'w') as f:
                json.dump(data, f, indent=2)
        
        source = self.base_path / "Content_Generation_Agent/Outputs/drafted_rfx_document.json"
        target = self.base_path / "Distribution_Agent/Inputs/drafted_rfx_from_CGA.json"
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(source, 'r') as f:
                data = json.load(f)
            with open(target, 'w') as f:
                json.dump(data, f, indent=2)
    
    def execute(self) -> Dict[str, Any]:
        print("\nValidating workflow inputs...")
        input_validation = self.validate_inputs()
        
        if not input_validation['valid']:
            print(f"✗ Input validation failed: {input_validation['message']}")
            return {
                'status': 'error',
                'message': input_validation['message'],
                'missing_files': input_validation['missing_files']
            }
        
        print("✓ All inputs validated\n")
        
        print("="*70)
        print("EXECUTING RFX WORKFLOW WITH EXCEPTION HANDLING")
        print("="*70)
        
        rfx_id = None
        
        try:
            # Step 1: Template Builder Agent
            print("\nStep 1: Template Builder Agent")
            template_result_str = self.template_builder()
            template_result = json.loads(template_result_str)
            
            # Validate template output
            template_validation = self.validate_template_output(template_result)
            
            if not template_validation['valid']:
                exception = self.handle_exception(
                    'Template_Builder_Agent',
                    template_result,
                    template_validation
                )
                # In production, would wait for stakeholder response
                # For now, log and continue with best effort
            
            self.workflow_results.append({
                'agent_id': 'Template_Builder_Agent',
                'status': template_result.get('status'),
                'message': template_result.get('message'),
                'validation': template_validation
            })
            
            if template_result.get('status') == 'success':
                rfx_id = template_result.get('rfx_id')
                self.copy_data_between_agents()
            else:
                raise Exception("Template building failed")
            
            # Step 2: Content Generation Agent
            print("\nStep 2: Content Generation Agent")
            content_result_str = self.content_generator()
            content_result = json.loads(content_result_str)
            
            # Validate content output
            content_validation = self.validate_content_output(content_result)
            
            if not content_validation['valid']:
                exception = self.handle_exception(
                    'Content_Generation_Agent',
                    content_result,
                    content_validation
                )
            
            self.workflow_results.append({
                'agent_id': 'Content_Generation_Agent',
                'status': content_result.get('status'),
                'message': content_result.get('message'),
                'validation': content_validation
            })
            
            if content_result.get('status') == 'success':
                self.copy_data_between_agents()
            else:
                raise Exception("Content generation failed")
            
            # Step 3: Distribution Agent
            print("\nStep 3: Distribution Agent")
            dist_result_str = self.distributor()
            dist_result = json.loads(dist_result_str)
            
            # Validate distribution output
            dist_validation = self.validate_distribution_output(dist_result)
            
            if not dist_validation['valid']:
                exception = self.handle_exception(
                    'Distribution_Agent',
                    dist_result,
                    dist_validation
                )
            
            self.workflow_results.append({
                'agent_id': 'Distribution_Agent',
                'status': dist_result.get('status'),
                'message': dist_result.get('message'),
                'validation': dist_validation
            })
            
            if dist_result.get('status') != 'success':
                raise Exception("Distribution failed")
            
            # Step 4: Audit Logger Agent
            print("\nStep 4: Audit Logger Agent")
            audit_result_str = self.audit_logger()
            audit_result = json.loads(audit_result_str)
            
            self.workflow_results.append({
                'agent_id': 'Audit_Logger_Agent',
                'status': audit_result.get('status'),
                'message': audit_result.get('message')
            })
            
            print("\n" + "="*70)
            print("WORKFLOW COMPLETED")
            print("="*70)
            
            # Determine overall status
            has_exceptions = len(self.exceptions) > 0
            all_success = all(r['status'] == 'success' for r in self.workflow_results)
            
            if all_success and not has_exceptions:
                status = 'success'
                message = 'RFX workflow completed successfully'
            elif all_success and has_exceptions:
                status = 'success_with_warnings'
                message = f'RFX workflow completed with {len(self.exceptions)} warnings'
            else:
                status = 'partial_success'
                message = 'RFX workflow completed with some failures'
            
            return {
                'status': status,
                'rfx_id': rfx_id,
                'message': message,
                'workflow_results': self.workflow_results,
                'exceptions': self.exceptions,
                'stakeholder_requests': self.stakeholder_requests
            }
            
        except Exception as e:
            print(f"\n✗ Critical workflow error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'workflow_results': self.workflow_results,
                'exceptions': self.exceptions,
                'stakeholder_requests': self.stakeholder_requests
            }


def create_orchestration_function(base_path: str, llm_config: Dict[str, Any]):
    """
    Create orchestration function for AutoGen
    
    Args:
        base_path: Base path to workflow data
        llm_config: LLM configuration
    
    Returns:
        Function that executes orchestrated workflow
    """
    orchestrator = OrchestrationAgent(base_path, llm_config)
    
    def run_orchestrated_workflow() -> str:
        """Execute complete orchestrated RFX workflow"""
        result = orchestrator.execute()
        return json.dumps(result, indent=2)
    
    return run_orchestrated_workflow
