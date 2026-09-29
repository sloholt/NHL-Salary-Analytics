#Salary Distribution Calculations 

library(readxl)
library(dplyr)
library(gt)

sal_data <- read_excel("NHL_Combined_Cap_Hits_2015-2025.xlsx")

team_salary_stats <- sal_data %>%
  group_by(Team, Year) %>%
  summarise(
    team_avg_salary = mean(`Cap Hit`, na.rm = TRUE),
    team_salary_sd = sd(`Cap Hit`, na.rm = TRUE),
    .groups = 'drop'
  )

sal_summary <- data.frame(
  Variable = c("Nominal Team Average Salary", "Nominal Team Salary Std. Deviation"),
  Mean = as.character(round(c(
    mean(team_salary_stats$team_avg_salary, na.rm = TRUE),
    mean(team_salary_stats$team_salary_sd, na.rm = TRUE)
  ), 0)),
  `Standard Deviation` = as.character(round(c(
    sd(team_salary_stats$team_avg_salary, na.rm = TRUE),
    sd(team_salary_stats$team_salary_sd, na.rm = TRUE)
  ), 0)),
  Minimum = as.character(round(c(
    min(team_salary_stats$team_avg_salary, na.rm = TRUE),
    min(team_salary_stats$team_salary_sd, na.rm = TRUE)
  ), 0)),
  Maximum = as.character(round(c(
    max(team_salary_stats$team_avg_salary, na.rm = TRUE),
    max(team_salary_stats$team_salary_sd, na.rm = TRUE)
  ), 0)),
  stringsAsFactors = FALSE
)

team_data <- read.csv("TeamData.csv")

gini_mean <- round(mean(team_data$Gini, na.rm = TRUE), 3)
gini_sd <- round(sd(team_data$Gini, na.rm = TRUE), 3)
gini_min <- round(min(team_data$Gini, na.rm = TRUE), 3)
gini_max <- round(max(team_data$Gini, na.rm = TRUE), 3)

roster_mean <- round(mean(team_data$RosterSize, na.rm = TRUE))
roster_sd <- round(sd(team_data$RosterSize, na.rm = TRUE))
roster_min <- round(min(team_data$RosterSize, na.rm = TRUE))
roster_max <- round(max(team_data$RosterSize, na.rm = TRUE))
additional_summary <- data.frame(
  Variable = c("Team Salary Gini Coefficient", "Team Roster Size"),
  Mean = c(gini_mean, as.character(roster_mean)),
  `Standard Deviation` = c(gini_sd, as.character(roster_sd)),
  Minimum = c(gini_min, as.character(roster_min)),
  Maximum = c(gini_max, as.character(roster_max)),
  stringsAsFactors = FALSE
)


#Combining tables 
sal_summary[] <- lapply(sal_summary, as.character)
combined_summary <- rbind(sal_summary, additional_summary)

combined_summary %>%
  gt() %>%
  tab_header(
    title = md("**Team Salary & Structure Summary**")
  ) %>%
  cols_label(
    Variable = "Variable",
    Mean = "Mean",
    `Standard.Deviation` = "Std. Deviation",
    Minimum = "Minimum",
    Maximum = "Maximum"
  ) %>%
  tab_style(
    style = cell_borders(
      sides = c("top", "bottom"),
      color = "#B22222",
      weight = px(3)
    ),
    locations = cells_column_labels(everything())
  ) %>%
  # Navy borders between rows
  tab_style(
    style = cell_borders(
      sides = "top",
      color = "#002244",
      weight = px(1)
    ),
    locations = cells_body(rows = everything())
  ) %>%
  # Navy header text
  tab_style(
    style = list(
      cell_text(color = "#002244", weight = "bold")
    ),
    locations = cells_column_labels(everything())
  ) %>%
  # Table design settings
  tab_options(
    table.background.color = "#F7FAFC",
    heading.background.color = "#F7FAFC",
    column_labels.background.color = "#F7FAFC",
    table.border.top.color = "#F7FAFC",
    table.border.bottom.color = "#F7FAFC",
    heading.align = "center"
  )
saveRDS(combined_summary, "combined_salary_summary.rds")

