import numpy as np
import pandas as pd
from openpyxl import Workbook
import os
import matplotlib.pyplot as plt

# Load once and use globally
df = pd.read_excel("Data\League Wide Cap Hits\LWCH_202425.xlsx", sheet_name=0)

""" CALCULATING & PLOTTING GINI COEFFICIENTS FOR NHL TEAMS """


def gini(team):
    """
    Parameters:
    team (list): A list of integers representing the scores of team members.

    Returns:
    float: The Gini coefficient, a measure of inequality.
    """
    n = len(team)
    if n == 0 or np.sum(team) == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return np.sum((2 * index - n - 1) * team) / (n * np.sum(team))


def compute_and_write_team_gini(team_name, output_path="Team_Inequality_Measures.xlsx"):
    team_data = df[df["Team"] == team_name]
    if team_data.empty:
        print(f"No data found for team: {team_name}")
        return

    year = team_data["Year"].iloc[0]
    salaries = np.sort(team_data["Cap Hit"].values)
    raw_gini = gini(salaries)
    adjusted_gini = (
        (len(salaries) + 1) / (len(salaries) - 1) * raw_gini
        if len(salaries) > 1
        else raw_gini
    )

    result_df = pd.DataFrame(
        [
            {
                "Team": team_name,
                "Year": year,
                "Raw Gini": round(raw_gini, 4),
                "Adjusted Gini": round(adjusted_gini, 4),
                "Roster Size": len(salaries),
            }
        ]
    )

    # Checking if output file exists and add the info if it does
    if os.path.exists(output_path):
        existing = pd.read_excel(output_path)
        combined = pd.concat([existing, result_df], ignore_index=True)
    else:
        combined = result_df

    combined.to_excel(output_path, index=False)
    return result_df


def plot_all_teams_gini():
    """
    Plot the Gini coefficient for all teams over the seasons.
    """
    if not os.path.exists("teamGinis.xlsx"):
        print("Gini data file does not exist. Please compute Gini coefficients first.")
        return

    # Load the Gini data

    gini = pd.read_excel("teamGinis.xlsx")
    gini["Year"] = pd.to_numeric(gini["Year"], errors="coerce")

    plt.figure(figsize=(12, 6))


# Group and plot
for team in gini["Team"].unique():
    team_data = gini[gini["Team"] == team]
    plt.scatter(team_data["Year"], team_data["Raw Gini"], label=team, alpha=0.6)

plt.title("Raw Gini Coefficient by Team per Season")
plt.xlabel("Season")
plt.ylabel("Raw Gini Coefficient")
plt.xticks(
    sorted(gini["Year"].dropna().unique().astype(int))
)  # Ensure correct X labels
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", ncol=1, fontsize="small")
plt.tight_layout()
plt.show()


def plot_gini_over_time(team, filepath="teamGinis.xlsx"):
    """
    Plot the Gini coefficient over time for a specific team.

    Parameters:
    team (str): The name of the team to plot.
    filepath (str): Path to the Excel file containing Gini data.
    """
    gini = pd.read_excel("teamGinis.xlsx")
    gini["Year"] = pd.to_numeric(gini["Year"], errors="coerce")
    team_data = gini[gini["Team"] == team]
    if team_data.empty:
        print(f"No Gini data found for team: {team}")
        return

    plt.figure(figsize=(10, 5))
    plt.scatter(team_data["Year"], team_data["Raw Gini"], color="green")
    plt.plot(team_data["Year"], team_data["Raw Gini"], linestyle="--", alpha=0.6)
    for _, row in team_data.iterrows():
        plt.text(
            row["Year"],
            row["Raw Gini"] + 0.002,
            f"{row['Raw Gini']:.3f}",
            fontsize=8,
            ha="center",
        )

    plt.title(f"Raw Gini Coefficient for {team} by Season")
    plt.xlabel("Season")
    plt.ylabel("Raw Gini Coefficient")
    plt.xticks(sorted(team_data["Year"].astype(int)))
    plt.grid(True)
    plt.tight_layout()
    plt.show()


"""CALCULATING & PLOTTING TEAM ORTEGA GAMMA SCORES FOR NHL TEAMS"""


