# MaTableGPT: GPT-based Table Data Extractor from Materials Science Literature

## Introduction
### 1) Overall workflow of MaTableGPT
1.  Generate customized TSV, JSON representation for HTML format of table and split the table.
2.  Test 3 models (fine tuning, few shot, zero shot) and go through the follow up questions process.
![1](https://github.com/KIST-CSRC/CO2RR_NER/assets/171128050/7ca70729-84cc-4b4e-a93d-225f60f424a8)

### 2) GPT modeling process
![5](https://github.com/KIST-CSRC/MaTableGPT/assets/171128050/1bb4729f-bca3-4f82-9ab1-c0d93909c37a)

## User Manual
### 1) Installation

**Using conda**
```bash
conda env create -f requirements_conda.txt
```
**Using pip**
```bash
pip install -r requirements_paper.txt
```
### 2) Download data files
```
git clone https://github.com/KIST-CSRC/MaTableGPT.git
git lfs pull
```
## 3) Script architecture
```
MaTableGPT
├── data
│   └── non_split
│   └── split
│   └── pickle_folder
│   └── result
├── GPT_models
│   └── models.py
│   └── follow_up_q.py.py
├── model_evaluation
│   └── utils
│   └── evaluation.py
├── table_representation
│   └── table_representer.py
│   └── table2json.py
├── table_splitting
│   └── split_table.py
│ 
└── run.py
```
### 4) Code usage (run.py)
**Examples : Input generation (split, tsv)**
> ```python
> input_guneration("split", "TSV")
> ```

**Examples : Data extraction (few shot, follow_up questions)**
> ```python
> model_test("few_shot", True)
> ```
## Benefit
Using MaTableGPT, we achieved a table data extraction accuracy of 96.8% and proposed the optimal solution for each situation through the Pareto-front solution.
## Reference



