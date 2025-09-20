import pathlib

def classify_files():
    """
    Analyzes ground truth summaries and classifies them as structured or unstructured.
    """
    input_dir = pathlib.Path('outputs/train/summary')
    output_dir = pathlib.Path('outputs')
    output_dir.mkdir(exist_ok=True)

    structured_keywords = [
        "problem definition:",
        "methodology/results:",
        "managerial implications:",
        "methodology:",
        "results:",
        "conclusion:",
        "implications:",
    ]

    structured_files = []
    unstructured_files = []

    if not input_dir.is_dir():
        print(f"Error: Directory not found: {input_dir}")
        return

    files = list(input_dir.glob('*.txt'))
    print(f"Found {len(files)} files to classify in {input_dir}...")

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            is_structured = False
            # Check if any line starts with one of the keywords
            for line in content.splitlines():
                if any(line.strip().startswith(keyword) for keyword in structured_keywords):
                    is_structured = True
                    break
            
            if is_structured:
                structured_files.append(file_path.name)
            else:
                unstructured_files.append(file_path.name)
        except Exception as e:
            print(f"Could not process file {file_path}: {e}")

    # Save the lists to files
    structured_list_path = output_dir / 'structured_files.txt'
    unstructured_list_path = output_dir / 'unstructured_files.txt'

    try:
        with open(structured_list_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(structured_files)))
        
        with open(unstructured_list_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted(unstructured_files)))
            
        print(f"\nClassification complete:")
        print(f"  - {len(structured_files)} structured summaries listed in {structured_list_path}")
        print(f"  - {len(unstructured_files)} unstructured summaries listed in {unstructured_list_path}")

    except Exception as e:
        print(f"Error writing classification files: {e}")


if __name__ == '__main__':
    classify_files()
