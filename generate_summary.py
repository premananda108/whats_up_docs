import os
import pathlib
import argparse
from time import sleep

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='.env')

# --- 1. Configuration ---
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("The GOOGLE_API_KEY environment variable must be set.")

# Configure the API key
genai.configure(api_key=api_key)

# Model settings
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 512,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    safety_settings=safety_settings,
    generation_config=generation_config,
)


# --- 2. Loading the improved prompt ---
def get_improved_prompt():
    prompt_text = '''**Task:** Generate a concise academic summary following the established patterns of high-quality scholarly abstracts.

**High-quality examples:**

Example 1 - Comparative Analysis Study:
Source: [8000-word analysis of honor codes evolution in Poland]
Summary: "This article is devoted to the key persons in honour proceedings - the seconds, who were also called deputies of honour. Through a comparative analysis of Władysław Boziewicz's codes of honour, the Polish Code of Honour (1919) and the General Principles of Honourable Conduct (1927), a reconstruction will be made of the normativity of the role of seconds contained in them. This will make it possible to trace the direction of changes in Boziewicz's reflection on the essence of the course of honour proceedings, which is contained in his codifications. Thus, one of the points of his social criticism directed against the practice of honour proceedings will be revealed. The study will reveal how, in Boziewicz's reflection on honour proceedings, the role of autonomous moral reflection of honour deputies and the ethical community they represent has increased in relation to the will of their principals."

Example 2 - Empirical Economics Study:
Source: [15000-word analysis of FDA regulation and innovation]
Summary: "How does FDA regulation affect innovation and market concentration? I examine this question by exploiting FDA deregulation events that affected certain medical device types but not others. I use text analysis to gather comprehensive data on medical device innovation, device safety, firm entry, prices, and regulatory changes. My analysis of these data yields three core results. First, these deregulation events significantly increase the quantity and quality of new technologies in affected medical device types relative to control groups. These increases are particularly strong among small and inexperienced firms. Second, these events increase firm entry and lower the prices of medical procedures that use affected medical device types. Third, the rates of serious injuries and deaths attributable to defective devices do not increase measurably after these events."

Example 3 - Survey Research Study:
Source: [6000-word study of Kurdish EFL students' beliefs]
Summary: "This paper is an attempt to deal with language learners' beliefs. Researchers used Elaine Kolker Horwitz's model (1988), Beliefs about Language Learning Inventory, and they applied it to explore the views of Kurdish EFL university students concerning language learning. The study aims to investigate and expose their opinions regarding language learning generally, then English language more precisely. Its significance lies in exploring the beliefs of Kurdish EFL university students about language learning. The researchers administered a Beliefs about Language Learning Inventory (BALLI) questionnaire to seven universities to achieve this aim. The questionnaire includes several viewpoints regarding the difficulty of language learning, foreign language aptitude, the nature of language learning, learning and communication strategies, and motivation and expectations. They collected and analyzed the questionnaire results and found out that the first category, the difficulty of language learning, has the lowest mean score among the five categories. In contrast, the fifth category, motivation and expectations, has the highest mean score."

**Critical Instructions:**
1. **Opening Structure**: Begin with either:
   - A research question: "How does [X] affect [Y]?" or "What are the [beliefs/effects/relationships] of [subject]?"
   - A declarative statement: "This [paper/study/article] [examines/analyzes/explores] [main topic]"

2. **Essential Academic Bigrammes**: Use these high-frequency academic phrases naturally:
   - "the study" / "this study"
   - "the findings" / "the results" / "the analysis"
   - "the researchers" / "the authors"
   - "data from" / "using data" / "based on"
   - "analysis of" / "examination of"

3. **Core Content Requirements**:
   - Methodology: Clearly state the research method/approach used
   - Key findings: Include 2-3 most important results with specific terminology from the source
   - Scope: Mention the sample size, geographic area, or time period when relevant
   - Implications: End with the main conclusion or significance

4. **Terminology Preservation**: Use the exact technical terms, proper nouns, and specialized vocabulary from the original document. This is crucial for accuracy.

5. **Structural Flow**: Follow this logical sequence:
   [Research focus] → [Method/Data] → [Key finding 1] → [Key finding 2] → [Key finding 3 if applicable] → [Main conclusion]

6. **Language Requirements**:
   - Single coherent paragraph, 150-250 words
   - Academic tone throughout
   - No external information beyond what's stated in the source
   - Paraphrase concepts but preserve key terminology exactly

**Document to analyze:**
{document}
'''
    return prompt_text

