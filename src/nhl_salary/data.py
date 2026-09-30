import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from nhl_salary.paths import (
        COMBINED_CAP_HITS_XLSX,
        PLAYER_DATA_DIR,
        PROCESSED_DIR,
        REPO_ROOT,
        missing_files,
    )
except ModuleNotFoundError:
    # Package not installed: find the folder that contains nhl_salary/paths.py
    for parent in Path(__file__).resolve().parents:
        if (parent / "nhl_salary" / "paths.py").is_file():
            sys.path.insert(0, str(parent))
            break
    from nhl_salary.paths import (
        COMBINED_CAP_HITS_XLSX,
        PLAYER_DATA_DIR,
        PROCESSED_DIR,
        REPO_ROOT,
        missing_files,
    )

# ---- inputs ----------------------------------------------------------------
SKATER_FILES = [
    PLAYER_DATA_DIR / "skaters_2008_to_2024.csv",
    PLAYER_DATA_DIR / "skaters_202526.csv",
]
GOALIE_FILES = [
    PLAYER_DATA_DIR / "goalies_2008_to_2024.csv",
    PLAYER_DATA_DIR / "goalies_202526.csv",
]
CAP_FILE = COMBINED_CAP_HITS_XLSX

# ---- outputs ---------------------------------------------------------------
PLAYER_VALUE_CSV = PROCESSED_DIR / "player_value_2008_2025.csv"
CAP_WITH_VALUE_CSV = PROCESSED_DIR / "cap_with_value.csv"
UNMATCHED_CSV = PROCESSED_DIR / "unmatched_cap_names.csv"
FUZZY_CSV = PROCESSED_DIR / "fuzzy_matches_to_review.csv"

missing = missing_files(tuple(SKATER_FILES + GOALIE_FILES + [CAP_FILE]))
if missing:
    listed = "\n  ".join(str(p.relative_to(REPO_ROOT)) for p in missing)
    raise FileNotFoundError(
        f"Missing input files (repo root: {REPO_ROOT}):\n  {listed}"
    )
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SMALL_SAMPLE_MIN = 200  # flag players with < 200 total minutes
LAGS = (1, 2, 3)

# Fix MoneyPuck outdated formatting
TEAM_MAP = {"L.A": "LAK", "N.J": "NJD", "S.J": "SJS", "T.B": "TBL", "WSH": "WAS"}
ALIASES = {
    "Mats Zuccarello-Aasen": "Mats Zuccarello",
    "Magnus Paajarvi-Svensson": "Magnus Paajarvi",
    "Thomas Wilson": "Tom Wilson",
    "Matthew Murray": "Matt Murray",
    "Anthony DeAngelo": "Tony DeAngelo",
    "Janis Moser": "J.J. Moser",
    "John-Jason Peterka": "JJ Peterka",
    "Jean-Francois Berube": "J-F Berube",
    "Pierre-Alexandre Parenteau": "PA Parenteau",
    "Theodor Blueger": "Teddy Blueger",
    "Michael Anderson": "Mikey Anderson",
    "Joseph Anderson": "Joey Anderson",
    "Zachary Jones": "Zac Jones",
    "Stanisalv Galiev": "Stanislav Galiev",
    "Jakob Karlsson": "Jakob Forsbacka Karlsson",
    "Nicklas Grossman": "Nicklas Grossmann",
    "Yevgeny Medvedev": "Evgeny Medvedev",
    "Nikita Okhotyuk": "Nikita Okhotiuk",
    "Emil Martinsen-Lilleberg": "Emil Lilleberg",
    "Yegor Zamula": "Egor Zamula",
    "Cristoval Nieves": "Boo Nieves",
    "Fyodor Svechkov": "Fedor Svechkov",
}
# Same name, same team, same season: resolve by (Player, Team, Year, Cap Hit).
ID_OVERRIDES = {
    ("Elias Pettersson", "VAN", 2024, 11_600_000): 8480012,  # forward
    ("Elias Pettersson", "VAN", 2024, 870_000): 8483678,  # defenseman
}


def name_key(x):
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", x)


def last_key(x):
    return name_key(str(x).split()[-1])


# --------------------------------------------------------------------------
# 1. Skaters: one row per player-season, columns from four game situations
# --------------------------------------------------------------------------
def load(files):
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df["team"] = df["team"].replace(TEAM_MAP)
    return df.drop_duplicates(["playerId", "season", "situation"])


sk = load(SKATER_FILES)
ID = ["playerId", "season"]


def situation(df, sit, cols):
    return df.loc[df.situation == sit, ID + list(cols)].rename(columns=cols)


# Score- and venue-adjusted xG removes the bias from teams sitting on leads.
XGF, XGA = (
    "OnIce_F_flurryScoreVenueAdjustedxGoals",
    "OnIce_A_flurryScoreVenueAdjustedxGoals",
)

