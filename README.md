ET WealthPulse
---


ET WealthPulse is a local-first personal finance dashboard that provides a comprehensive analysis of financial health. By processing Form 16 and Consolidated Account Statement (CAS), it generates insights on tax savings, investment performance, and retirement planning, without any data leaving the local system.

The application includes a demo mode to explore features without uploading personal documents.

---

## Key Features

- Document Intelligence  
  Parses Form 16 and CAMS/KFintech CAS PDFs to extract financial data  

- Tax Wizard  
  Compares old and new tax regimes for FY 2025–26 and highlights potential savings  

- Portfolio Analysis  
  Calculates portfolio XIRR, evaluates fund performance, and identifies expense drag  

- FIRE Planner  
  Projects financial independence goals and estimates required investments  

- Financial Health Score  
  Evaluates emergency fund, insurance, debt, diversification, tax efficiency, and retirement readiness  

- Privacy-Focused  
  All processing is local; no storage or external transmission  

- Interactive Interface  
  Built using Streamlit with structured insights and visualizations  

- Manual Input  
  Allows manual data entry if parsing fails  

---

## How It Works

1. Select Demo Mode or upload Form 16 and CAS PDFs  
2. Data is processed locally and relevant fields are extracted  
3. Financial analysis is performed  
4. Insights are displayed in a multi-page dashboard  

---

## Technology Stack

- Streamlit  
- Pandas  
- NumPy  
- NumPy-Financial  
- pyxirr  
- PyMuPDF (fitz)  
- Matplotlib  

---

## Setup and Usage

### Clone Repository

```bash
git clone https://github.com/jainharshil34/ET-WealthPulse.git
cd ET-WealthPulse
````

### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

Application runs at: [http://localhost:8501](http://localhost:8501)

---

## Demo Mode

Demo mode allows users to explore the application using pre-generated financial data without uploading documents.

---

## Project Structure

```
ET-WealthPulse/
├── app.py
├── finance_engine.py
├── mock_data_generator.py
├── requirements.txt
├── demo_docs/
├── .devcontainer/
└── README.md
```

---

## Privacy

* No data is stored
* No external APIs are used
* All processing happens locally

---

## Limitations

* PDF parsing depends on document format
* Some inputs may require manual entry
* Limited support for asset classes beyond mutual funds

---

## Future Improvements

* Support for additional financial instruments
* Improved parsing accuracy
* Real-time data integration
* Web deployment
* Advanced financial recommendations

---

## Contributing

Fork the repository and submit a pull request with your changes.

---

## Author

Harshil Jain
GitHub: [https://github.com/jainharshil34](https://github.com/jainharshil34)

```



If you want, next step I can make it **resume-aligned (so your README directly supports your internship applications)**.
```