# --- Original prompt for comparison ---
def get_prompt_from_report():
    prompt_text = '''**Task:** Generate a concise summary of the following document.

**Instructions:**
1.  The summary must be a single, coherent paragraph.
2.  The word count must be between 150 and 250 words.
3.  The summary must only contain information explicitly stated in the source document. Do not add any external information or conclusions.
4.  Paraphrase the content. Do not copy sentences verbatim.
5.  Prioritize using the key terminology and phrasing from the original document to maintain its tone and style.

**Document to analyze:**
{document}
'''
    return prompt_text


# --- 3. Main function ---
def generate_summary_for_file(input_path, output_path, prompt_template):
    """
    Reads a file, generates a summary for it using Gemini, and saves the result.
    """
    input_path = pathlib.Path(input_path)
    output_path = pathlib.Path(output_path)

    # Create the output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"1. Reading article from file: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            article_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at path {input_path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Check if the file is empty
    if not article_text.strip():
        print("Error: File is empty or contains only whitespace")
        return

    # Format the prompt with the article text
    full_prompt = prompt_template.format(document=article_text)

    print("2. Sending request to Gemini API to generate summary...")
    try:
        response = model.generate_content(full_prompt)

        # Check if a response was received
        if not response or not response.text:
            print("Error: Empty response from Gemini API")
            return

        generated_summary = response.text.strip()

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return

    print(f"3. Saving result to file: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_summary)
        print("Done!")
        print(f"Generated summary saved to: {output_path}")
        print(f"Summary length: {len(generated_summary.split())} words")

    except Exception as e:
        print(f"Error saving file: {e}")


def get_next_start_number(output_dir):
    """Finds the number of the next article to process based on existing summaries."""
    output_dir = pathlib.Path(output_dir)
    if not output_dir.is_dir():
        return 1  # Directory doesn't exist, start from 1

    summaries = list(output_dir.glob('*.txt'))
    if not summaries:
        return 1  # Directory is empty, start from 1

    last_num = 0
    for summary_path in summaries:
        try:
            num = int(summary_path.stem)
            if num > last_num:
                last_num = num
        except ValueError:
            # Ignore files that don't have a number as a name
            continue

    return last_num + 1


def main():
    """Main function of the program"""
    # --- Command-line argument setup ---
    parser = argparse.ArgumentParser(
        description="Generate summaries for articles using Gemini. Automatically resumes from the last generated summary."
    )
    parser.add_argument(
        '--start-from',
        type=int,
        default=None,
        help='Manually specify the file number to start from. Overrides automatic resume.'
    )
    args = parser.parse_args()

    # Define directory paths
    INPUT_DIR = pathlib.Path('outputs/test_features/text')
    OUTPUT_DIR = pathlib.Path('outputs/test_features/summary_ai')
    FILES_TO_PROCESS_LIMIT = 100

    # Determine the starting file number
    start_number = args.start_from
    if start_number is None:
        start_number = get_next_start_number(OUTPUT_DIR)
        if start_number > 1:
            print(f"Automatically resuming from article #{start_number}.")
        else:
            print("No previous summaries found. Starting from article #1.")
    else:
        print(f"Manual start number provided. Starting from article #{start_number}.")

    try:
        # Check if the input directory exists
        if not INPUT_DIR.is_dir():
            print(f"Error: Input directory not found: {INPUT_DIR}")
            return

        # Get a list of all files from the input directory
        all_files = list(INPUT_DIR.glob('*'))

        # Sort all files by the numerical value in their name
        sorted_files = sorted(all_files, key=lambda p: int(p.stem))

        # Filter files to start from the specified number
        files_to_start_from = [p for p in sorted_files if int(p.stem) >= start_number]

        # Limit the number of files to process
        files_to_process = files_to_start_from[:FILES_TO_PROCESS_LIMIT]

        if not files_to_process:
            print(f"No new files found in {INPUT_DIR} to process starting from number {start_number}.")
            return

        start_file_num = int(files_to_process[0].stem)
        print(f"Starting processing for {len(files_to_process)} files, beginning with article #{start_file_num}...")

        # Load the improved prompt template
        prompt_template = get_improved_prompt()
        print("\n[INFO] Using improved prompt with few-shot learning!")
        print("[WARNING] Results will overwrite files in outputs/train/summary_ai/")
        print("[REVERT] To revert to the old prompt, replace get_improved_prompt() with get_prompt_from_report()")
        print("-" * 80)

        # Iterate over the files and generate summaries
        for i, input_path in enumerate(files_to_process, 1):
            # Form the path for the output file, preserving the name
            output_path = OUTPUT_DIR / input_path.name

            print("-" * 50)
            print(f"({i}/{len(files_to_process)}) Processing file: {input_path}")

            # Execute the main task
            generate_summary_for_file(input_path, output_path, prompt_template)

            sleep(5)

    except (ValueError, FileNotFoundError) as e:
        print(f"Error during startup preparation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
