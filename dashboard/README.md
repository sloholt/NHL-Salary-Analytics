# NHL Salary Inequality Analysis Dashboard

A statistical dashboard exploring the impact of salary distribution on team success in the NHL, using Gini coefficients and econometric models over 10 seasons.

---

## Overview

This repository contains the interactive dashboard and code for:

> **"Modeling the Impact of Salary Distribution on NHL Team Success"**  
> *Sloane Holtby, McGill University*  
> July 2025

The dashboard visualizes how intra-team salary inequality affects NHL team performance, leveraging both a Poisson Generalized Linear Model (GLM) and a dynamic panel Generalized Method of Moments (GMM). Results reveal a concave relationship: teams perform best when balancing high-salary stars with cost-effective depth players.
Visit [https://sloholt.github.io/NHL-Salary-Inequality-Analysis/](https://sloholt.github.io/NHL-Salary-Inequality-Analysis/) to read the full paper!

---

## Key Features & Findings

- **Optimal Gini coefficient:** ~0.408 (performance-maximizing salary dispersion)
- **Performance metric:** Regulation + Overtime Wins (ROW)
- **Methods:**
  - Poisson GLM for predictive stability
  - GMM (Arellano-Bond) to address endogeneity
- **Simulation results:** Model findings are robust under repeated simulations
- **Roster construction framework:** Based on optimal Gini and realistic salary caps
- **Strategic insight:** Teams achieve better outcomes by balancing star power and depth under the NHL's hard cap system

---

## Data Sources

- **Spotrac NHL Contracts**
- **NHL Official Stats**
- **Included Data:**
  - Annual team salary distributions (2015–2024)
  - Player cap hits and roster sizes
  - Regulation + Overtime Wins (ROW) by team and season

---

## Methodology

### Models Used

**Poisson GLM**
- Models count data (ROW)
- Predictors: Gini, Gini², Lagged ROW
- Interpretable, well-behaved residuals

**Dynamic GMM**
- Addresses potential endogeneity
- Instruments: lagged variables
- Replicates Park (2022) NFL study methodology

See `ROW_GLM.R` and `ROW_GMM.R` in the research repository for implementation details.

---

## Dashboard Usage

### Prerequisites

- Python 3.8+
- [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/python/)

### Quick Start

1. **Clone the repository:**
    ```sh
    git clone https://github.com/<your-username>/NHL-Salary-Inequality-Analysis-Dash.git
    cd NHL-Salary-Inequality-Analysis-Dash
    ```
2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
3. **Run the app:**
    ```sh
    python app/app.py
    ```
4. **Open your browser:**  
   Go to [http://localhost:8050](http://localhost:8050)

---

## Citation

If you use this dashboard, code, or data, please cite:

> Holtby, Sloane. (2025). Modeling the Impact of Salary Distribution on NHL Team Success. McGill University.

---

## Acknowledgements

- Inspired by Park (2022) on NFL Salary Inequality
- Supported by McGill University, Department of Mathematics & Statistics
- Data collected from Spotrac and NHL.com

---

## License

Distributed for academic and research purposes.  
To use outside of fair-use research, please contact the author.
