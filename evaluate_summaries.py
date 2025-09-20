import click
from pathlib import Path
from evaluator import Evaluator
import tqdm

@click.command()
@click.option('--predictions-dir', 
              default='outputs/train/summary_ai', 
              help='Directory with AI-generated summaries.')
@click.option('--ground-truth-dir', 
              default='outputs/train/summary', 
              help='Directory with ground truth summaries.')
def main(predictions_dir, ground_truth_dir):
    """
    Evaluates generated summaries against ground truth summaries from specified directories.
    """
    # --- 1. Define Paths ---
    pred_dir = Path(predictions_dir)
    truth_dir = Path(ground_truth_dir)
    
    if not pred_dir.is_dir():
        click.echo(f"Error: Predictions directory not found at {pred_dir}")
        return
        
    if not truth_dir.is_dir():
        click.echo(f"Error: Ground truth directory not found at {truth_dir}")
        return

    # --- 2. Load Ground Truth Summaries ---
    click.echo(f"Loading ground truth summaries from {truth_dir}...")
    truth_files = list(truth_dir.glob('*.txt'))
    truth_summaries_map = {}
    for file_path in tqdm.tqdm(truth_files, desc="Reading ground truth"):
        try:
            paper_id = int(file_path.stem)
            with open(file_path, 'r', encoding='utf-8') as f:
                truth_summaries_map[paper_id] = f.read()
        except (ValueError, IOError) as e:
            click.echo(f"Warning: Could not process file {file_path}. Error: {e}")
            continue
    click.echo(f"Loaded {len(truth_summaries_map)} ground truth summaries.")

    # --- 3. Load Predicted Summaries ---
    click.echo(f"Loading predicted summaries from {pred_dir}...")
    pred_files = list(pred_dir.glob('*.txt'))
    if not pred_files:
        click.echo("No summary files found to evaluate.")
        return
        
    pred_summaries_map = {}
    for file_path in tqdm.tqdm(pred_files, desc="Reading predictions"):
        try:
            paper_id = int(file_path.stem)
            with open(file_path, 'r', encoding='utf-8') as f:
                pred_summaries_map[paper_id] = f.read()
        except (ValueError, IOError) as e:
            click.echo(f"Warning: Could not process file {file_path}. Error: {e}")
            continue
    click.echo(f"Loaded {len(pred_summaries_map)} predicted summaries.")

    # --- 4. Align Data for Evaluation ---
    true_summaries_aligned = []
    pred_summaries_aligned = []
    
    click.echo("Aligning predictions with ground truth...")
    for paper_id, pred_summary in pred_summaries_map.items():
        if paper_id in truth_summaries_map:
            true_summaries_aligned.append(truth_summaries_map[paper_id])
            pred_summaries_aligned.append(pred_summary)
        else:
            click.echo(f"Warning: No ground truth found for paper_id {paper_id}. Skipping.")
            
    if not true_summaries_aligned:
        click.echo("Could not find any matching ground truth summaries for the predictions. Aborting.")
        return
        
    click.echo(f"Found {len(true_summaries_aligned)} matching summaries for evaluation.")

    # --- 5. Run Evaluation ---
    click.echo("Calculating ROUGE scores...")
    evaluator = Evaluator(metrics=['rouge-2'])
    results = evaluator.evaluate_predictions(true_summaries_aligned, pred_summaries_aligned)

    # --- 6. Display Report ---
    report = evaluator.generate_evaluation_report(results)
    click.echo("\n" + report)

if __name__ == '__main__':
    main()
