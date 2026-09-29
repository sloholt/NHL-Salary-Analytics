#ROW Calculations & Residual Diagnosis for the GMM Model using real data 
library(dplyr)
library(ggplot2)
library(ggfortify)
library(pdynmc)
library(plm)

data <- read.csv("TeamData.csv")

data[,c("Gini","Gini2")]<-poly(data$Gini,2)

#Adding lagged vars & instruments
gmm_real_data <- data %>%
  group_by(Team) %>%
  arrange(Team, Year) %>%
  mutate(ROW_prev = dplyr::lag(ROW), 
         ROW_lag2 = dplyr::lag(ROW, 2))%>%
  ungroup()

gmm_real_data<-gmm_real_data%>%
  select(Team, Year, ROW, Gini, Gini2, ROW_prev, ROW_lag2) %>%
  na.omit()

valid_teams <- gmm_real_data %>%
  group_by(Team) %>%
  filter(n() >= 8) %>%
  ungroup()


#Checking for persistence
panel_data <- pdata.frame(valid_teams, index = c("Team", "Year"))

# Simple AR(1) panel model
persistence_model <- plm(ROW ~ lag(ROW, 1), data = panel_data, model = "within")
summary(persistence_model)

#GMM with pdynmc
gmm_model <- pdynmc(
  dat = valid_teams, 
  varname.i = "Team", varname.t = "Year", 
  
  #Dep variable 
  include.y = TRUE, 
  varname.y = "ROW", 
  lagTerms.y = 2,
  
  #Gini terms (endogenous regressors)
  include.x = TRUE, 
  varname.reg.end = c("Gini", "Gini2"),
  lagTerms.reg.end = c(1,1),
  maxLags.reg.end = c(3,3),
  
  #Moment Conditions
  use.mc.diff = TRUE, #First-differences 
  use.mc.lev = FALSE, #No level-based instruments 
  use.mc.nonlin = FALSE, #No nonlinear moments
  
  #Including year in fixed effects 
  include.dum = FALSE, 
  dum.diff = FALSE,
  dum.lev = FALSE,
  varname.dum = "Year", 
  
  #GMM 
  w.mat = "iid.err", #Weighted matrix 
  std.err = "corrected", #Windmeijer corrected
  estimation = "twostep" #SHOULD THIS BE 1 OR 2? 
  
)
#saveRDS(gmm_summary, "gmm_summary_table.rds")

summary(gmm_model)

summary(persistence_model)       

fitted_AR1 <- fitted(persistence_model)   
head(fitted_AR1)

# GMM Results table: 
gmm_summary <- as.data.frame(summary(gmm_model)$coefficients)
#write.csv(gmm_summary, "gmm_model_results.csv", row.names = FALSE)

gmm_summary <- gmm_summary %>%
  tibble::rownames_to_column(var = "Term") %>%
  rename(
    Estimate = Estimate,
    StdError = `Std.Err.rob`,
    zValue = `z-value.rob`,
    pValue = `Pr(>|z.rob|)`
  )
gmm_summary %>%
  gt() %>%
  tab_header(
    title = md("**GMM Coefficient Estimates**"),
  ) %>%
  fmt_number(
    columns = c(Estimate, StdError, zValue, pValue),
    decimals = 4
  ) %>%
  # Red borders on header row
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
    heading.align = "center",
  )














