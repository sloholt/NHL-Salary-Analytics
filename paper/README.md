# NHL-Salary-Inequality Analysis
_A statistical examination using Gini coefficients and econometric models over 10 seasons in the National Hockey League._

---

## Overview

This repository contains the data, code, and documentation for the paper:  

> **"Modeling the Impact of Salary Distribution on NHL Team Success"**   
> _Sloane Holtby, McGill University_  
> July 2025  

The study analyzes how intra-team salary inequality affects team performance in the NHL using both a **Poisson Generalized Linear Model (GLM)** and a **dynamic panel Generalized Method of Moments (GMM)**. Results reveal a **concave relationship**: teams perform best when balancing high-salary stars with cost-effective depth players.

---

## Key Findings

- **Optimal Gini coefficient**: ~0.408    
- **Performance metric**: Regulation + Overtime Wins (ROW)    
- **Methods**:    
  - Poisson GLM for predictive stability    
  - GMM (Arellano-Bond) to address endogeneity    
- **Simulation results**: Model results are stable under repeated simulations    
- **Roster construction framework**: Based on optimal Gini using realistic salary caps  

> _Finding the sweet spot between star power and depth leads to better outcomes under the NHL's hard cap system._  

---

## Data Sources
- [Sportrac NHL Contracts](https://www.spotrac.com/nhl/)  
- [NHL Official Stats](https://www.nhl.com/stats/)  
Data Includes:  
- Annual team salary distributions (2015-2024)  
- Player cap hits and roster sizes  
- Regular + Overtime Wins (ROW) by team and season  

## Methodology  
### Models Used:  

1. **Poisson GLM**  
   - Models count data (ROW)  
   - Predictors: Gini, Gini², Lagged ROW  
   - Interpretable, well-behaved residuals  

2. **Dynamic GMM**  
   - Addresses potential endogeneity  
   - Instruments: lagged variables  
   - Replicates Park (2022) NFL study methodology  

> See `ROW_GLM.R` and `ROW_GMM.R` for implementation.  

## Citation 
If you use this code or data, please cite:  
Holtby, Sloane. (2025). Modeling the Impact of Salary Distribution on NHL Team Success. McGill University.

## Acknowledgements 
- Inspired by Park (2022) on NFL Salary Inequality  
- Suppoerted by McGill University, Department of Mathematics & Statistics  
- Data collected from Spotrac and NHL.com  

## License 
Distributed for academic and research purposes.  
To use outside of fair-use research, please contact the author.  