from src.sandbox import Sandbox
from src.attacks.jailbreaks import basic_prompt_injection
from src.attacks.jailbreaks import unicode_bypass

# Create the sandbox environment
sandbox = Sandbox()

# Generate the attack input
attack_prompt = basic_prompt_injection()

# Run the attack through the model
response = sandbox.run(attack_prompt)

print("Attack Prompt:", attack_prompt)
print("Model Response:", response)

# Test Unicode bypass attack
bypass_prompt = unicode_bypass()
bypass_response = sandbox.run(bypass_prompt)

print("\nBypass Attack Prompt:", bypass_prompt)
print("Model Response:", bypass_response)