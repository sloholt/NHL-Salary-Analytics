from dash import html, dcc, dash_table
from app.figures import *
from app.themes import RED_LINE

min_year = int(df_teams["Year"].min())
max_year = int(df_teams["Year"].max())

years = sorted(df_teams["Year"].unique())
default_year = int(min(years))


def logo_scatter_section():
    """
    Returns the layout section for the league-wide Gini vs ROW scatter plot.
    Includes year dropdown, explanatory text, and the plot container.
    """
    return html.Div(
        [
            html.H3("League Wide Gini vs ROW by Year"),
            dcc.Markdown(
                "This plot shows how each NHL team’s salary inequality (Gini coefficient) relates to its Regulation + Overtime Wins (ROW) in a selected season.",
                style={"marginBottom": "12px"},
            ),
            dcc.Markdown(
                "**Use the dropdown to explore year-by-year patterns and see how different roster structures align with regular-season performance.**",
                style={
                    "fontStyle": "italic",
                    "color": "#002244",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        dcc.Dropdown(
                            id="logo-year-dropdown",
                            options=get_year_options(),
                            value=default_year,
                            clearable=False,
                            className="dash-dropdown",
                        ),
                        style={"maxWidth": "220px", "marginBottom": "10px"},
                    ),
                    dcc.Graph(
                        id="logo-scatter-graph",
                        className="full-width",
                        style={"height": "520px"},
                    ),
                ],
                className="plot-container",
            ),
        ]
    )


