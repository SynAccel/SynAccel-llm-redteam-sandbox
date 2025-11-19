# SynAccel-llm-redteam-sandbox
Sandbox for testing LLM prompt injections, jailbreaks, and AI red teaming techniques, part of the SynAccel Mirage line


## SynAccel Update — 11/19/2025

The SynAccel Mirage AI Red Teaming Sandbox reached its initial functional milestone today.  
Core components were established to support future AI security research and automated attack simulation.

### Key Developments
- Established baseline project structure for models, attack modules, sandbox logic, and testing utilities.
- Implemented the `DummyLLM` model to simulate foundational large-language-model behavior, including:
  - Internal system prompt
  - Basic response generation
  - Simulated vulnerability to prompt-based attacks
- Developed the `Sandbox` environment responsible for:
  - Model execution control
  - Safety-layer enforcement
  - Input routing and response handling
- Added initial attack modules:
  - Baseline prompt injection attempting system-prompt extraction
  - Unicode homoglyph-based bypass designed to circumvent naive keyword filters
- Verified the full pipeline end-to-end via structured tests in `tests/test_sandbox.py`.

### Technical Insights
- Demonstrated the limitations of keyword-based safety controls.
- Confirmed that Unicode homoglyph substitution successfully evades both sandbox filtering and model-level detection.
- Validated core concepts used in real AI red teaming workflows:
  - Prompt injection
  - Filter bypass strategies
  - Safety-layer evaluation