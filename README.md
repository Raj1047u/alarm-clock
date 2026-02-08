# Scientific Calculator

A comprehensive scientific calculator built with PyQt5 featuring advanced mathematical capabilities, OCR for equations, and step-by-step solutions.

## Features

- **Basic Calculator:** Standard arithmetic operations with memory functions
- **Scientific Functions:** Trigonometric, logarithmic, exponential functions, and more
- **Symbolic Math:** Solve equations, compute derivatives, integrals, and limits with step-by-step explanations
- **OCR Integration:** Extract mathematical expressions from images using Tesseract and EasyOCR
- **Matrix Operations:** Determinant, inverse, transpose, multiplication, eigenvalues, etc.
- **Unit Conversions:** Length, mass, temperature, time, area, volume, energy, pressure
- **Base Conversions:** Convert between binary, octal, decimal, and hexadecimal
- **Statistical Analysis:** Mean, median, mode, standard deviation, variance
- **Natural Language Processing:** Enter math expressions in plain English
- **Modern UI:** Clean interface with light/dark mode toggle
- **Asynchronous Processing:** Responsive UI during complex calculations

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/saunet-calculator.git
   cd saunet-calculator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Additional steps for OCR functionality:
   - Install Tesseract OCR:
     - Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
     - macOS: `brew install tesseract`
     - Linux: `sudo apt install tesseract-ocr`
   - Configure the path in `ocr.py` if Tesseract is not in the default location

## Usage

Run the calculator with:
```
python main.py
```

### Basic Operations
- Use the basic calculator tab for standard arithmetic
- Memory buttons: MC (Memory Clear), MR (Memory Recall), M+ (Memory Add), M- (Memory Subtract)

### Scientific Functions
- Access trigonometric, logarithmic, and other advanced functions
- Click on function buttons to add them to the expression

### Calculus Functions
- Click on Derivative, Integral, Limit, or Solve buttons
- Enter the expression and parameters in the dialog
- View the step-by-step solution in the steps display area

### OCR for Equations
- Click the "+" button to upload an image containing mathematical expressions
- The extracted equation will appear in the input field ready for calculation

### Natural Language Input
- Go to the "Text Input" tab
- Type expressions like "differentiate sin(x^2)" or "integrate x^3 dx"

### Other Functions
- Use the "Others" tab for:
  - Matrix operations
  - Base conversions
  - Statistical analysis
  - Unit conversions

## License

This project is licensed under the MIT License.

## Credits

- PyQt5 for the GUI framework
- SymPy for symbolic mathematics
- NumPy and SciPy for numerical computations
- Tesseract and EasyOCR for optical character recognition 