def ortega_gamma(team):
    """
    Calculate Ortega Gamma score for a team.

    Parameters:
    team (list): A list of integers representing the scores of team members.

    Returns:
    float: The Ortega Gamma score, a measure of inequality.
    """
    n = len(team)
    if n <= 1 or np.mean(team) == 0:
        return 0.0
    mean_salary = np.mean(team)
    return np.sum(((team - mean_salary) / mean_salary) ** 2) / (n - 1)


def compute_and_append_ortega_column(
    inequality_file="Team_Inequality_Measures.xlsx",
    caphit_folder="Data\League Wide Cap Hits",
):
    df = pd.read_excel(inequality_file)
    df["Ortega Gamma"] = 0.0

    for filename in os.listdir(caphit_folder):
        if not filename.endswith(".xlsx"):
            continue
        caphit_file = os.path.join(caphit_folder, filename)
        caphit_data = pd.read_excel(caphit_file)

        for idx, row in df.iterrows():
            team = row["Team"]
            year = row["Year"]

            match = caphit_data[
                (caphit_data["Team"] == team) & (caphit_data["Year"] == year)
            ]
            if not match.empty:
                salaries = match["Cap Hit"].values
                ortega_score = ortega_gamma(salaries)
                df.at[idx, "Ortega Gamma"] = round(ortega_score, 4)
    df.to_excel(inequality_file, index=False)


compute_and_append_ortega_column()


"""CALCULATING ATKINSON INEQUALITY MEASURE FOR NHL TEAMS"""


def atkinson(salaries, epsilon=0.5):
    """
    Calculate the Atkinson inequality measure for a list of salaries.

    Parameters:
    salaries (list): A list of integers representing the salaries of team members.
    epsilon (float): The inequality aversion parameter.

    Returns:
    float: The Atkinson inequality measure.
    """
    salaries = np.array(salaries)
    n = len(salaries)
    if n <= 1 or np.mean(salaries) == 0:
        return 0.0
    mean_salary = np.mean(salaries)
    if epsilon == 1:
        log_mean = np.exp(np.mean(np.log(salaries)))
        return 1 - (log_mean / mean_salary)
    else:
        term = np.mean((salaries / mean_salary) ** (1 - epsilon))
        return 1 - (term ** (1 / (1 - epsilon)))


def compute_and_append_atkinson_across_years(
    inequality_file="Team_Inequality_Measures.xlsx",
    caphit_folder="Data/League Wide Cap Hits",
    epsilon=0.5,
):
    df = pd.read_excel(inequality_file)
    df["Atkinson Index"] = 0.0  # Initialize new column

    for filename in os.listdir(caphit_folder):
        if not filename.endswith(".xlsx"):
            continue
        cap_file_path = os.path.join(caphit_folder, filename)
        cap_data = pd.read_excel(cap_file_path)

        for idx, row in df.iterrows():
            team = row["Team"]
            year = row["Year"]
            match = cap_data[(cap_data["Team"] == team) & (cap_data["Year"] == year)]
            if not match.empty:
                salaries = match["Cap Hit"].values
                index_val = atkinson(salaries, epsilon)
                df.at[idx, "Atkinson Index"] = round(index_val, 4)

    df.to_excel(inequality_file, index=False)


compute_and_append_atkinson_across_years()


def giniStats():
    file_path = "TeamData.csv"
    data = pd.read_csv(file_path)
    gini_stats = {
        "Average Gini": data["Gini"].mean(),
        "Max Gini": data["Gini"].max(),
        "Min Gini": data["Gini"].min(),
    }
    return giniStats


giniStats()


pd.set_option("display.float_format", "{:.2f}".format)
file_path = "C:\\Users\\Sloane\\Desktop\\project\\LWCH_201516.xlsx"
df = pd.read_excel(file_path)

salary_stats_by_team = (
    df.groupby("Team")
    .agg(
        Average_Cap_Hit=("Cap Hit", "mean"),
        Salary_Variation_PopSD=("Cap Hit", lambda x: x.std(ddof=0)),
    )
    .reset_index()
)

salary_stats_by_team = salary_stats_by_team.round(2)


# Optional: Save to Excel or CSV
output_path = r"C:\Users\Sloane\Desktop\project\SalaryStatsByTeam2015.xlsx"
salary_stats_by_team.to_excel(output_path, index=False, float_format="%.2f")
