import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

class Summarizer:
    """Class to handle OpenAI-based content summarization and analysis."""

    def __init__(self):
        """Initialize the Summarizer with OpenAI client."""
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)

    def _read_transcription(self, file_path: str) -> str:
        """Read transcription from file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Transcription file not found at: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading transcription: {str(e)}")

    def _save_summary(self, content: str, file_path: str) -> None:
        """Save summary to file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise Exception(f"Error saving summary: {str(e)}")

    def _get_analysis_prompt(self, transcription: str) -> str:
        """Generate the analysis prompt with the original structure."""
        return f"""
Objective

Condense the provided transcription into approximately 2,000 words, focusing exclusively on the key concepts, central topics, and significant subtopics discussed. The response must exclude any information that is not relevant to the requested summary. Maintain a formal, clear, and professional tone throughout. The summary must strictly follow the original sequence of topics and subtopics without omitting key sections. The final output must be written in Spanish.

Specific Instructions:
General Summary of the Session:

Provide a clear and coherent overview of the topics discussed, correcting grammatical or stylistic errors if necessary.
Include only relevant information from the transcription.
Detailed Development of Topics:

2.x Topic [Topic Name]:
Conceptual Development: Offer an accurate explanation of the main concepts, ensuring clarity and precision.
Practical or Illustrative Examples: Summarize the important examples provided in the transcription, improving clarity while staying true to the original content.
Relevance and Application: Explain the importance and practical application of the topics discussed, based exclusively on relevant information from the transcription.
Continue with subsequent topics in the same structured format.
Activities or Assigned Tasks:

Document only the activities, tasks, or projects explicitly mentioned during the session, improving their clarity but without adding unrelated information.
Style and Formatting:
Formal and Professional Tone: Use polished and concise language, avoiding redundancy, casual expressions, or irrelevant details.
Hierarchical Structure: Organize the content using clear headings and subheadings to enhance readability.
Approximate Length: Limit the summary to approximately 2,000 words, providing sufficient detail while excluding irrelevant information.
Output Language: The summary must be written in Spanish.
Output Format:
Use an introductory paragraph for the General Summary of the Session, followed by a hierarchical structure with numbered subheadings (2.x) for the Detailed Development of Topics.
When developing each topic, use clearly delineated subheadings for Conceptual Development, Practical Examples, and Relevance and Application.
The final section, Activities or Assigned Tasks, should be presented at the end of the response as a clear and concise list.
Examples:
2.1 Topic: Environmental Education

Conceptual Development: Explanation of the importance of environmental education as a pedagogical tool to foster environmental care.
Practical or Illustrative Examples: A workshop on recycling organized at a local school was mentioned as an example of how environmental education is applied in practice.
Relevance and Application: Environmental education plays a fundamental role in raising community awareness about sustainability and climate change.
Activities or Assigned Tasks:

The task of researching local waste management policies for the next session.
Notes:
Ensure good coherence of ideas and fluency between each section.
Make sure no key concept or relevant example is omitted when summarizing.
Correct any grammatical or stylistic errors to achieve a more professional text.
Output must be only the summary following the instructions, do not include anything else like "This is the summary..." , "This summary captures the main concepts, examples, and tasks addressed in the session, following the structure and sequence of the material discussed."

{transcription}
"""

    def analyze_transcription(self, transcription_file: str, output_file: str, model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 16384) -> str:
        """
        Analyze transcription and generate structured summary.
        
        Args:
            transcription_file (str): Path to transcription file
            output_file (str): Path to save the summary
            model (str): OpenAI model to use (default is GPT-4)
            temperature (float): Temperature for generation
            max_tokens (int): Maximum tokens for generation
            
        Returns:
            str: Generated summary content
        """
        try:
            # Step 1: Read transcription
            transcription = self._read_transcription(transcription_file)
            
            # Step 2: Generate prompt
            prompt = self._get_analysis_prompt(transcription)
            
            # Step 3: Call OpenAI's API to get the summary
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Step 4: Extract the generated summary and save it
            summary = response.choices[0].message.content.strip()
            self._save_summary(summary, output_file)
            return summary
        
        except Exception as e:
            raise Exception(f"Error in transcription analysis: {str(e)}")
