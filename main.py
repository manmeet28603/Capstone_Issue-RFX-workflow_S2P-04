"""
Main RFX Workflow Execution with AutoGen Framework
Orchestrates multi-agent workflow using Microsoft AutoGen
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import AutoGen configuration
from autogen_config import get_llm_config

# Import agent functions
from agents.template_builder_agent import create_template_builder_function
from agents.content_generation_agent import create_content_generation_function
from agents.distribution_agent import create_distribution_function
from agents.audit_logger_agent import create_audit_logger_function


def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print(" "*10 + "RFX WORKFLOW AUTOMATION SYSTEM - AUTOGEN")
    print(" "*10 + "Source-to-Pay (S2P) - Issue RFX Process")
    print("="*70)
    print("\nPowered by Microsoft AutoGen Framework")
    print("Version 2.0.0")
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def copy_data_between_agents(base_path: Path):
    """Copy output from one agent to input of next agent"""
    
    # Template Builder → Content Generator
    source = base_path / "Template_Builder_Agent/Outputs/customized_rfx_template.json"
    target = base_path / "Content_Generation_Agent/Inputs/customized_template_from_TBA.json"
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(source, 'r') as f:
            data = json.load(f)
        with open(target, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Content Generator → Distributor
    source = base_path / "Content_Generation_Agent/Outputs/drafted_rfx_document.json"
    target = base_path / "Distribution_Agent/Inputs/drafted_rfx_from_CGA.json"
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(source, 'r') as f:
            data = json.load(f)
        with open(target, 'w') as f:
            json.dump(data, f, indent=2)


def run_autogen_workflow():
    """
    Run RFX workflow using AutoGen framework
    
    Returns:
        Workflow execution result
    """
    # Get base path
    base_path = Path(__file__).parent / "Issue_RFX_Workflow_Data"
    
    if not base_path.exists():
        print(f"ERROR: Workflow data directory not found: {base_path}")
        return {"status": "error", "message": "Workflow data not found"}
    
    # Get LLM configuration
    llm_config = get_llm_config()
    
    # Check if LLM is available
    has_llm = len(llm_config.get("config_list", [])) > 0
    
    if has_llm:
        print("✓ AutoGen configured with Azure OpenAI")
    else:
        print("⚠ Running in rule-based mode (no LLM configured)")
    
    print(f"Workflow Data Path: {base_path}\n")
    
    # Create agent functions
    build_template = create_template_builder_function(str(base_path), llm_config)
    generate_content = create_content_generation_function(str(base_path), llm_config)
    distribute_rfx = create_distribution_function(str(base_path), llm_config)
    log_audit = create_audit_logger_function(str(base_path), llm_config)
    
    print("="*70)
    print("EXECUTING AUTOGEN WORKFLOW")
    print("="*70)
    
    results = []
    rfx_id = None
    
    try:
        # Step 1: Template Building
        print("\nStep 1: Template Builder Agent")
        template_result = build_template()
        template_data = json.loads(template_result)
        results.append({
            "agent": "Template_Builder_Agent",
            "status": template_data.get("status"),
            "message": template_data.get("message")
        })
        
        if template_data.get("status") == "success":
            rfx_id = template_data.get("rfx_id")
            copy_data_between_agents(base_path)
        else:
            raise Exception("Template building failed")
        
        # Step 2: Content Generation
        print("\nStep 2: Content Generation Agent")
        content_result = generate_content()
        content_data = json.loads(content_result)
        results.append({
            "agent": "Content_Generation_Agent",
            "status": content_data.get("status"),
            "message": content_data.get("message")
        })
        
        if content_data.get("status") == "success":
            copy_data_between_agents(base_path)
        else:
            raise Exception("Content generation failed")
        
        # Step 3: Distribution
        print("\nStep 3: Distribution Agent")
        dist_result = distribute_rfx()
        dist_data = json.loads(dist_result)
        results.append({
            "agent": "Distribution_Agent",
            "status": dist_data.get("status"),
            "message": dist_data.get("message")
        })
        
        if dist_data.get("status") != "success":
            raise Exception("Distribution failed")
        
        # Step 4: Audit Logging
        print("\nStep 4: Audit Logger Agent")
        audit_result = log_audit()
        audit_data = json.loads(audit_result)
        results.append({
            "agent": "Audit_Logger_Agent",
            "status": audit_data.get("status"),
            "message": audit_data.get("message")
        })
        
        print("\n" + "="*70)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*70)
        
        return {
            "status": "success",
            "rfx_id": rfx_id,
            "message": "RFX workflow completed successfully",
            "workflow_results": results,
            "framework": "AutoGen"
        }
        
    except Exception as e:
        print(f"\n✗ Workflow Error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "workflow_results": results
        }


def print_summary(result: dict):
    """Print workflow summary"""
    print("\n" + "="*70)
    print("WORKFLOW EXECUTION SUMMARY")
    print("="*70)
    
    print(f"\nFramework: Microsoft AutoGen")
    print(f"Status: {result.get('status', 'unknown').upper()}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if 'rfx_id' in result:
        print(f"RFX ID: {result['rfx_id']}")
    
    if 'workflow_results' in result:
        print("\n" + "-"*70)
        print("AGENT EXECUTION DETAILS")
        print("-"*70)
        
        for idx, agent_result in enumerate(result['workflow_results'], 1):
            agent = agent_result.get('agent', 'Unknown')
            status = agent_result.get('status', 'unknown')
            message = agent_result.get('message', 'N/A')
            
            status_symbol = "✓" if status == 'success' else "✗"
            print(f"\n{idx}. {agent}")
            print(f"   {status_symbol} {status.upper()}: {message}")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    try:
        # Print banner
        print_banner()
        
        # Run AutoGen workflow
        result = run_autogen_workflow()
        
        # Print summary
        print_summary(result)
        
        # Save execution report
        report_path = Path(__file__).parent / "Issue_RFX_Workflow_Data" / "execution_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                'execution_timestamp': datetime.now().isoformat(),
                'framework': 'Microsoft AutoGen',
                'workflow_result': result
            }, f, indent=2)
        
        print(f"Execution report saved to: {report_path}")
        
        # Return exit code
        if result.get('status') == 'success':
            print("\n✓ Workflow completed successfully!")
            return 0
        else:
            print("\n✗ Workflow completed with errors.")
            return 1
        
    except Exception as e:
        print(f"\n{'='*70}")
        print("CRITICAL ERROR")
        print("="*70)
        print(f"Error: {str(e)}")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
