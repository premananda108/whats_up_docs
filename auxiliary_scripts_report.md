# Отчет: Вспомогательные скрипты для обработки и оценки данных

В ходе работы были созданы три Python-скрипта для решения вспомогательных задач по подготовке данных и оценке качества аннотаций. Эти инструменты не являются частью основного конвейера `main.py`, но предоставляют гибкие возможности для экспериментов и анализа.

## 1. `prepare_test_data.py`

*   **Назначение:** Извлечение текстов статей из `test_features.csv` и их сохранение в виде отдельных файлов. Это упрощает доступ к отдельным статьям для ручного анализа или выборочной обработки.
*   **Функциональность:**
    1.  Читает `data/test_features.csv`.
    2.  Создает директорию `outputs/test_features/text/`.
    3.  Для каждой строки в CSV-файле создает текстовый файл `{paper_id}.txt`, содержащий полный текст статьи.
*   **Использование:**
    ```bash
    .venv\Scripts\python.exe prepare_test_data.py
    ```

## 2. `prepare_train_data.py`

*   **Назначение:** Аналогичен предыдущему скрипту, но работает с обучающим набором `train.csv`. Он разделяет как тексты статей, так и их эталонные (человеческие) аннотации.
*   **Функциональность:**
    1.  Читает `data/train.csv`.
    2.  Создает две директории: `outputs/train/text/` и `outputs/train/summary/`.
    3.  Для каждой статьи сохраняет два файла:
        *   `outputs/train/text/{paper_id}.txt` (полный текст).
        *   `outputs/train/summary/{paper_id}.txt` (эталонная аннотация).
*   **Использование:**
    ```bash
    .venv\Scripts\python.exe prepare_train_data.py
    ```

## 3. `evaluate_summaries.py` (модифицированный)

*   **Назначение:** Вычисление ROUGE-метрик для оценки качества сгенерированных аннотаций путем их сравнения с эталонными.
*   **Функциональность:**
    1.  Принимает два пути к директориям в качестве аргументов командной строки:
        *   `--predictions-dir`: папка со сгенерированными аннотациями.
        *   `--ground-truth-dir`: папка с эталонными аннотациями.
    2.  Находит пары файлов с одинаковыми именами (`{paper_id}.txt`) в обеих директориях.
    3.  Для каждой пары вычисляет ROUGE-2 (precision, recall, f1-score).
    4.  Выводит усредненные метрики для всех найденных пар.
*   **Использование:**
    ```bash
    # Пример сравнения одной сгенерированной аннотации
    .venv\Scripts\python.exe evaluate_summaries.py --predictions-dir "outputs/train/summary_ai" --ground-truth-dir "outputs/train/summary"
    ```

## Рабочий процесс, который мы выполнили:

1.  С помощью `prepare_train_data.py` разделили `train.csv` на тексты и эталонные аннотации.
2.  Вручную (с моей помощью) сгенерировали аннотацию для статьи `0.txt` и сохранили ее в `outputs/train/summary_ai/0.txt`.
3.  С помощью `evaluate_summaries.py` сравнили нашу аннотацию с эталонной (`outputs/train/summary/0.txt`) и получили оценку **ROUGE-2 F1-score: 0.0935**, что подтверждает работоспособность нашего подхода.

---

## 4. Основной промпт (`academic_v2`)

Этот промпт используется по умолчанию в основной программе (`main.py`) для генерации аннотаций.

```yaml
academic_v2: |
  You are an expert academic editor tasked with producing a high-quality, concise abstract for a leading social science journal. Your work must be impeccable.

  **Follow these steps meticulously:**

  1.  **Internal Analysis (Do not show this in the output):**
      -  First, silently identify the paper's core Research Objective.
      -  Second, silently determine the Methodology used.
      -  Third, silently extract the most critical Findings.
      -  Fourth, silently summarize the main Conclusion and its Implications.

  2.  **Abstract Generation:**
      -  Based on your internal analysis, write a single, dense, and coherent paragraph.
      -  **Strictly adhere to a word count of 150-250 words.**
      -  The language must be formal, objective, and use a passive voice where appropriate for academic writing.
      -  **Crucially, do NOT include any information, claims, or conclusions that are not explicitly stated in the source document.**
      -  Do not directly quote sentences from the text; you must paraphrase and synthesize.

  **Input Document:**
  ---
  {document}
  ---

  **Generated Abstract:**
```
