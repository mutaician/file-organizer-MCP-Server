# File Organizer MCP Server

A Model Context Protocol (MCP) server that uses Google's Gemini Vision API to analyze screenshots of file listings/course contents and automatically organize files based on the extracted order.

## Features

- Screenshot Analysis: Uses Gemini Vision API to extract file organization order from screenshots
- Smart File Organization: Matches files with extracted order and renames them with numeric prefixes
- Descriptive Folders: Creates section-specific folders based on content type
- AI/OCR Handling: Robust handling of common OCR variations (e.g., AI vs Al)
- Undo Support: Can revert organized files back to their original state

## Prerequisites

- Python 3.13+
- Visual Studio Code
- Google API key for Gemini Vision API
- MCP Extension for VS Code
- `uv` package manager (recommended) or pip

## Setup

1. Clone the repository:
```bash{:copy}
git clone https://github.com/mutaician/file-organizer-MCP-Server.git
cd file-organizer-mcp
```

2. Create and activate virtual environment using uv:
```bash{:copy}
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

3. Install VS Code MCP Extension:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Install the GitHub Copilot extension (or any extension that supports MCP servers).

4. Configure VS Code workspace:
   - Create `.vscode` folder if it doesn't exist
   - Add `mcp.json` with the following content:
   ```json
   {
     "inputs": [
       {
         "type": "promptString",
         "id": "gemini-key",
         "description": "Gemini API Key",
         "password": true
       }
     ],
     "servers": {
       "File Organizer": {
         "type": "stdio",
         "command": "\${workspaceFolder}/.venv/bin/python",
         "args": ["\${workspaceFolder}/src/server.py"],
         "env": {
           "GOOGLE_API_KEY": "\${input:gemini-key}"
         }
       }
     }
   }
   ```

## Usage in VS Code

1. Start the MCP Server:
   - Open Command Palette (Ctrl+Shift+P)
   - Type "MCP: List Servers"
   - Select "File Organizer"
   - Enter your Gemini API key when prompted
   - You should now see your server and its tools available in the Copilot Chat/Agent mode.

2. In the Copilot Chat, you can organize your files by:
   - First, analyze a screenshot to get the file order:
     ```chat{:copy}
     Could you analyze the screenshot at "/path/to/screenshot.jpg"?
     ```
   - Then organize files using the extracted order:
     ```chat{:copy}
     Could you organize the files in "/path/to/section" using this order?
     ```
   - The server will automatically:
     - Create a descriptive subfolder based on the section title
     - Number files according to their order
     - Handle AI/OCR variations
   
3. Additional Commands:
   - List files in a directory:
     ```chat{:copy}
     Could you list the files in "/path/to/directory"?
     ```
   - Undo organization:
     ```chat{:copy}
     Could you undo the organization from "/path/to/organized" back to "/path/to/source"?
     ```

4. Best Practices:
   - Keep screenshots clear and well-lit for better OCR
   - Verify organization results after each operation
   - Use the undo function if needed before trying again

## Key Concepts

1. **Screenshot Analysis**:
   - Takes a screenshot of your desired file organization (e.g., course content listing)
   - Uses Gemini Vision to extract the order and hierarchy
   - Handles numbered lists and various formats

2. **File Organization**:
   - Matches files to the extracted order
   - Adds numeric prefixes (e.g., "01_", "02_")
   - Creates descriptive subfolders based on content type
   - Preserves original filenames after the prefix

3. **Smart Matching**:
   - Handles variations in OCR text (AI vs Al)
   - Ignores case sensitivity
   - Removes special characters that might interfere
   - Matches partial names when appropriate

## Troubleshooting

- If files aren't matching correctly:
  - Check for special characters in filenames
  - Verify the screenshot text is clear and readable
  - Ensure file extensions are correct

- If the server won't start:
  - Verify your Gemini API key is valid
  - Check Python virtual environment is activated
  - Ensure all dependencies are installed

## Dependencies

- `mcp-sdk`: Model Context Protocol implementation
- `google-generativeai`: Gemini AI API client
- `pillow`: Image processing for screenshots

