# Mechanical Drawing Analyzer

## Overview

The **Mechanical Drawing Analyzer** is a Python-based tool designed to facilitate the analysis of mechanical drawing files, specifically those intended for use in processes such as **laser cutting** and **bending**. The program reads drawing files and provides important metrics about the design, including the number of cut-ins (holes), turns, and the total cutting length. This data can be essential for manufacturing processes and cost estimation.

## Features

- **Count Holes and Cut-Ins**: Analyze the number of holes or cut-ins in the drawing that represent potential cutouts for machining.
- **Calculate Total Laser-Cutting Length**: Determine the overall length of the laser-cutting path based on the design.
- **Measure Turns**: Calculate the number of turns (direction changes) in the cutting path.

## Usage

### Installation

1. **Clone the Repository:**

   ```bash
   git clone git@github.com:Kuba2901/precimet_drawing_analyser.git
   cd precimet_drawing_analyser
   ```

2. **Install the Required Dependencies:**

   The program relies on Python 3 and certain libraries. You can install them using the following (when using mac or linux):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### How to Run

1. **Prepare Your Drawing File**: Make sure your drawing is in a compatible format (DXF).
   
2. **Run the Analyzer**:

   Use the following command to analyze a drawing file:

   ```bash
   python3 main.py
   ```

   Replace `<path_to_drawing_file>` with the actual path to the drawing file you want to analyze.

### Example Output

After running the program, you will get an analysis report with key metrics such as:

```
Analyser for example.dxf
Total cutting length: 4596.927
Total cut-ins: 3
Total turns: 14
Entities count: 14
```

### Unit Testing

The project includes a suite of unit tests to ensure the reliability of the analysis. To run the tests:

```bash
python -m src.pm_tester
```

## Maintainer
Jakub Nenczak

[Github](https://github.com/Kuba2901)

[Email](kubanenczakdev@gmail.com)
