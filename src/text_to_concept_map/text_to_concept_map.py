import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_summary(file_path: Path) -> str:
    """Reads the summary content from a file."""
    with file_path.open("r", encoding="utf-8") as file:
        return file.read()

def extract_concept_map_elements(summary: str) -> dict:
    """Extracts core concept map elements (main topic, subtopics, supporting concepts) from the summary."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an expert at creating educational concept maps. Your task is to extract the main topic, subtopics, and supporting concepts from the following summary. You will return the following in JSON format:
                {
                    "main_topic": "Main Topic",
                    "subtopics": [
                        {"subtopic": "Subtopic 1", "concepts": ["Concept 1", "Concept 2"]},
                        {"subtopic": "Subtopic 2", "concepts": ["Concept 3", "Concept 4"]}
                    ]
                }
                The structure should focus on major themes from the summary.
                """
            },
            {
                "role": "user",
                "content": f"Extract the core elements for a concept map from this summary:\n\n{summary}"
            }
        ],
        temperature=0.2
    )
    
    elements = response.choices[0].message.content
    return elements  # Assumed that GPT will return a clean JSON string that can be parsed

def generate_mermaid_code_from_elements(elements: dict) -> str:
    """Generates Mermaid code based on the extracted elements."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an expert at generating educational concept maps in Mermaid flowchart format. Your task is to convert the following concept map elements into a valid Mermaid code:
                - Main Topic
                - Subtopics with their related concepts
                The output should be in Mermaid flowchart format (in Spanish) with rounded boxes. Example:
                
                ```mermaid
                flowchart LR
                    %% Concept Map Node Style Guide
                    classDef main fill:#f9f,stroke:#333,stroke-width:2px;
                    classDef sub fill:#ccf,stroke:#333,stroke-width:2px;
                    classDef default fill:#aaf,stroke:#333,stroke-width:2px;
                    Main["Main Topic"]:::main
                    Sub1["Subtopic 1"]:::sub
                    Concept1["Concept 1"]:::default
                    Main --> Sub1
                    Sub1 --> Concept1
                ```

                Ensure the structure follows the guidelines below:
                - Must start with 'flowchart LR'
                - Use red shades colors for each level using classDef
                - The connections between nodes should use arrows (e.g., --> or ---)
                - Only in Spanish
                - Return just the mermaid code without any markdown or explanations
                """
            },
            {
                "role": "user",
                "content": f"Generate Mermaid code for this concept map:\n\n{elements}"
            }
        ],
        temperature=0.2
    )
    
    mermaid_code = response.choices[0].message.content
    # Clean the mermaid code and ensure it starts with flowchart LR
    mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
    if not mermaid_code.startswith("flowchart LR"):
        mermaid_code = "flowchart LR\n" + mermaid_code
    return mermaid_code

def save_to_file(content: str, file_path: Path):
    """Saves content to a specified file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        file.write(content)

def set_png_dpi(png_path: Path, dpi: int):
    """Sets the DPI metadata for a PNG image using Pillow."""
    try:
        img = Image.open(png_path)
        img.save(png_path, dpi=(dpi, dpi))
        print(f"DPI set to {dpi} for: {png_path}")
    except Exception as e:
        print(f"Failed to set DPI for {png_path}: {e}")

def generate_concept_map(summary_path: Path, output_dir: Path) -> Path:
    """Generates a concept map based on a summary file.
    
    Args:
        summary_path (Path): Path to the summary file
        output_dir (Path): Directory where the concept map should be saved
        
    Returns:
        Path: Path to the generated PNG file
    """
    try:
        # Read the summary content
        print(f"Reading summary from: {summary_path}")
        summary = read_summary(summary_path)

        # Extract core concept map elements from the summary
        print("Extracting concept map elements using OpenAI...")
        elements = extract_concept_map_elements(summary)
        
        # Generate Mermaid code from the extracted elements
        print("Generating Mermaid code using OpenAI...")
        mermaid_code = generate_mermaid_code_from_elements(elements)

        # Save Mermaid code to a temporary .mmd file
        temp_mmd_path = output_dir / "temp.mmd"
        print(f"Saving Mermaid code to: {temp_mmd_path}")
        save_to_file(mermaid_code, temp_mmd_path)

        # Define output file names
        base_file_name = f"concept_map_{summary_path.stem.replace('summary_', '')}"
        output_png_path = output_dir / f"{base_file_name}.png"

        # Generate PNG using mermaid-cli
        print(f"Generating high-resolution PNG: {output_png_path}")
        command_png = [
            r"C:\Users\esanchezb\AppData\Roaming\npm\mmdc.cmd",
            "-i", str(temp_mmd_path),
            "-o", str(output_png_path),
            "-s", "4",  # Scale factor for resolution
            "-t", "default",
            "-b", "transparent"
        ]
        
        print("Running command:", command_png)
        subprocess.run(command_png, check=True)
        print(f"PNG generated at: {output_png_path}")

        # Set DPI metadata for the PNG
        dpi = 300
        set_png_dpi(output_png_path, dpi)

        # Clean up temporary .mmd file
        temp_mmd_path.unlink()
        print(f"Concept map successfully generated at: {output_png_path}")

        return output_png_path  # Return the path to the generated PNG

    except subprocess.CalledProcessError as cpe:
        print(f"Mermaid CLI failed: {cpe}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def generate_concept_map_from_text(summary_text: str, output_dir: Path) -> Path:
    """
    Generates a concept map PNG from raw text (rather than reading a file).
    
    Args:
        summary_text (str): The raw summary text to process.
        output_dir (Path): Directory where the concept map should be saved.
    
    Returns:
        Path: Path to the generated PNG file.
    """
    try:
        print("Extracting concept map elements using OpenAI...")
        elements = extract_concept_map_elements(summary_text)

        print("Generating Mermaid code using OpenAI...")
        mermaid_code = generate_mermaid_code_from_elements(elements)

        # Save Mermaid code to a temporary .mmd file
        temp_mmd_path = output_dir / "temp.mmd"
        print(f"Saving Mermaid code to: {temp_mmd_path}")
        save_to_file(mermaid_code, temp_mmd_path)

        # Define output file names
        # Using a generic name; or you can do something like 'concept_map_inmemory'
        base_file_name = "concept_map_inmemory"
        output_png_path = output_dir / f"{base_file_name}.png"

        # Generate PNG using mermaid-cli
        print(f"Generating high-resolution PNG: {output_png_path}")
        command_png = [
            r"C:\Users\esanchezb\AppData\Roaming\npm\mmdc.cmd",
            "-i", str(temp_mmd_path),
            "-o", str(output_png_path),
            "-s", "4",
            "-t", "default",
            "-b", "transparent"
        ]

        print("Running command:", command_png)
        subprocess.run(command_png, check=True)
        print(f"PNG generated at: {output_png_path}")

        # Set DPI metadata for the PNG
        dpi = 300
        set_png_dpi(output_png_path, dpi)

        # Clean up temporary .mmd file
        temp_mmd_path.unlink()
        print(f"Concept map successfully generated at: {output_png_path}")

        return output_png_path

    except subprocess.CalledProcessError as cpe:
        print(f"Mermaid CLI failed: {cpe}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def main():
    """Main execution function."""
    # Example paths (replace with actual paths as needed)
    summary_path = Path(r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\summary\transcription_summary.txt")
    output_dir = Path(r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\output\concept_map")
    
    # Generate the concept map
    generate_concept_map(summary_path, output_dir)

if __name__ == "__main__":
    main()