import pandas as pd
from pathlib import Path
import tqdm

def prepare_test_data():
    """
    Reads the test_features.csv file and saves each article's text into a 
    separate file in the outputs/test_features/text directory.
    The filename for each article will be its paper_id.
    """
    # Define paths
    input_csv_path = Path('data/test_features.csv')
    output_dir = Path('outputs/test_features/text')

    # Create the output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading data from {input_csv_path}...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return

    print(f"Processing {len(df)} articles and saving to {output_dir}...")
    
    # Iterate over each row in the DataFrame and save the text to a file
    for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0], desc="Saving articles"):
        paper_id = row['paper_id']
        text_content = row['text']
        
        # Define the output file path
        output_file_path = output_dir / f"{paper_id}.txt"
        
        # Write the text content to the file
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(str(text_content))
        except Exception as e:
            print(f"Could not write file for paper_id {paper_id}. Error: {e}")

    print("Processing complete.")
    print(f"Text files have been saved in: {output_dir.resolve()}")

if __name__ == '__main__':
    prepare_test_data()
