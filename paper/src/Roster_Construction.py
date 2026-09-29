import numpy as np
from scipy.optimize import minimize
import pandas as pd

# Load and clean data
opt_teams = pd.read_excel("Opt_Gini_teams.xlsx")
opt_teams.columns = ["Season", "Player", "Year", "Team", "Salary"]
opt_teams = opt_teams.dropna(subset=["Salary"])
opt_teams["Salary"] = pd.to_numeric(opt_teams["Salary"], errors="coerce")


def salary_bins(salaries, round_thousands=True):
    if round_thousands:
        salaries = np.round(salaries, -3)
    bins = [0, 2_000_000, 6_000_000, float("inf")]
    labels = ["< $2M", "$2M-$6M", ">$6M"]

    binned_salaries = pd.cut(salaries, bins=bins, labels=labels, right=False)
    bin_counts = binned_salaries.value_counts().sort_index()

    return bin_counts, binned_salaries


opt_teams_cleaned = []

for (team, year), group in opt_teams.groupby(["Team", "Year"]):
    bin_counts, _ = salary_bins(group["Salary"], round_thousands=True)
    bin_counts = bin_counts.reindex(["< $2M", "$2M-$6M", ">$6M"], fill_value=0)
    bin_counts["Team"] = team
    bin_counts["Year"] = year
    opt_teams_cleaned.append(bin_counts)
salary_counts = pd.DataFrame(opt_teams_cleaned).reset_index(drop=True)
cols = ["Team", "Year", "< $2M", "$2M-$6M", ">$6M"]
salary_counts = salary_counts[cols]
print(salary_counts.head())


# Gini Function
def gini(array):
    array = np.sort(np.array(array))
    n = len(array)
    index = np.arange(1, n + 1)
    return np.sum((2 * index - n - 1) * array) / (n * np.sum(array))


def optimization(salaries):
    optimal_gini = 0.408
    cap_target = 88_000_000

    gini_penalty = (gini(salaries) - optimal_gini) ** 2
    cap_penalty = ((np.sum(salaries) - cap_target) / cap_target) ** 2

    return 80 * gini_penalty + cap_penalty


def cap_ceiling(salaries):
    return 88_000_000 - np.sum(salaries)


def cap_floor(salaries):
    return np.sum(salaries) - 65_000_000


def gini_upper_bound(salaries):
    return 0.415 - gini(salaries)


def optimize_roster(
    roster=23,
    min_salary=0,
    max_salary=0,
    initial_guess=None,
):
    if initial_guess is None:
        np.random.seed(42)
        initial_guess = np.array(
            [13_500_000] * 3 + [3_750_000] * 8 + [1_450_000] * 12
        ) * np.random.uniform(0.95, 1.05, size=23)

    if len(initial_guess) != roster:
        initial_guess = np.random.uniform(min_salary, max_salary, roster)

    bounds = [(min_salary, max_salary)] * roster
    constraints = [
        {"type": "ineq", "fun": cap_ceiling},
        {"type": "ineq", "fun": cap_floor},
        {"type": "ineq", "fun": gini_upper_bound},
    ]

    result = minimize(
        optimization,
        initial_guess,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-6, "maxiter": 1000},
    )

    return result


opt_roster = optimize_roster(
    roster=23,
    min_salary=775_000,
    max_salary=17_000_000,
    initial_guess=None,
)

if opt_roster.success:
    final_salaries = np.round(opt_roster.x, -2)
    total_salary = np.sum(final_salaries)
    final_gini = gini(final_salaries)

    final_salaries_sorted = np.sort(final_salaries)

    bin_counts, salary_bins = salary_bins(final_salaries_sorted)
    print("\n✅ Optimization successful.")
    print(f"Gini Coefficient: {final_gini:.4f}")
    print(f"Total Salary: ${total_salary:,.0f}")

    print("\n📋 Roster Salary Projection:")
    for i, salary in enumerate(final_salaries_sorted, 1):
        print(f"  Player {i:>2}: ${salary:,.0f}")

    print("\n📊 Salary Bin Breakdown:")
    print(bin_counts)
else:
    print("\n❌ Optimization failed:")
    print(opt_roster.message)