def team_salary_selection():
    """
    Returns the layout section for team salary visualization.
    Includes team/year dropdowns, info box, and salary histogram plot.
    """
    return html.Div(
        [
            html.H3("Team Salary"),
            dcc.Markdown(
                "This chart breaks down the selected team’s player salaries (Cap Hits) for a given season, showing how earnings are distributed across the roster. The Gini coefficient and roster size above summarize the overall inequality in that team’s payroll.",
                style={"marginBottom": "12px"},
            ),
            dcc.Markdown(
                "**Using the drop-downs select a team and a year to view each player's Cap Hit.**",
                style={
                    "fontStyle": "italic",
                    "color": "#002244",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                [
                    # Team dropdown
                    html.Div(
                        dcc.Dropdown(
                            id="ts-team",
                            options=get_team_options(),
                            value=(
                                get_team_options()[0]["value"]
                                if get_team_options()
                                else None
                            ),
                            placeholder="Team Selection",
                            clearable=False,
                            className="dash-dropdown",
                        ),
                        style={"minWidth": "220px"},
                    ),
                    # Year dropdown
                    html.Div(
                        dcc.Dropdown(
                            id="ts-year",
                            options=get_year_options(),
                            value=default_year,
                            placeholder="Year Selection",
                            clearable=False,
                            className="dash-dropdown",
                        ),
                        style={"minWidth": "140px", "marginLeft": "10px"},
                    ),
                    # Info box
                    html.Div(
                        [
                            html.Div(id="ts-info-line", style={"fontWeight": "bold"}),
                            html.Div(id="ts-roster-line", style={"marginTop": "6px"}),
                        ],
                        className="cta-box",
                        style={
                            "marginLeft": "16px",
                            "padding": "10px 14px",
                            "maxWidth": "500px",
                            "minWidth": "400px",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                            "alignSelf": "center",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "18px",
                    "marginBottom": "10px",
                },
            ),
            # Plot
            html.Div(
                dcc.Graph(id="ts-graph", style={"height": "520px"}),
                className="plot-container",
            ),
        ]
    )


def gini_vs_row_section():
    """
    Returns the layout section for team Gini vs ROW trends.
    Includes team dropdown, year slider, and two side-by-side trend plots.
    """
    return html.Div(
        [
            html.H3("Gini vs Regulation + Overtime Wins"),
            dcc.Markdown(
                "Comparing the two trends can reveal whether payroll inequality and performance tend to move together or diverge across seasons. These charts track the selected team’s performance (ROW) and salary inequality (Gini coefficient) over time.",
                style={"marginBottom": "12px"},
            ),
            dcc.Markdown(
                "**Use the drop-down to select a team and use the slider to explore how changes in roster structure align with shifts in on-ice results.**",
                style={
                    "fontStyle": "italic",
                    "color": "#002244",
                    "marginBottom": "8px",
                },
            ),
            # Dropdown & Slider
            html.Div(
                [
                    # Team dropdown
                    html.Div(
                        dcc.Dropdown(
                            id="trend-team",
                            options=get_team_options(),
                            value=(
                                get_team_options()[0]["value"]
                                if get_team_options()
                                else None
                            ),
                            clearable=False,
                            className="dash-dropdown",
                        ),
                        style={"minWidth": "320px"},
                    ),
                    # Year slider
                    html.Div(
                        dcc.RangeSlider(
                            id="trend-years",
                            min=2015,
                            max=2024,
                            step=1,
                            value=[2015, 2024],
                            marks={y: str(y) for y in range(2015, 2025)},
                            tooltip={
                                "placement": "bottom",
                                "always_visible": False,
                            },
                        ),
                        style={"flex": "1", "paddingLeft": "14px"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "12px"},
                className="text-container",
            ),
            # Two plots side by side
            html.Div(
                [
                    html.Div(
                        dcc.Graph(
                            id="row-trend-graph",
                            style={"height": "520px", "width": "100%"},
                            config={"responsive": True},
                        ),
                        style={"flex": 1, "minWidth": 0},
                    ),
                    html.Div(
                        dcc.Graph(
                            id="gini-trend-graph",
                            style={"height": "520px", "width": "100%"},
                            config={"responsive": True},
                        ),
                        style={"flex": 1, "minWidth": 0},
                    ),
                ],
                className="plot-container",
                style={
                    "display": "flex",
                    "gap": "16px",
                    "maxWidth": "1100px",
                    "margin": "0 auto",
                    "width": "100%",
                },
            ),
        ]
    )


def glm_model_section():
    """
    Returns the layout section for the Poisson GLM model analysis.
    Includes model explanation, formula, results table, and fitted curve plot.
    """
    return html.Div(
        [
            html.H3("GLM Model"),
            dcc.Markdown(
                "I used a Poisson Generalized Linear Model (GLM) here because Regulation + Overtime Wins (ROW) are count data, making the Poisson distribution with a log-link function an appropriate choice. "
                "The GLM assumes that, conditional on the predictors, ROW values are independent and that their variance is proportional to the mean, with only mild overdispersion observed in our data. This makes it a strong empirical fit for estimating and interpreting the relationship between payroll structure and on-ice performance.",
                style={"marginBottom": "12px"},
            ),
            dcc.Markdown(
                "**Hover over any point to see a team’s Gini coefficient and ROW in the model.**",
                style={
                    "fontStyle": "italic",
                    "color": "#002244",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                [
                    # Text + Table
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Markdown(
                                        r"""This Poisson GLM models ROW as a function of the Gini coefficient,
its square, and the previous season's ROW. Using a log-link, the model is:""",
                                        style={"marginBottom": "12px"},
                                    ),
                                    html.P(
                                        [
                                            "log(",
                                            html.Sub("λᵢ"),
                                            ") = β",
                                            html.Sub("0"),
                                            " + β",
                                            html.Sub("1"),
                                            " Gini",
                                            html.Sub("i"),
                                            " + β",
                                            html.Sub("2"),
                                            " Gini",
                                            html.Sub("i"),
                                            html.Sup("2"),
                                            " + β",
                                            html.Sub("3"),
                                            " ROW",
                                            html.Sub("t−1"),
                                        ],
                                        style={
                                            "color": "#C53030",
                                            "textAlign": "center",
                                            "margin": "0 0 12px 0",
                                        },
                                    ),
                                    dcc.Markdown(
                                        """The fitted curve in the plot holds the previous ROW at its league-average to show the isolated effect of Gini on ROW.""",
                                        style={"marginBottom": "12px"},
                                    ),
                                ],
                                className="text-container",
                            ),
                            # Table
                            html.Div(
                                dash_table.DataTable(
                                    id="glm-table",
                                    columns=glm_table_cols(),
                                    data=glm_table_records(),
                                    style_as_list_view=True,
                                    style_table={"overflowX": "auto", "width": "100%"},
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "6px 8px",
                                        "fontFamily": "Georgia, serif",
                                        "fontSize": "14px",
                                        "border": "none",
                                    },
                                    style_header={
                                        "fontWeight": "bold",
                                        "color": NAVY,
                                        "border": "none",
                                        "backgroundColor": ACCENT,
                                    },
                                ),
                                className="text-container",
                            ),
                        ],
                        className="plot-container",
                        style={"flex": "1", "minWidth": "0"},
                    ),
                    # Plot
                    html.Div(
                        dcc.Graph(
                            id="glm-plot",
                            figure=glm_curve_fig(),
                            style={"height": "520px", "width": "100%"},
                        ),
                        className="plot-container",
                        style={"flex": "1", "minWidth": "0"},
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "16px",
                    "alignItems": "stretch",
                    "maxWidth": "1100px",
                    "margin": "0 auto",
                    "width": "100%",
                },
            ),
            html.Div(
                dcc.Markdown(
                    "The GLM results indicate a concave relationship between salary inequality and performance, with an estimated optimal Gini of about 0.408. Teams near this level tend to achieve more ROW, while both lower and higher inequality are linked to weaker outcomes. The strong, positive effect of the previous season’s ROW confirms that past success is a key driver of current performance.",
                    style={"marginBottom": "12px"},
                ),
                className="text-container",
            ),
        ]
    )


def gmm_model_section():
    """
    Returns the layout section for the dynamic panel GMM model analysis.
    Includes model explanation, formula, results table, and summary text.
    """
    return html.Div(
        [
            html.H3("GMM Model"),
            dcc.Markdown(
                "I included a dynamic panel Generalized Method of Moments (GMM) model to address potential endogeneity between past performance and salary inequality—issues the GLM does not account for. By using internal instruments and removing team-specific effects, GMM mitigates bias from unobserved factors that remain constant over time. This approach assumes that the instruments are valid (uncorrelated with the error term) and that salary inequality and performance follow a stable dynamic process, allowing us to isolate both immediate and delayed effects of payroll structure on team outcomes.",
                style={"marginBottom": "12px"},
            ),
            html.Div(
                [
                    # Text & Table
                    html.Div(
                        [
                            dcc.Markdown(
                                (
                                    "This dynamic panel GMM models ROW as a function of two lags of ROW, "
                                    "the Gini coefficient, and its square. "
                                    "To address potential endogeneity between past performance and salary structure, "
                                    "lagged variables are used as instruments, and team fixed effects are removed via "
                                    "first differencing. The model is:"
                                ),
                                style={"marginBottom": "12px"},
                            ),
                            html.P(
                                [
                                    "ROW",
                                    html.Sub("i,t"),
                                    " = ",
                                    "α",
                                    html.Sub("1"),
                                    " ROW",
                                    html.Sub("i,t−1"),
                                    " + ",
                                    "α",
                                    html.Sub("2"),
                                    " ROW",
                                    html.Sub("i,t−2"),
                                    " + ",
                                    "β",
                                    html.Sub("1"),
                                    " Gini",
                                    html.Sub("i,t−1"),
                                    " + ",
                                    "β",
                                    html.Sub("2"),
                                    " Gini",
                                    html.Sub("i,t−1"),
                                    html.Sup("2"),
                                    " + ",
                                    "η",
                                    html.Sub("i"),
                                    " + ",
                                    "ε",
                                    html.Sub("i,t"),
                                ],
                                style={
                                    "color": "#C2185B",
                                    "fontFamily": "Georgia, serif",
                                    "fontSize": "16px",
                                    "textAlign": "center",
                                    "fontStyle": "italic",
                                },
                            ),
                            dcc.Markdown(
                                "The fitted results capture both short-run and lagged effects of salary inequality on team performance.",
                                style={"marginBottom": "12px"},
                            ),
                        ],
                        className="text-container",
                    ),
                    html.Div(
                        dash_table.DataTable(
                            id="gmm-table",
                            columns=gmm_table_cols(),
                            data=gmm_table_records(),
                            style_as_list_view=True,
                            style_table={"overflowX": "auto", "width": "100%"},
                            style_cell={
                                "textAlign": "left",
                                "padding": "6px 8px",
                                "fontFamily": "Georgia, serif",
                                "fontSize": "14px",
                                "border": "none",
                            },
                            style_header={
                                "fontWeight": "bold",
                                "color": NAVY,
                                "border": "none",
                                "backgroundColor": ACCENT,
                            },
                        ),
                        className="text-container",
                    ),
                ],
                className="plot-container",
                style={
                    "flexDirection": "column",
                    "gap": "16px",
                    "alignItems": "stretch",
                    "maxWidth": "1100px",
                    "margin": "0 auto",
                    "width": "100%",
                },
            ),
            html.Div(
                dcc.Markdown(
                    "The GMM results show that higher inequality in the same season tends to lower performance, while greater inequality in the previous season boosts ROW. This points to a delayed hump-shaped effect, where the benefits of salary concentration emerge over time."
                ),
                style={"marginBottom": "12px"},
                className="text-container",
            ),
        ]
    )


def model_comparison_summary_panel():
    """
    Returns a summary comparison table of the Poisson GLM and dynamic GMM models.
    Includes tooltips for each cell explaining model features and differences.
    """
    columns = [
        {"name": "Feature", "id": "feature"},
        {"name": "Poisson GLM", "id": "glm"},
        {"name": "Dynamic GMM", "id": "gmm"},
    ]

    data = [
        {
            "feature": "Goal",
            "glm": "Predict ROW given inequality",
            "gmm": "Identify dynamic/causal effects",
        },
        {
            "feature": "Endogeneity handled?",
            "glm": "No",
            "gmm": "Yes (lag instruments, FD)",
        },
        {
            "feature": "Best for",
            "glm": "Stable fit & simulation",
            "gmm": "Causal inference & timing",
        },
        {
            "feature": "Significant terms",
            "glm": "Gini (+), Gini² (–), LagROW (+)",
            "gmm": "Gini_t (–), Gini_{t−1} (+)",
        },
        {
            "feature": "Limitations",
            "glm": "Exogeneity assumption",
            "gmm": "Variance & instrument sensitivity",
        },
    ]

    tooltip_data = [
        {
            "feature": {"value": "What this row is about.", "type": "markdown"},
            "glm": {
                "value": "**GLM goal**\n\nLog-link Poisson count model; strong predictive fit.",
                "type": "markdown",
            },
            "gmm": {
                "value": "**GMM goal**\n\nHandle **endogeneity** and **lagged** effects.",
                "type": "markdown",
            },
        },
        {
            "feature": {
                "value": "Does the model address feedback loops?",
                "type": "markdown",
            },
            "glm": {
                "value": "Assumes exogenous regressors; possible bias.",
                "type": "markdown",
            },
            "gmm": {
                "value": "First differences + lagged instruments allow endogeneity.",
                "type": "markdown",
            },
        },
        {
            "feature": {"value": "Where this model shines.", "type": "markdown"},
            "glm": {
                "value": "Great **in-sample fit**; easy to **simulate**.",
                "type": "markdown",
            },
            "gmm": {
                "value": "Better for **causal direction** and **timing**.",
                "type": "markdown",
            },
        },
        {
            "feature": {
                "value": "Which coefficients matter most here.",
                "type": "markdown",
            },
            "glm": {
                "value": "**Gini (+)**, **Gini² (–)** ⇒ hump; **LagROW (+)**.",
                "type": "markdown",
            },
            "gmm": {
                "value": "**Gini_t (–)** now; **Gini_{t−1} (+)** later.",
                "type": "markdown",
            },
        },
        {
            "feature": {"value": "Main caveats to keep in mind.", "type": "markdown"},
            "glm": {"value": "No explicit fix for endogeneity.", "type": "markdown"},
            "gmm": {
                "value": "Estimate variability; instrument choice matters.",
                "type": "markdown",
            },
        },
    ]

    tooltip_header = {
        "feature": {"value": "Comparison dimension", "type": "markdown"},
        "glm": {"value": "Poisson GLM", "type": "markdown"},
        "gmm": {"value": "Dynamic GMM", "type": "markdown"},
    }

    return html.Div(
        [
            dash_table.DataTable(
                id="model-compare-table",
                columns=columns,
                data=data,
                tooltip_data=tooltip_data,
                tooltip_header=tooltip_header,
                tooltip_delay=150,
                tooltip_duration=None,
                style_as_list_view=True,
                style_table={
                    "overflowX": "auto",
                    "width": "100%",
                    "backgroundColor": "#FFFFFF",
                    "border": "1px solid #E2E8F0",
                    "borderRadius": "16px",
                    "boxShadow": "0 8px 20px rgba(0,0,0,0.08)",
                    "padding": "6px 8px",
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "10px 12px",
                    "fontFamily": "Georgia, serif",
                    "fontSize": "15px",
                    "color": "#1A202C",
                    "whiteSpace": "normal",
                    "height": "auto",
                    "border": "none",
                },
                style_header={
                    "fontWeight": "bold",
                    "color": NAVY,
                    "border": "none",
                    "backgroundColor": ACCENT,
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#F7FAFC"},
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "rgba(168,216,255,0.25)",
                    },
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "rgba(168,216,255,0.35)",
                    },
                    {
                        "if": {"column_id": "feature"},
                        "width": "26%",
                        "fontWeight": "600",
                    },
                    {"if": {"column_id": "glm"}, "width": "37%"},
                    {"if": {"column_id": "gmm"}, "width": "37%"},
                ],
                css=[
                    {
                        "selector": ".dash-table-tooltip",
                        "rule": (
                            "background-color: #FFFFFF; color: #1A202C; "
                            "border: 1px solid #D1D9E6; box-shadow: 0 6px 18px rgba(0,0,0,0.12); "
                            "font-family: Georgia, serif; font-size: 14px;"
                        ),
                    },
                    {
                        "selector": ".dash-table-container",
                        "rule": "border-radius: 16px; overflow: hidden;",
                    },
                ],
            ),
        ],
        className="card",
        style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "16px",
            "padding": "12px 16px",
        },
    )


