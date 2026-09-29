import pandas as pd

pd.set_option("display.float_format", "{:.2f}".format)
file_path = "C:\\Users\\Sloane\\Desktop\\project\\LWCH_201516.xlsx"
df = pd.read_excel(file_path)

salary_stats_by_team = df.groupby('Team').agg(
    Average_Cap_Hit=('Cap Hit', 'mean'),
    Salary_Variation_PopSD=('Cap Hit', lambda x: x.std(ddof=0))
).reset_index()

salary_stats_by_team = salary_stats_by_team.round(2)


#print(salary_stats_by_team)

# Optional: Save to Excel or CSV
output_path = r"C:\Users\Sloane\Desktop\project\SalaryStatsByTeam2015.xlsx"
salary_stats_by_team.to_excel(output_path, index=False, float_format="%.2f")
