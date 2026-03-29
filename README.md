Got you—here’s a **single clean README block**, no explanations, no breaks—just copy-paste and done ✅

---

````markdown
# ET WealthPulse

ET WealthPulse is a **local-first personal finance dashboard** that provides a comprehensive analysis of your financial health. By processing your Form 16 and Consolidated Account Statement (CAS), it generates actionable insights on tax savings, investment performance, and retirement planning — all while ensuring your data never leaves your machine.

The application includes a built-in demo mode, allowing users to explore its features without uploading personal documents.

---

## 🚀 Key Features

- **Document Intelligence**  
  Parses Form 16 and CAMS/KFintech CAS PDFs to extract financial data.

- **Tax Wizard**  
  Compares Old vs New tax regimes (FY 2025–26) and highlights potential savings.

- **Portfolio X-Ray**  
  Calculates portfolio XIRR, analyzes fund performance, and identifies expense drag.

- **FIRE Path Planner**  
  Projects your journey towards Financial Independence and estimates required investments.

- **Money Health Score**  
  Evaluates financial health across emergency fund, insurance, debt, diversification, tax efficiency, and retirement readiness.

- **Privacy-First Design**  
  All processing is done locally — no data storage or transmission.

- **Interactive Dashboard**  
  Built with Streamlit for intuitive visualization and insights.

- **Manual Input Mode**  
  Allows manual data entry if document parsing fails.

---

## ⚙️ How It Works

1. Choose Demo Mode or upload Form 16 and CAS PDFs  
2. Data is processed locally and extracted  
3. Financial analysis is performed (tax, portfolio, retirement, etc.)  
4. Insights are displayed via an interactive dashboard  

---

## 🛠 Tech Stack

- Python  
- Streamlit  
- Pandas, NumPy  
- NumPy-Financial, pyxirr  
- PyMuPDF (fitz)  
- Matplotlib  

---

## 📦 Setup & Usage

### Clone Repository
```bash
git clone https://github.com/jainharshil34/ET-WealthPulse.git
cd ET-WealthPulse
````

### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

App runs at: [http://localhost:8501](http://localhost:8501)

---

## 🧪 Demo Mode

Use demo mode to explore all features with pre-generated financial data — no uploads required.

---

## 📁 Project Structure

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

## 🔒 Privacy

* No data is stored
* No external APIs are used
* All processing happens locally

---

## ⚠️ Limitations

* PDF parsing may fail for non-standard formats
* Accuracy depends on document structure
* Limited support for financial instruments

---

## 🔮 Future Improvements

* Support for more financial instruments
* Improved parsing accuracy
* Real-time integrations
* Web deployment
* ML-based financial recommendations

---

## 🤝 Contributing

Feel free to fork the repo and submit a pull request.

---


## 👤 Author

Harshil Jain
GitHub: [https://github.com/jainharshil34](https://github.com/jainharshil34)

---

## 💡 Acknowledgements

* Open-source Python ecosystem
* Streamlit community

```

---

If you want next upgrade:  
I can add **badges + screenshots + GitHub stats section** → that makes it look *top-tier portfolio repo* instantly 🚀
```
