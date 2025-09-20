import os
import csv

def create_summary_file():
    """
    Reads all summary files from the input directory, extracts paper_id and summary,
    and writes the data to a CSV file in the output directory.
    """
    input_dir = os.path.join('outputs', 'test_features', 'summary_ai')
    output_file = os.path.join('outputs', 'summaries.csv')
    
    summaries = []

    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at '{input_dir}'")
        return

    # Iterate over all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            paper_id = os.path.splitext(filename)[0]
            file_path = os.path.join(input_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                summary = f.read().strip()
            
            summaries.append({'paper_id': paper_id, 'summary': summary})

    # Sort summaries by paper_id to ensure consistent order
    summaries.sort(key=lambda x: int(x['paper_id']))

    # Write the collected data to a CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['paper_id', 'summary']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(summaries)

    print(f"Successfully created summary file at '{output_file}'")

if __name__ == '__main__':
    create_summary_file()
