import re
from collections import Counter
from typing import List, Dict, Tuple

def _get_ngrams(text: str, n: int) -> Counter:
    """
    Calculates n-grams for a given text.
    """
    # Simple text normalization: lowercase and split by non-alphanumeric characters
    words = re.split(r'\W+', text.lower())
    words = [word for word in words if word]  # Remove empty strings
    
    ngrams = Counter()
    for i in range(len(words) - n + 1):
        ngram = tuple(words[i:i+n])
        ngrams[ngram] += 1
    return ngrams

def calculate_rouge_scores(target: str, prediction: str, n: int = 2) -> Dict[str, float]:
    """
    Calculates ROUGE-N precision, recall, and F1-score.

    Args:
        target (str): The ground truth summary.
        prediction (str): The generated summary.
        n (int): The "N" in ROUGE-N (e.g., 2 for bigrams).

    Returns:
        Dict[str, float]: A dictionary with 'precision', 'recall', and 'f1'.
    """
    if not prediction or not target:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    pred_ngrams = _get_ngrams(prediction, n)
    target_ngrams = _get_ngrams(target, n)

    overlapping_ngrams = pred_ngrams & target_ngrams
    overlapping_count = sum(overlapping_ngrams.values())

    total_pred_ngrams = sum(pred_ngrams.values())
    total_target_ngrams = sum(target_ngrams.values())

    precision = overlapping_count / total_pred_ngrams if total_pred_ngrams > 0 else 0.0
    recall = overlapping_count / total_target_ngrams if total_target_ngrams > 0 else 0.0
    
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1}


class Evaluator:
    """
    Handles the evaluation of generated summaries against ground truth abstracts.
    """
    def __init__(self, metrics: List[str] = None):
        """
        Initializes the Evaluator.

        Args:
            metrics (List[str], optional): List of metrics to compute. 
                                           Defaults to ['rouge-2'].
        """
        if metrics is None:
            self.metrics = ['rouge-2']
        else:
            self.metrics = metrics

    def evaluate_predictions(self, true_summaries: List[str], pred_summaries: List[str]) -> Dict[str, float]:
        """
        Evaluates a list of predicted summaries against true summaries.

        Args:
            true_summaries (List[str]): The list of ground truth summaries.
            pred_summaries (List[str]): The list of generated summaries.

        Returns:
            Dict[str, float]: A dictionary containing the average scores for each metric.
        """
        if len(true_summaries) != len(pred_summaries):
            raise ValueError("The number of true summaries and predicted summaries must be the same.")

        total_scores = {metric: {"precision": 0.0, "recall": 0.0, "f1": 0.0} for metric in self.metrics}
        num_samples = len(true_summaries)

        for true_summary, pred_summary in zip(true_summaries, pred_summaries):
            for metric in self.metrics:
                if metric == 'rouge-2':
                    scores = calculate_rouge_scores(true_summary, pred_summary, n=2)
                    total_scores[metric]['precision'] += scores['precision']
                    total_scores[metric]['recall'] += scores['recall']
                    total_scores[metric]['f1'] += scores['f1']
                # Add other metrics like rouge-1, rouge-l here if needed

        average_scores = {}
        for metric, scores in total_scores.items():
            average_scores[f'avg_{metric}_precision'] = scores['precision'] / num_samples
            average_scores[f'avg_{metric}_recall'] = scores['recall'] / num_samples
            average_scores[f'avg_{metric}_f1'] = scores['f1'] / num_samples
            
        return average_scores

    def generate_evaluation_report(self, results: Dict[str, float]) -> str:
        """
        Generates a simple string report from evaluation results.
        """
        report = "--- Evaluation Report ---"
        for key, value in results.items():
            report += f"{key.replace('_', ' ').title()}: {value:.4f}\n"
        report += "-------------------------"
        return report

# Example usage:
if __name__ == '__main__':
    true_abstract = "The paper investigates the impact of social media on political polarization. Using a large dataset of tweets, the study finds a significant correlation between echo chambers and extreme views."
    generated_abstract = "This study looks at social media's effect on political views. The paper finds that social media echo chambers are linked to polarization."

    # ROUGE-2 example
    rouge2_scores = calculate_rouge_scores(true_abstract, generated_abstract, n=2)
    print(f"ROUGE-2 Scores: {rouge2_scores}")

    # Evaluator class example
    evaluator = Evaluator(metrics=['rouge-2'])
    results = evaluator.evaluate_predictions([true_abstract], [generated_abstract])
    print(f"\nEvaluation Results: {results}")
    
    report = evaluator.generate_evaluation_report(results)
    print(f"\n{report}")
