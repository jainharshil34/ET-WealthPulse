# ET WealthPulse
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/jainharshil34/ET-WealthPulse)

ET WealthPulse is a local-first personal finance dashboard that provides a comprehensive analysis of your financial health. By processing your Form 16 and Consolidated Account Statement (CAS), it generates actionable insights on tax savings, investment performance, retirement planning, and more—all without your data ever leaving your machine.

The application features a built-in demo mode, allowing you to explore its full capabilities without needing to upload any personal documents.

## Key Features

*   **Document Intelligence:** Locally parses PDF documents like Form 16 (for salary and tax details) and CAMS/KFintech statements (for mutual fund holdings and transactions).
*   **Tax Wizard:** Compares the Old and New tax regimes based on your financial profile for FY 2025-26, highlighting potential tax savings ("Tax Alpha").
*   **Portfolio X-Ray:** Calculates your portfolio's money-weighted return (XIRR), identifies the "expense drag" from regular-plan mutual funds, and provides fund-level performance metrics.
*   **FIRE Path Planner:** Models a path to Financial Independence, Retire Early (FIRE) by projecting your corpus growth, calculating a target, and determining the required monthly investment.
*   **Money Health Score:** Grades your overall financial well-being across six critical dimensions: Emergency Fund, Insurance Coverage, Debt-to-Income, Diversification, Tax Efficiency, and Retirement Readiness.
*   **Privacy-Focused:** All document parsing and financial calculations are performed in-memory on your local machine. No data is stored, transmitted, or shared.
*   **Interactive UI:** Built with Streamlit, offering an intuitive interface with clear visualizations, metric cards, and detailed recommendations.
*   **Manual Fallback:** If a document cannot be parsed automatically, you can enter your financial data manually to use the analysis engine.

## How It Works

1.  **Input Data:** Launch the application and choose between:
    *   **Demo Mode (Default):** Run the application with a pre-configured demo scenario.
    *   **Live Mode:** Upload your Form 16 PDF and your CAMS/KFintech CAS PDF.
2.  **Local Processing:** The application's backend parses the documents to extract relevant data, such as income, deductions, and investment transactions.
3.  **Financial Analysis:** The `finance_engine` module processes the extracted data to:
    *   Compare tax liabilities under different regimes.
    *   Compute XIRR from transaction history and current holdings.
    *   Estimate potential savings from switching to direct mutual fund plans.
    *   Project your retirement corpus based on current investments and goals.
    *   Score your overall financial health.
4.  **View Insights:** The results are presented in a multi-page Streamlit dashboard, including an Executive Summary and detailed views for each analysis area.

## Technology Stack

*   **Frontend & Application Logic:** [Streamlit](https://streamlit.io/)
*   **Data Manipulation:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
*   **Financial Calculations:** [NumPy-Financial](https://numpy.org/numpy-financial/), [pyxirr](https://github.com/Anexen/pyxirr)
*   **PDF Parsing:** [PyMuPDF (fitz)](https://github.com/pymupdf/PyMuPDF)
*   **Plotting:** [Matplotlib](https://matplotlib.org/)

## Setup and Usage

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jainharshil34/ET-WealthPulse.git
    cd ET-WealthPulse
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    Your browser will open a new tab with the application running at `http://localhost:8501`.

### Using the Dev Container

This repository includes a pre-configured development container, which provides a consistent environment with all necessary dependencies installed. You can use it with [GitHub Codespaces](https://github.com/features/codespaces) or a local Docker setup with the [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

On launching the container, the dependencies will be installed automatically, and the Streamlit server will start.

## File Structure

```
└── et-wealthpulse/
    ├── app.py                  # Main Streamlit application file (UI and control flow)
    ├── finance_engine.py       # Core financial calculation and analysis logic
    ├── mock_data_generator.py  # Generates data and PDFs for the demo mode
    ├── requirements.txt        # Python package dependencies
    ├── demo_docs/              # Directory for generated demo documents
    ├── .devcontainer/          # Configuration for the development container
    └── ...
