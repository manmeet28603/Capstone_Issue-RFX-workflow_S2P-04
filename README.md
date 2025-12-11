# RFX Workflow Automation System

An intelligent multi-agent system for automating the "Issue RFX" workflow in the Source-to-Pay (S2P) procurement process, built with **Microsoft AutoGen Framework**.

## Overview

This system automates the complete Request for X (RFX) creation and distribution process using coordinated AI agents powered by AutoGen that work together to:
- Select and customize appropriate RFX templates based on procurement requirements
- Generate complete RFX documents with SAP-compliant fields
- Distribute RFX packages to qualified suppliers
- Maintain comprehensive audit trails for compliance

## Architecture

### Multi-Agent System

The system consists of 5 specialized agents orchestrated to execute the RFX workflow:

#### 1. **Template Builder Agent**
- Analyzes procurement requirements (material type, category, specifications)
- Intelligently selects the most relevant historical RFX template
- Customizes the template with current requirements
- Generates unique RFX ID and SAP metadata

#### 2. **Content Generation Agent**
- Populates the customized template with detailed content
- Generates SAP-compliant headers (BUKRS, EKORG, EKGRP, BSART)
- Creates line items with material specifications (MATNR, MENGE, MEINS)
- Validates document completeness and accuracy

#### 3. **Distribution Agent**
- Loads supplier shortlists based on category and region
- Creates RFX packages with attachments
- Distributes to qualified suppliers via portal
- Tracks delivery status and confirmation

#### 4. **Audit Logger Agent**
- Captures all workflow events with timestamps
- Ensures compliance and traceability
- Validates audit trail completeness
- Stores centralized logs for reporting

#### 5. **Orchestration Agent**
- Coordinates execution across all agents
- Manages data flow between agents
- Handles exceptions and error recovery
- Validates inputs and outputs

## Technology Stack

- **Microsoft AutoGen**: Multi-agent orchestration framework
- **Python 3.12+**: Core programming language
- **Azure OpenAI GPT-4o**: LLM integration for intelligent decision-making
- **SAP ERP**: Integration with enterprise resource planning fields
- **JSON**: Data exchange format between agents

## Key Features

### SAP Integration
Full support for SAP procurement fields:
- **BUKRS**: Company Code
- **EKORG**: Purchasing Organization
- **EKGRP**: Purchasing Group
- **MATNR**: Material Number
- **MATKL**: Material Group
- **WAERS**: Currency
- **WERKS**: Plant
- **BSART**: Document Type
- **LIFNR**: Supplier Number
- **INCO1/INCO2**: Incoterms
- **ZTERM**: Payment Terms

### Intelligent Template Selection
The system uses historical RFX templates across multiple categories:
- **Chemicals**: Glycerin, Solvents, Fragrances
- **Packaging**: HDPE, Bottles, Labels
- **Logistics**: Sea freight, Air freight, Warehousing
- **Raw Materials**: Various industrial materials

### Compliance & Audit
- Complete event logging with timestamps
- Validation at each workflow step
- Traceability from requirement to distribution
- Compliance-ready audit trails

## Installation

### Prerequisites
- Python 3.12 or higher
- Azure OpenAI account (optional - system works in fallback mode without it)

### Setup

1. **Clone or download the project**

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create a `.env` file in the project root:
```env
openai_api_type=azure
openai_api_base=https://your-endpoint.openai.azure.com/
openai_api_version=2025-01-01-preview
openai_api_key=your-api-key-here
openai_engine_name=gpt-4o
```

## Usage

### Run Complete Workflow
```bash
python main.py
```

This executes the full RFX workflow:
1. Template selection and customization
2. RFX document generation
3. Supplier distribution
4. Audit logging

## Workflow Example

**Input Requirements:**
```json
{
  "category": "Chemical",
  "material": "Refined Glycerin",
  "grade": "USP/Pharma",
  "annual_volume_mt": 6000,
  "plants": ["US01", "US02"]
}
```

**System Actions:**
1. Selects historical glycerin RFP template (TPL-RFP-CHEM-GLYC-2023)
2. Generates RFX ID: `2000-GLYC-2025-RFP-###`
3. Creates document with SAP fields and line items
4. Distributes to qualified chemical suppliers
5. Logs complete audit trail

**Execution Time:** ~5 seconds

## Project Structure

```
├── agents/                          # AutoGen-powered AI agents
│   ├── template_builder_agent.py   # Template selection
│   ├── content_generation_agent.py # RFX document creation
│   ├── distribution_agent.py       # Supplier distribution
│   └── audit_logger_agent.py       # Compliance logging
├── Issue_RFX_Workflow_Data/        # Input/output data
├── utils/                           # Utility functions
├── autogen_config.py               # AutoGen configuration
├── main.py                         # Main execution script
├── requirements.txt                # Dependencies
└── README.md                       # Documentation
```

## License

Proprietary - Source-to-Pay Procurement Automation

## System Status Check

Verify system health:
```bash
python check_system.py
```

Validates:
- Environment configuration
- Required dependencies
- LLM service connectivity
- Data file availability

## Project Structure

```
04. Issue RFX workflow_S2P/
├── agents/
│   ├── template_builder_agent.py      # Template selection & customization
│   ├── content_generation_agent.py    # RFX document drafting
│   ├── distribution_agent.py          # Supplier distribution
│   ├── audit_logger_agent.py          # Compliance logging
│   └── orchestration_agent.py         # Workflow coordination
├── utils/
│   ├── llm_service.py                 # Azure OpenAI integration
│   └── workflow_utils.py              # Helper functions
├── config/
│   └── workflow_config.py             # System configuration
├── Issue_RFX_Workflow_Data/
│   ├── company_profile.json
│   ├── sap_field_dictionary.json
│   └── [Agent Data Sources & Outputs]
├── main.py                            # Main execution script
├── check_system.py                    # System validation
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Benefits

### Efficiency
- **Speed**: Complete RFX workflow in seconds vs. hours manually
- **Automation**: Zero manual intervention required
- **Scale**: Handle multiple RFXs simultaneously

### Accuracy
- **SAP Compliance**: All fields validated against SAP standards
- **Template Reuse**: Proven templates from successful RFXs
- **Validation**: Multi-stage verification at each step

### Intelligence
- **Context-Aware**: Understands procurement requirements semantically
- **Learning**: Leverages historical data for better decisions
- **Adaptive**: Falls back gracefully when external services unavailable

### Compliance
- **Complete Audit Trail**: Every action logged with timestamp
- **Traceability**: Full workflow history from start to finish
- **Validation**: Automated compliance checks

## Use Cases

1. **Commodity Procurement**: Chemicals, packaging materials, raw materials
2. **Service RFPs**: Logistics, warehousing, consulting
3. **Strategic Sourcing**: Long-term supplier partnerships
4. **Emergency Sourcing**: Quick RFX turnaround for urgent needs

## Future Enhancements

- Real-time supplier portal integration
- Bid response collection and analysis
- Contract generation from awarded RFXs
- Advanced analytics and reporting dashboard
- Multi-language support for global suppliers

## Support

For questions or issues with the RFX Workflow Automation System, contact your procurement technology team.

---

**Version:** 1.0.0  
**Last Updated:** December 11, 2025  
**Powered by:** Agentic AI
