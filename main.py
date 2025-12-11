import json
import sys
from pathlib import Path
from datetime import datetime

from autogen_config import get_llm_config
from agents.orchestration_agent import create_orchestration_function


def print_banner():
    print("\n" + "="*70)
    print(" "*10 + "RFX WORKFLOW AUTOMATION SYSTEM - AUTOGEN")
    print(" "*10 + "Source-to-Pay (S2P) - Issue RFX Process")
    print("="*70)
    print("\nPowered by Microsoft AutoGen Framework")
    print("Version 2.0.0")
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")





def run_autogen_workflow():
    base_path = Path(__file__).parent / "Issue_RFX_Workflow_Data"
    
    if not base_path.exists():
        print(f"ERROR: Workflow data directory not found: {base_path}")
        return {"status": "error", "message": "Workflow data not found"}
    
    llm_config = get_llm_config()
    has_llm = len(llm_config.get("config_list", [])) > 0
    
    if has_llm:
        print("✓ AutoGen configured with Azure OpenAI")
    else:
        print("⚠ Running in rule-based mode (no LLM configured)")
    
    print(f"Workflow Data Path: {base_path}\n")
    
    run_orchestrated = create_orchestration_function(str(base_path), llm_config)
    result_str = run_orchestrated()
    result = json.loads(result_str)
    
    return result


def print_summary(result: dict):
    print("\n" + "="*70)
    print("WORKFLOW EXECUTION SUMMARY")
    print("="*70)
    
    print(f"\nFramework: Microsoft AutoGen with Orchestration")
    print(f"Status: {result.get('status', 'unknown').upper()}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if 'rfx_id' in result:
        print(f"RFX ID: {result['rfx_id']}")
    
    if 'workflow_results' in result:
        print("\n" + "-"*70)
        print("AGENT EXECUTION DETAILS")
        print("-"*70)
        
        for idx, agent_result in enumerate(result['workflow_results'], 1):
            agent_id = agent_result.get('agent_id', agent_result.get('agent', 'Unknown'))
            status = agent_result.get('status', 'unknown')
            message = agent_result.get('message', 'N/A')
            
            status_symbol = "✓" if status == 'success' else "✗"
            print(f"\n{idx}. {agent_id}")
            print(f"   {status_symbol} {status.upper()}: {message}")
            
            # Print validation status if available
            if 'validation' in agent_result:
                validation = agent_result['validation']
                val_status = "PASS" if validation.get('valid') else "FAIL"
                print(f"   Validation: {val_status}")
                if validation.get('issues'):
                    print(f"   Issues: {', '.join(validation['issues'])}")
    
    # Print exceptions if any
    if 'exceptions' in result and result['exceptions']:
        print("\n" + "-"*70)
        print("EXCEPTIONS HANDLED")
        print("-"*70)
        
        for idx, exception in enumerate(result['exceptions'], 1):
            print(f"\n{idx}. Agent: {exception.get('agent_id', 'Unknown')}")
            print(f"   Status: {exception.get('resolution_status', 'Unknown')}")
            if exception.get('error', {}).get('issues'):
                print(f"   Issues: {', '.join(exception['error']['issues'])}")
    
    # Print stakeholder requests if any
    if 'stakeholder_requests' in result and result['stakeholder_requests']:
        print("\n" + "-"*70)
        print("STAKEHOLDER REQUESTS")
        print("-"*70)
        
        for idx, request in enumerate(result['stakeholder_requests'], 1):
            print(f"\n{idx}. Request ID: {request.get('request_id', 'Unknown')}")
            print(f"   Agent: {request.get('agent_id', 'Unknown')}")
            print(f"   Status: {request.get('status', 'Unknown')}")
    
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