base = situation(
    sk,
    "all",
    {
        "name": "name",
        "team": "team",
        "position": "position",
        "games_played": "games_played",
        "icetime": "toi_all_sec",
        "I_F_xGoals": "ixg_all",
        "I_F_goals": "goals_all",
        "I_F_primaryAssists": "a1_all",
        "I_F_points": "points_all",
        "penalties": "pen_taken",
        "penaltiesDrawn": "pen_drawn",
    },
)
ev = situation(
    sk,
    "5on5",
    {
        "icetime": "toi_5v5_sec",
        XGF: "xgf_5v5",
        XGA: "xga_5v5",
        "OnIce_F_goals": "gf_5v5",
        "OnIce_A_goals": "ga_5v5",
        "OffIce_F_xGoals": "off_xgf_5v5",
        "OffIce_A_xGoals": "off_xga_5v5",
    },
)
pp = situation(sk, "5on4", {"icetime": "toi_pp_sec", XGF: "xgf_pp", XGA: "xga_pp"})
pk = situation(sk, "4on5", {"icetime": "toi_pk_sec", XGF: "xgf_pk", XGA: "xga_pk"})

skaters = (
    base.merge(ev, on=ID, how="left")
    .merge(pp, on=ID, how="left")
    .merge(pk, on=ID, how="left")
)

# Seconds -> minutes
for c in [c for c in skaters if c.endswith("_sec")]:
    skaters[c.replace("_sec", "_min")] = skaters.pop(c) / 60

# Derived value components, all in goal units unless noted
skaters["xgd_5v5"] = skaters.xgf_5v5 - skaters.xga_5v5  # on-ice xG differential
skaters["gd_5v5"] = skaters.gf_5v5 - skaters.ga_5v5
on_pct = skaters.xgf_5v5 / (skaters.xgf_5v5 + skaters.xga_5v5)
off_pct = skaters.off_xgf_5v5 / (skaters.off_xgf_5v5 + skaters.off_xga_5v5)
skaters["rel_xg_pct_5v5"] = (
    on_pct - off_pct
)  # share, not goals; isolates player from team
skaters["finishing"] = (
    skaters.goals_all - skaters.ixg_all
)  # goals above expected on own shots
skaters["xgd_pp"] = skaters.xgf_pp - skaters.xga_pp
skaters["xgd_pk"] = skaters.xgf_pk - skaters.xga_pk
skaters["pen_diff"] = skaters.pen_drawn - skaters.pen_taken  # penalties, not goals
skaters = skaters.drop(columns=["off_xgf_5v5", "off_xga_5v5"])

# --------------------------------------------------------------------------
# 2. Goalies: GSAx = expected goals against - actual goals against
# --------------------------------------------------------------------------
gl = load(GOALIE_FILES)
g_all = situation(
    gl,
    "all",
    {
        "name": "name",
        "team": "team",
        "position": "position",
        "games_played": "games_played",
        "icetime": "toi_all_sec",
        "xGoals": "g_xga_all",
        "goals": "g_ga_all",
        "unblocked_shot_attempts": "g_shots_all",
    },
)
g_ev = situation(
    gl, "5on5", {"icetime": "toi_5v5_sec", "xGoals": "g_xga_5v5", "goals": "g_ga_5v5"}
)
goalies = g_all.merge(g_ev, on=ID, how="left")
for c in [c for c in goalies if c.endswith("_sec")]:
    goalies[c.replace("_sec", "_min")] = goalies.pop(c) / 60
goalies["gsax_all"] = goalies.g_xga_all - goalies.g_ga_all
goalies["gsax_5v5"] = goalies.g_xga_5v5 - goalies.g_ga_5v5
goalies["gsax_per60"] = goalies.gsax_all / goalies.toi_all_min * 60

# --------------------------------------------------------------------------
# 3. Stack, tidy, add lags
# --------------------------------------------------------------------------
players = pd.concat([skaters, goalies], ignore_index=True)
players["pos_group"] = players.position.map(
    {"C": "F", "L": "F", "R": "F", "D": "D", "G": "G"}
)
players["small_sample"] = players.toi_all_min < SMALL_SAMPLE_MIN

LAG_COLS = [
    "games_played",
    "toi_all_min",
    "xgd_5v5",
    "rel_xg_pct_5v5",
    "finishing",
    "xgd_pp",
    "xgd_pk",
    "pen_diff",
    "gsax_all",
]
for k in LAGS:
    prev = players[ID + LAG_COLS].copy()
    prev["season"] += k  # season t-k lines up with season t
    players = players.merge(
        prev.rename(columns={c: f"{c}_lag{k}" for c in LAG_COLS}), on=ID, how="left"
    )

# ---- keep FIRST_SEASON onward ----------------------------------------------
# Done after the lags so 2014-2016 rows still get their lag values from
# 2011-2013. Move this block above the lag loop to drop those seasons entirely.
n_before = len(players)
players = players[players.season >= FIRST_SEASON].reset_index(drop=True)
print(f"dropped {n_before - len(players):,} player-seasons before {FIRST_SEASON}")

