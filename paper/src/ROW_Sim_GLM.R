#Simulating ROW Data using a Poisson Distribution and Log-Link GLM 
library(dplyr)
library(ggplot2)
library(ggfortify)
library(tibble)
library(tidyverse)
library(gt)

data <- read.csv("TeamData.csv")

#Lagged ROW column 
data <- data %>% 
  arrange(Team, Year) %>%
  group_by(Team) %>%
  mutate(ROW_prev_actual = dplyr::lag(ROW)) %>%
  ungroup()

#######################################################
#UPDATED SIMULATION WITH POISSON MODEL & UNCENTERED
######################################################

simulate_row <- function(beta0, beta1, beta2, beta3){
  
  data <- data %>% arrange(Team, Year)
  data$ROW_sim <- NA 
  teams <- unique(data$Team)
  
  for (team in teams){ 
    team_data <- data %>% filter(Team == team) #all rows for current team 
    
    for (i in 1:nrow(team_data)){
      year <- team_data$Year[i] 
      
      if (year == min(team_data$Year)){ #keeping actual ROW for first year 
        data$ROW_sim[data$Team == team & data$Year == year] <- team_data$ROW[i]
      }else { 
        #For al other years, simulate the ROW with the previous years simulated ROW 
        prev_sim <- data$ROW_sim[data$Team == team & data$Year == (year - 1)]
        gini <- team_data$Gini[i]
        gini2 <- gini^2
        
        log_mu <- beta0 + 
          beta1 * (gini) + 
          beta2 * (gini2) +
          beta3 * (prev_sim)
        mu <- exp(log_mu)
        
        sim_row <- rpois(1, lambda = mu)
        data$ROW_sim[data$Team == team & data$Year == year] <- sim_row
      }
    }
    
  }
  return(data)
}


#Our version of one_VAR_sim to simulate one 20yr dataset & estimate the coefficients with GLM
one_ROW_sim <- function(data){
  
  #GLM on actual data for starting coeffs
  glm_fit <- glm(
    ROW ~ poly(Gini,2) + ROW_prev_actual,
    family = poisson(link = "log"),
    data = data
  )
  
  beta0 <- coef(glm_fit)[1]
  beta1 <- coef(glm_fit)[2]
  beta2 <- coef(glm_fit)[3]
  beta3 <- coef(glm_fit)[4]
  
  #Sim new ROW values
  sim_data <- simulate_row(beta0, beta1, beta2, beta3)
  
  #GLM on simulated data 
  sim_glm <- glm(
    ROW_sim ~ poly(Gini,2) + ROW_prev_actual,
    family = poisson(link = "log"),
    data = sim_data
  )
  
  #return(autoplot(glm_fit))
  #return(coef(glm_fit))
  return(sim_glm)
}

#Running one simulation & visualizing 
my_model<- one_ROW_sim(data)
summary(my_model)
autoplot(my_model)
plot(fitted(my_model), my_model$y)

sd(data$Gini)


#100 Replications of simulation
set.seed(123)
rep_results <- replicate(100, 
                         coef(one_ROW_sim(data)),
                         simplify = "matrix")
rep_results_df_uncentered <- as.data.frame(t(rep_results))
colnames(rep_results_df_uncentered) <- c("Intercept", "Gini_UnCentered", "Gini2_UnCentered", "LagROW_UnCentered")
write.csv(rep_results_df_uncentered, "row_simulation_results.csv", row.names = FALSE)

saveRDS(sim_stats, "glm_sim_stats.rds")

dim(rep_results_df_uncentered)

# Boxplots
ggplot(rep_results_df_uncentered, aes(y = Intercept)) + geom_boxplot()
ggplot(rep_results_df_uncentered, aes(y = Gini_UnCentered)) + geom_boxplot()
ggplot(rep_results_df_uncentered, aes(y = Gini2_UnCentered)) + geom_boxplot()
ggplot(rep_results_df_uncentered, aes(y = LagROW_UnCentered)) + geom_boxplot()

