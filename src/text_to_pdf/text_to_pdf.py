import os
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from dotenv import load_dotenv
import re
import gc

load_dotenv()  # Load environment variables from .env file

class StudyGuideGenerator:
    def __init__(self, openai_api_key=None):
        # Use provided API key or fall back to environment variable
        self.client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        self.styles = self._setup_styles()
    
    def _setup_styles(self):
        """Initialize ReportLab styles."""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(name='MainHeader', parent=styles['Heading1'], fontSize=18, spaceBefore=20))
        styles.add(ParagraphStyle(name='SubHeader', parent=styles['Heading2'], fontSize=14, spaceBefore=12))
        styles.add(ParagraphStyle(name='ThirdHeader', parent=styles['Heading3'], fontSize=12, spaceBefore=10, spaceAfter=6))
        styles.add(ParagraphStyle(name='FourthHeader', parent=styles['Heading4'], fontSize=11, spaceBefore=8, spaceAfter=6, textColor=colors.grey))
        styles.add(ParagraphStyle(name='BulletText', parent=styles['BodyText'], leftIndent=15, bulletFontSize=10))
        styles.add(ParagraphStyle(name='ImportantNote', parent=styles['BodyText'], borderColor=colors.grey, borderWidth=1, borderPadding=8, backColor=colors.lightgrey, spaceBefore=10, spaceAfter=10))

        return styles
    
    def generate_study_guide_content(self, summary):
        """Use OpenAI API to create study guide content from summary."""
        messages = [
            {
                "role": "system",
                "content": """Please create a document following these guidelines:

# Document Structure

1. Use the following markdown formatting:
   - Main titles with '#'
   - Subtitles with '##'
   - Subsections with '###'
   - Important points with '####'
   - Italics for key terms using single *asterisks*
   - Bold for important phrases using **double asterisks**

2. Development Process:
   - Analyze each point from the summary document
   - Include practical examples for each main point
   - Maintain consistent formatting throughout

## Example Format:

# Main Title
## Section Title
### Subsection
#### Important Point
This is regular text with *italicized terms* and **bold important phrases**

> Note: The above format will generate a well-structured PDF using our current code. Remember using Spanish.
"""
            },
            {
                "role": "user",
                "content": "Transform the provided summary into a comprehensive study guide PDF based on the instructions:" + summary
            }
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=16384,
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    
    def create_pdf(self, content, output_path):
        """Generate PDF from structured content and save to output_path."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []

        # Process and add each line to the document
        for line in content.split('\n'):
            if not line.strip():
                continue

            # Replace markdown bold markers with HTML bold tags
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)

            # Replace markdown italic markers with HTML italic tags
            line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)

            # Add content based on markdown-like headers
            if line.startswith('# '):
                elements.append(Paragraph(line[2:], self.styles['MainHeader']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], self.styles['SubHeader']))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], self.styles['ThirdHeader']))
            elif line.startswith('#### '):
                elements.append(Paragraph(line[5:], self.styles['FourthHeader']))
            elif line.startswith('- '):
                elements.append(Paragraph(line[2:], self.styles['BulletText'], bulletText='•'))
            elif line.startswith('> '):
                elements.append(Paragraph(line[2:], self.styles['ImportantNote']))
            else:
                elements.append(Paragraph(line, self.styles['Normal']))

            elements.append(Spacer(1, 6))

        # Build the PDF
        doc.build(elements)
        del doc
        gc.collect()
        
    def create_study_guide(self, summary_path, output_path):
        """Generate a study guide PDF based on the summary file."""
        try:
            # Load the summary file
            with open(summary_path, "r", encoding="utf-8") as file:
                summary_content = file.read()

            # Generate the study guide content using OpenAI
            study_guide_content = self.generate_study_guide_content(summary_content)

            # Create the PDF and save it
            self.create_pdf(study_guide_content, output_path)

        except Exception as e:
            raise Exception(f"Error creating study guide: {str(e)}")

    def create_study_guide_from_text(self, summary_text: str, output_path: str):
        """
        Create a study guide PDF from a raw text string (rather than a file).
        This method directly calls the OpenAI API to refine the text into a 
        'study guide format,' then calls create_pdf(...) to build the final PDF.
        """
        try:
            # 1) Generate the study guide content using OpenAI
            study_guide_content = self.generate_study_guide_content(summary_text)

            # 2) Create the PDF
            self.create_pdf(study_guide_content, output_path)

        except Exception as e:
            raise Exception(f"Error creating study guide from text: {str(e)}")


if __name__ == "__main__":
    # Example usage (replace with actual paths as needed):
    summary_path = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\summary\transcription_summary.txt"
    output_path = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\output\study_guides\study_guide.pdf"

    generator = StudyGuideGenerator()
    generator.create_study_guide(summary_path, output_path)
