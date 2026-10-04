# Financial Analytics & Real Estate Market Intelligence

## 📌 Project Overview

This project uses "Machine Learning and Data Analytics" to identify different types of real estate buyers and understand their investment behavior.

The system applies "K-Means and Hierarchical Clustering" to discover hidden patterns in customer data and create meaningful buyer segments.

## 🎯 Objectives

- Identify different real estate buyer segments
- Analyze investment and financing behavior
- Understand geographic differences in buyer behavior
- Improve customer and investor targeting
- Support data-driven property recommendations
- Provide interactive market intelligence through a Streamlit dashboard

## 📊 Dataset

The dataset contains customer-related information such as:

- Client Type
- Gender
- Country
- Region
- Age
- Acquisition Purpose
- Loan Applied
- Referral Channel
- Satisfaction Score

## 🔍 Methodology

1. **Data Cleaning**
   - Handle missing values
   - Remove duplicate records
   - Normalize categorical data

2. **Feature Engineering**
   - Create age-related features
   - Encode categorical variables
   - Scale numerical features

3. **Exploratory Data Analysis**
   - Analyze demographics
   - Study investment behavior
   - Analyze geographic patterns
   - Examine financing behavior

4. **Clustering**
   - K-Means Clustering
   - Hierarchical Clustering

5. **Cluster Evaluation**
   - Elbow Method
   - Silhouette Score

6. **Buyer Profiling**
   - Global Investors
   - First-Time Buyers
   - Corporate Buyers
   - Luxury Investors

## 📈 Dashboard

The project includes a "Streamlit dashboard" with:

- Buyer Segmentation Overview
- Investor Behavior Dashboard
- Geographic Buyer Analysis
- Segment Insights Panel
- Interactive filters for Country, Region, Acquisition Purpose, and Client Type

## 🛠️ Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Streamlit
- Jupyter Notebook

## 📁 Project Structure

```text
Financial-Analytics-Real-Estate/
│
├── data/
├── docs/
├── models/
├── notebooks/
├── src/
├── visualizations/
├── app.py
├── README.md
├── requirements.txt
└── .gitignore