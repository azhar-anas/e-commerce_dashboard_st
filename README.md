<h1 align="center">E-Commerce Dashboard with Streamlit</h1>

<p align="center">
  <a href="https://www.python.org" target="_blank"> <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://streamlit.io/" target="_blank"> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"></a>
</p>

This repository contains an interactive e-commerce dashboard built with Streamlit for a comprehensive analysis of key business metrics. This project serves as the final submission for the "[Belajar Analisis Data dengan Python](https://www.dicoding.com/academies/555-belajar-analisis-data-dengan-python)" class from Dicoding. The dashboard provides clear insights into sales performance, customer behavior, and delivery efficiency through a series of dynamic visualizations.

Key insights include:
- Visualize total revenue and delivered orders over a specified period to identify sales trends.
- Analyze customer distribution by state and city, and segment them based on Payment Type.
- Evaluate average, minimum, and maximum delivery times to optimize logistics.
- Identify the **Best Customers** based on **RFM (Recency, Frequency, Monetary) parameters** to inform marketing and retention strategies.

---

## 🚀 Getting Started

To run this application, you can set up your environment using either **Anaconda** or a standard **Shell/Terminal**.

### 1️⃣ Using Anaconda

Create and activate a new Conda environment, then install the required dependencies.

```bash
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

### 2️⃣ Using a Standard Shell/Terminal

Create a new project directory and set up a virtual environment using `pipenv` before installing the dependencies.

```bash
mkdir e-commerce_dashboard_st
cd e-commerce_dashboard_st
pipenv install
pipenv shell
pip install -r requirements.txt
```

▶️ Running the App

Once the environment is set up, run the application using the following command:

```bash
streamlit run dashboard.py
```

