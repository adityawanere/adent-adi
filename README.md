# Agent-Adi

Agent-Adi is an intelligent automation agent built in Python that can process
natural language commands and automate application restarts via GitHub. It is
designed for enterprise environments where automation and seamless integration
with GitHub are required.

## Features

- **Natural Language Command Processing**: Accepts user commands and routes them
  to the correct action.
- **Application Restart Automation**: Validates customer/environment
  combinations and automates GitHub PR creation, approval, and merging for
  restarts.
- **Extensible Architecture**: Easily add new actions or integrate with other AI
  providers (OpenAI, MCP server, etc.).

## Project Structure

```
Agent-Adi/
├── actions.py                # Core agent actions (restart)
├── main.py                   # Main agent loop and user interface
├── restart_prompt.py         # System prompt for restart automation
├── prompts.py                # General system prompts
├── json_helpers.py           # JSON extraction helpers
├── customers.csv             # Customer/environment mappings
├── Adi-Agent-venv/           # Python virtual environment
├── .env                      # Environment variables (API keys, repo info)
├── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the Repository**

   ```powershell
   git clone https://github.com/adityawanere/agent-adi.git
   cd agent-adi
   ```

2. **Create and Activate Virtual Environment**

   ```powershell
   python -m venv Adi-Agent-venv
   .\Adi-Agent-venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**

```powershell
pip install -r requirements.txt
pip install python-dotenv openai
```

4. **Configure Environment Variables**

   - Create a `.env` file in the project root:
     ```
     GITHUB_TOKEN=your_github_token_here
     REPO_OWNER=adityawanere
     REPO_NAME=agent-adi
     ```
   - Replace `your_github_token_here` with your actual GitHub token.

5. **Run the Agent**

```powershell
python main.py
```

- Enter your restart command.

## Usage Examples

- **Restart Application**:

  - "Restart AC15 in dv01 environment"
  - Agent will validate, create a PR, and automate the restart process.

## Integrating MCP Server

To use an MCP server for AI inference:

- Deploy or run an MCP server and obtain its endpoint URL.
- Update `main.py` to send requests to the MCP server instead of OpenAI.
- Store MCP server URL and credentials in `.env`.
- Refactor the model call logic to use MCP’s API.

## Extending the Agent

- Add new actions to `actions.py` and update `available_actions` in `main.py`.
- Create new prompts in `prompts.py` or dedicated prompt files.
- Integrate other AI providers by updating the model call logic.

## License

MIT License

## Author

Aditya Wanere

---

For questions or support, open an issue on
[GitHub](https://github.com/adityawanere/agent-adi).