front = [
    "playerId",
    "name",
    "season",
    "team",
    "position",
    "pos_group",
    "games_played",
    "toi_all_min",
    "small_sample",
]
players = players[front + [c for c in players if c not in front]].sort_values(
    ["season", "team", "name"]
)
players.to_csv(PLAYER_VALUE_CSV, index=False)
print(
    f"{PLAYER_VALUE_CSV.relative_to(REPO_ROOT)}: {len(players):,} player-seasons, "
    f"{players.season.min()}-{players.season.max()}"
)

# --------------------------------------------------------------------------
# 4. Match cap-file names to MoneyPuck playerIds
# --------------------------------------------------------------------------
cap = pd.read_excel(CAP_FILE)
n_raw = len(cap)
cap = cap.dropna(subset=["Player", "Cap Hit"])
cap = cap.drop_duplicates(
    ["Player", "Team", "Year", "Cap Hit"]
)  # file repeats rows ~4x
print(f"cap file: {n_raw:,} rows -> {len(cap):,} after removing blanks and duplicates")

roster = players[["playerId", "name", "season", "team"]].copy()
roster["key"] = roster.name.map(name_key)
roster["last"] = roster.name.map(last_key)
roster["first1"] = roster.name.map(name_key).str[:2]  # first two letters

cap["mp_name"] = cap.Player.replace(ALIASES)
cap["key"] = cap.mp_name.map(name_key)
cap["last"] = cap.mp_name.map(last_key)
cap["first1"] = cap.mp_name.map(name_key).str[:2]


def pick(cands, team, year):
    """Choose one playerId from candidate rows; prefer same team and nearby seasons."""
    ids = cands.playerId.unique()
    if len(ids) == 1:
        return ids[0]
    for window in (0, 1, 3):  # same team, then within 1 or 3 seasons
        near = cands[
            (cands.team == team) & (cands.season.sub(year).abs() <= window)
        ].playerId.unique()
        if len(near) == 1:
            return near[0]
    near = cands[cands.season.sub(year).abs() <= 1].playerId.unique()
    return near[0] if len(near) == 1 else np.nan


by_key = dict(tuple(roster.groupby("key")))
by_last = dict(tuple(roster.groupby(["last", "first1"])))
match, how = {}, {}
for (player, key, last, f1, team, year), _ in cap.groupby(
    ["Player", "key", "last", "first1", "Team", "Year"]
):
    pid = np.nan
    if key in by_key:  # exact normalized name
        pid, rule = pick(by_key[key], team, year), "exact"
    if (
        pd.isna(pid) and (last, f1) in by_last
    ):  # Cameron -> Cam, Matthew -> Matt (first 2 letters must agree)
        c = by_last[(last, f1)]
        c = c[c.season.sub(year).abs() <= 1]
        if len(c):
            pid, rule = pick(c, team, year), "surname+prefix"
    match[(player, team, year)] = pid
    how[(player, team, year)] = rule if pd.notna(pid) else "unmatched"

k = list(zip(cap.Player, cap.Team, cap.Year))
cap["playerId"] = [match[x] for x in k]
cap["match_rule"] = [how[x] for x in k]
for (player, team, year, hit), pid in ID_OVERRIDES.items():
    row = (
        (cap.Player == player)
        & (cap.Team == team)
        & (cap.Year == year)
        & (cap["Cap Hit"] == hit)
    )
    cap.loc[row, ["playerId", "match_rule"]] = [pid, "manual"]
cap["playerId"] = cap.playerId.astype("Int64")
cap = cap.drop(columns=["mp_name", "key", "last", "first1"])

unmatched = cap[cap.playerId.isna()][["Player", "Team", "Year", "Cap Hit"]]
unmatched.to_csv(UNMATCHED_CSV, index=False)
# Fuzzy matches deserve a glance: cap spelling next to the MoneyPuck spelling
names = players.drop_duplicates("playerId").set_index("playerId").name
fuzzy = cap[cap.match_rule == "surname+prefix"].drop_duplicates("Player")
fuzzy.assign(moneypuck_name=fuzzy.playerId.map(names))[
    ["Player", "moneypuck_name"]
].to_csv(FUZZY_CSV, index=False)
print(cap.match_rule.value_counts().to_string())
print(
    f"unmatched cap rows: {len(unmatched)} ({unmatched['Cap Hit'].sum() / cap['Cap Hit'].sum():.1%} "
    f"of cap dollars) -> {UNMATCHED_CSV.relative_to(REPO_ROOT)}"
)

# --------------------------------------------------------------------------
# 5. Join value onto cap rows (by player and season, NOT team: MoneyPuck lists
#    a traded player under one team only)
# --------------------------------------------------------------------------
value = players.drop(columns=["name", "team"]).rename(
    columns={"season": "Year", "team": "mp_team"}
)
out = cap.merge(value, on=["playerId", "Year"], how="left")
out["played_this_season"] = out.games_played.notna()
out.to_csv(CAP_WITH_VALUE_CSV, index=False)
print(
    f"{CAP_WITH_VALUE_CSV.relative_to(REPO_ROOT)}: {len(out):,} rows; "
    f"{out.played_this_season.mean():.1%} have same-season stats, "
    f"{out.filter(like='_lag1').notna().any(axis=1).mean():.1%} have prior-season stats"
)
