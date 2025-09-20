import pandas as pd
from pathlib import Path
import tqdm

def prepare_train_data():
    """
    Reads the train.csv file and saves each article's text and summary into
    separate files in the outputs/train/text and outputs/train/summary directories.
    """
    # --- 1. Define Paths ---
    input_csv_path = Path('data/train.csv')
    output_text_dir = Path('outputs/train/text')
    output_summary_dir = Path('outputs/train/summary')

    # --- 2. Create Output Directories ---
    output_text_dir.mkdir(parents=True, exist_ok=True)
    output_summary_dir.mkdir(parents=True, exist_ok=True)

    # --- 3. Load Data ---
    print(f"Reading data from {input_csv_path}...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return

    # --- 4. Process and Save Files ---
    print(f"Processing {len(df)} articles and summaries...")
    
    for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0], desc="Saving files"):
        paper_id = row['paper_id']
        text_content = row['text']
        summary_content = row['summary']
        
        # Define output file paths
        text_file_path = output_text_dir / f"{paper_id}.txt"
        summary_file_path = output_summary_dir / f"{paper_id}.txt"
        
        # Write the text content
        try:
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(str(text_content))
        except Exception as e:
            print(f"Could not write text file for paper_id {paper_id}. Error: {e}")

        # Write the summary content
        try:
            with open(summary_file_path, 'w', encoding='utf-8') as f:
                f.write(str(summary_content))
        except Exception as e:
            print(f"Could not write summary file for paper_id {paper_id}. Error: {e}")

    print("Processing complete.")
    print(f"Text files saved in: {output_text_dir.resolve()}")
    print(f"Summary files saved in: {output_summary_dir.resolve()}")

if __name__ == '__main__':
    prepare_train_data()
