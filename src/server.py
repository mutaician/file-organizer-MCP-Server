from mcp.server.fastmcp import FastMCP
import google.generativeai as genai
from PIL import Image
import os
import logging

# Initialize MCP server
mcp = FastMCP("file-organizer")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
def init_gemini(api_key: str):
    """Initialize Gemini with API key."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

@mcp.tool()
async def analyze_screenshot(screenshot_path: str) -> str:
    """Analyze screenshot to extract file organization order.
    
    Args:
        screenshot_path: Path to screenshot containing organization order
    """
    try:
        # Validate image path
        if not os.path.exists(screenshot_path):
            return f"Error: Screenshot not found at {screenshot_path}"

        # Load and process image
        image = Image.open(screenshot_path)
        
        # Initialize Gemini
        model = init_gemini(os.getenv('GEMINI_API_KEY'))
        
        # Use Gemini to analyze the image
        response = model.generate_content([
            "Analyze this screenshot and extract the file organization order together with section title if present. " +
            "Return the order as a numbered list of file names or patterns, and the title " +
            "Format the response as section title and simple numbered list of filenames, one per line.",
            image
        ])
        
        return response.text
    except Exception as e:
        logger.error(f"Error analyzing screenshot: {str(e)}")
        return f"Error analyzing screenshot: {str(e)}"

@mcp.tool()
async def organize_files(
    folder_path: str,
    organization_order: str,
    output_folder: str
) -> str:
    """Organize files based on the provided order.
    
    Args:
        folder_path: Path to folder containing files to organize
        organization_order: Order of files extracted from screenshot
        output_folder: Path to output folder for organized files (use section title if present)
    """
    try:
        # Validate paths
        if not os.path.exists(folder_path):
            return f"Error: Source folder not found at {folder_path}"
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Parse organization order into a list of titles
        order_list = []
        for line in organization_order.split('\n'):
            if not line.strip():
                continue
            # Remove the number and duration, keep just the title
            title = line.split('(')[0].strip()
            if '. ' in title:
                title = title.split('. ', 1)[1]
            # Clean up special characters that might interfere with matching
            title = title.replace(':', '').replace('?', '').strip()
            # Handle AI/Al variations more comprehensively
            title = (title.lower()
                    .replace('openal', 'openai')
                    .replace('genal', 'genai')
                    .replace(' al ', ' ai '))
            order_list.append(title)
        
        # Get list of files in source folder
        source_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        file_positions = {}  # Will store {filename: position}
        
        # Match files to their positions in order_list
        for file in source_files:
            file_lower = file.lower()
            for pos, title in enumerate(order_list):
                # Convert the title into a simple string to match against filename
                if title in file_lower:
                    file_positions[file] = pos
                    break
        
        # Sort files by their matched positions
        organized_files = sorted(file_positions.keys(), key=lambda x: file_positions[x])
        
        # Move files with numeric prefixes
        organized_count = 0
        for idx, file in enumerate(organized_files, 1):
            # Create new filename with numeric prefix
            base_name = file
            new_name = f"{idx:02d}_{base_name}"
            
            src_path = os.path.join(folder_path, file)
            dst_path = os.path.join(output_folder, new_name)
            os.rename(src_path, dst_path)
            organized_count += 1
        
        return f"Successfully organized {organized_count} files to {output_folder}"
    except Exception as e:
        logger.error(f"Error organizing files: {str(e)}")
        return f"Error organizing files: {str(e)}"

@mcp.tool()
async def undo_organization(
    organized_folder: str,
    source_folder: str
) -> str:
    """Undo the file organization by moving files back and removing numeric prefixes.
    
    Args:
        organized_folder: Path to folder containing organized files
        source_folder: Path to original source folder
    """
    try:
        # Validate paths
        if not os.path.exists(organized_folder):
            return f"Error: Organized folder not found at {organized_folder}"
        if not os.path.exists(source_folder):
            return f"Error: Source folder not found at {source_folder}"
            
        # Get list of organized files
        organized_files = [f for f in os.listdir(organized_folder) if os.path.isfile(os.path.join(organized_folder, f))]
        
        moved_count = 0
        for file in organized_files:
            if len(file) > 3 and file[2] == '_':  # Check if file has the numeric prefix pattern
                # Remove numeric prefix (first 3 characters)
                original_name = file[3:]
                
                # Define paths
                src_path = os.path.join(organized_folder, file)
                dst_path = os.path.join(source_folder, original_name)
                
                # Move file back to source directory
                os.rename(src_path, dst_path)
                moved_count += 1
        
        return f"Successfully moved {moved_count} files back to {source_folder} and removed numeric prefixes"
    except Exception as e:
        logger.error(f"Error undoing organization: {str(e)}")
        return f"Error undoing organization: {str(e)}"

@mcp.tool()
async def list_files(folder_path: str) -> str:
    """List all files in the specified folder.
    
    Args:
        folder_path: Path to folder to list files from
    """
    try:
        if not os.path.exists(folder_path):
            return f"Error: Folder not found at {folder_path}"
            
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return "\n".join(files)
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return f"Error listing files: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')