def model_comparison_section():
    """
    Returns the layout section for model comparison.
    Includes explanatory text and the model comparison summary panel.
    """
    return html.Div(
        [
            html.H3("Poisson GLM vs Dynamic Panel GMM"),
            dcc.Markdown(
                "This section compares the Poisson GLM and dynamic panel GMM approaches, highlighting how each models the relationship between salary inequality and team performance, their strengths, limitations, and the distinct insights they provide.",
            ),
            dcc.Markdown(
                "**Hover over each cell in the table for more details.**",
                style={
                    "fontStyle": "italic",
                    "color": "#002244",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                model_comparison_summary_panel(),
                className="text-container",
            ),
        ]
    )


layout = html.Div(
    [
        html.Div(
            [
                # Title
                html.H1(
                    "Modeling the Impact of Salary Distribution on NHL Team Success"
                ),
                # Sub-heading and callout box
                html.Div(
                    [
                        html.H3("Interactive Visualizations & Simulations Based On:"),
                        html.Div(
                            [
                                dcc.Markdown(
                                    """
>**"Modeling the Impact of Salary Distribution on NHL Team Success"**
>*Sloane Holtby, McGill University*
>July 2025  
Read the full paper for detailed methodology and findings:https://sloholt.github.io/NHL-Salary-Inequality-Analysis/ 
""",
                                    style={"whiteSpace": "pre-line"},
                                )
                            ],
                            className="cta-box",
                        ),
                    ],
                ),
                # Key Metrics Cards
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Optimal Gini: 0.408", className="card-title"),
                                html.Div(
                                    "Performance-maximizing salary dispersion.",
                                    className="positive",
                                ),
                            ],
                            className="card",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    "Average Salary: $2.17M", className="card-title"
                                ),
                                html.Div(
                                    "Based on 2024-25 league AAVs", className="positive"
                                ),
                            ],
                            className="card",
                        ),
                    ],
                    className="kpi-row",
                ),
                # Overview block
                html.Div(
                    [
                        html.H2("Overview"),
                        html.Div(
                            dcc.Markdown(
                                """
This dashboard explores how NHL teams can optimize performance through strategic salary distribution. Drawing on ten seasons of data and leveraging Gini coefficients to measure intra-team inequality, the analysis reveals a concave relationship between salary dispersion and team success--suggesting that teams perform best when balancing high-paid stars with cost-effective depth players. Using both a Poisson Generalized Linear Model and a dynamic panel Generalized Method of Moments Model, the study identifies an optimal Gini coefficient of ~0.408, providing a practical benchmark for front offices aiming to maximize Regulation + Overtime Wins under the NHL's strict salary cap. Use this app to explore team-by-team salary structures, simulate roster scenarios, and examine how inequality has shaped historical performance.
"""
                            ),
                            className="text-container",
                        ),
                    ]
                ),
                # League-wide plot
                logo_scatter_section(),
                RED_LINE,
                html.H2("Team Explorer"),
                # Team Salary Display
                team_salary_selection(),
                # Gini vs ROW Display
                gini_vs_row_section(),
                # Divider
                RED_LINE,
                html.H2("Model Analysis & Comparison"),
                # GLM Model Display
                glm_model_section(),
                # GMM Model
                gmm_model_section(),
                # Model Comparisons
                model_comparison_section(),
                RED_LINE,
                # Footer
                html.Footer(
                    [
                        html.P("Sloane Holtby | McGill University"),
                        html.P(
                            "Based on research using Poisson GLM and GMM models on NHL salary data."
                        ),
                    ],
                    style={
                        "marginTop": "5px",
                        "textAlign": "center",
                        "fontSize": "1.15rem",
                        "color": "#1A202C",
                    },
                ),
            ],
            className="content",
        )
    ],
    className="page",
)
