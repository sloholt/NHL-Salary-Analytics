from dash import Input, Output
from app.figures import *


def register_callbacks(app):
    @app.callback(
        Output("logo-scatter-graph", "figure"),
        Input("logo-year-dropdown", "value"),
    )
    def _update_logo_scatter(year):
        return gini_vs_row_by_year(year)

    @app.callback(
        Output("ts-graph", "figure"),
        Output("ts-info-line", "children"),
        Output("ts-roster-line", "children"),
        Input("ts-team", "value"),
        Input("ts-year", "value"),
    )
    def update_team_salary(team, year):
        year = int(year)
        if not team or not year:
            return {}, "", ""
        fig = salary_histogram(team, int(year))
        name = TEAM_NAME_MAP.get(team, team)
        g = get_gini(team, year)
        roster_size = get_roster_size(team, year)
        info = f"{name} — Gini Coefficient: {g:.3f}" if g == g else f"{name}"
        roster = (
            f"Roster Size: {roster_size} players" if roster_size else "Roster Size: N/A"
        )
        return fig, info, roster

    @app.callback(
        Output("row-trend-graph", "figure"),
        Output("gini-trend-graph", "figure"),
        Input("trend-team", "value"),
        Input("trend-years", "value"),
    )
    def _update_team_trends(team, year_range):
        if not team or not year_range:
            return {}, {}
        return team_trend_figures(team, year_range)

    @app.callback(
        Output("glm-plot", "figure"),
        Output("glm-table", "data"),
        Input("logo-year-dropdown", "value"),
    )
    def _refresh_glm(_):
        return glm_curve_fig(), glm_table_records()
