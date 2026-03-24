import os
import sys
import json
import re

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not found. To use this feature, install it via: pip install openai")
    sys.exit(0)

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
        return ""

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"[+] Successfully wrote {filepath}")

def extract_code_block(text, language):
    # Matches ```language \n ... \n ```
    pattern = rf"```{language}\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)

    # Fallback if the LLM didn't specify the language
    pattern_fallback = r"```\n(.*?)```"
    match_fallback = re.search(pattern_fallback, text, re.DOTALL)
    if match_fallback:
        return match_fallback.group(1)

    return ""

def main():
    print("🤖 Starting Continuous Code-Generating Meta-Agent...")

    # Load the prompt and the rules
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(root_dir, 'meta_agent_prompt.md')
    rules_path = os.path.join(root_dir, 'GAMERULES.md')

    system_prompt = read_file(prompt_path)
    game_rules = read_file(rules_path)

    if not system_prompt or not game_rules:
        print("Missing prompt or rules. Exiting.")
        sys.exit(1)

    api_key = os.environ.get("ENTERPRISE_AI_KEY")
    if not api_key:
        print("[!] No ENTERPRISE_AI_KEY found in environment.")
        print("    Running in dry-run/simulation mode. No API call will be made.")
        # In dry run mode, we simulate what the LLM *would* have returned.
        llm_response = """
Here is the generated architecture based on the provided rules.

```json
{
  "game_name": "DynamicGame",
  "estimated_state_space_size": "unknown",
  "chosen_algorithm": "q_table",
  "state_representation": "string array",
  "action_representation": "integer index",
  "reward_structure": "1 win, -1 loss, 0 draw"
}
```

```python
# env.py
class GameEnv:
    def __init__(self):
        self.state = []
    def reset(self):
        return self.state
    def step(self, action):
        return self.state, 0, False
```

```html
<!-- index.html -->
<div><h1>Dynamically Generated Game UI</h1></div>
```

```javascript
// app.js
console.log("Dynamically Generated Game Logic Loaded.");
```
"""
    else:
        # Actually call the Enterprise LLM API
        print("Connecting to Enterprise LLM...")

        # Safely handle base_url
        base_url = os.environ.get("ENTERPRISE_AI_BASE")
        client_kwargs = {"api_key": api_key}
        if base_url and base_url.strip():
            client_kwargs["base_url"] = base_url.strip()

        client = OpenAI(**client_kwargs)

        try:
            response = client.chat.completions.create(
                model="gpt-4o", # Replace with your enterprise model name
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"# GAMERULES.md\n{game_rules}"}
                ],
                temperature=0.2
            )
            llm_response = response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            sys.exit(1)

    print("Parsing LLM Output...")

    # Extract the generated code blocks
    json_config = extract_code_block(llm_response, "json")
    python_env = extract_code_block(llm_response, "python")
    html_ui = extract_code_block(llm_response, "html")
    js_logic = extract_code_block(llm_response, "javascript")

    # Define paths where the dynamically generated code will live
    projects_dir = os.path.join(root_dir, 'projects', 'dynamic_game')
    docs_dir = os.path.join(root_dir, 'docs') # The web UI

    if json_config: write_file(os.path.join(projects_dir, 'model_config.json'), json_config)
    if python_env: write_file(os.path.join(projects_dir, 'env.py'), python_env)

    # Overwrite the static frontend with the newly generated one
    if html_ui: write_file(os.path.join(docs_dir, 'index.html'), html_ui)
    if js_logic: write_file(os.path.join(docs_dir, 'app.js'), js_logic)

    print("✅ Meta-Agent completed code generation successfully.")

if __name__ == "__main__":
    main()