#Combined Boxplots
rep_results_long <- rep_results_df_uncentered %>%
  pivot_longer(cols = everything(), 
               names_to = "Coefficient", 
               values_to = "Estimate")

# Create combined boxplot
ggplot(rep_results_long, aes(x = Coefficient, y = Estimate)) +
  geom_boxplot(
    fill = "#A8D8FF",       # Positive Contrast
    color = "#002244",      # Accent/Primary
    outlier.shape = 21,
    outlier.fill = "#B22222",  # CTA / Highlights
    outlier.color = "#002244"
  ) +
  theme_minimal(base_size = 14, base_family = "Abhaya Libre") +
  theme(
    plot.background = element_rect(fill = "#F7FAFC", color = NA),  # Background
    panel.background = element_rect(fill = "#F7FAFC", color = NA),
    panel.grid.major = element_line(color = "#D9E2EC"),
    panel.grid.minor = element_blank(),
    plot.title = element_text(color = "#1A202C", face = "bold"),
    axis.title = element_text(color = "#1A202C"),
    axis.text = element_text(color = "#1A202C")
  ) +
  labs(
    title = "Distribution of Estimated Coefficients Across 100 Simulated Runs",
    x = "Coefficient",
    y = "Estimated Value"
  )


# Faceted histogram
ggplot(rep_results_long, aes(x = Estimate)) +
  geom_histogram(bins = 30, fill = "steelblue", color = "white") +
  facet_wrap(~ Coefficient, scales = "free") +  # 'scales = "free"' lets each panel scale independently
  theme_minimal(base_size = 14) +
  labs(
    title = "Histogram of Estimated Coefficients Across 100 Simulated Runs",
    x = "Estimate",
    y = "Count"
  )


summary_stats <- rep_results_df_uncentered %>%
  summarise(across(everything(), list(mean = mean, sd = sd, IQR = IQR)))
summary_stats

#GLM Sim Results Table 
sim_stats <- data.frame(
  Intercept_mean = 3.106044,
  Intercept_sd = 0.0650607,
  Intercept_IQR = 0.1026177,
  Gini_mean = -0.7567526,
  Gini_sd = 0.2553087,
  Gini_IQR = 0.3165708,
  Gini2_mean = 0.004234288,
  Gini2_sd = 0.2804508,
  Gini2_IQR = 0.3808954,
  LagROW_mean = 0.001751037,
  LagROW_sd = 0.001731994,
  LagROW_IQR = 0.002470845
)
sim_stats_long <- sim_stats %>%
  pivot_longer(cols = everything(), names_to = "Metric", values_to = "Value") %>%
  separate(Metric, into = c("Coefficient", "Statistic"), sep = "_(?=mean|sd|IQR)") %>%
  pivot_wider(names_from = Statistic, values_from = Value)
sim_stats_long <- sim_stats_long %>%
  rename(
    `Mean` = mean,
    `Std. Deviation` = sd,
    `IQR` = IQR
  )

sim_stats_long %>%
  gt() %>%
  tab_header(
    title = md("**Summary of Simulated Coefficients**")
  ) %>%
  fmt_number(
    columns = c(Mean, `Std. Deviation`, IQR),
    decimals = 4
  ) %>%
  tab_style(
    style = cell_borders(
      sides = c("top", "bottom"),
      color = "#B22222",
      weight = px(3)
    ),
    locations = cells_column_labels(everything())
  ) %>%
  tab_style(
    style = cell_borders(
      sides = "top",
      color = "#002244",
      weight = px(1)
    ),
    locations = cells_body(rows = everything())
  ) %>%
  tab_style(
    style = list(
      cell_text(color = "#002244", weight = "bold")
    ),
    locations = cells_column_labels(everything())
  ) %>%
  tab_options(
    table.background.color = "#F7FAFC",
    heading.background.color = "#F7FAFC",
    column_labels.background.color = "#F7FAFC",
    table.border.top.color = "#F7FAFC",
    table.border.bottom.color = "#F7FAFC",
    heading.align = "center"
  )



