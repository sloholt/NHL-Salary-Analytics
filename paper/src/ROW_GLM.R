#Residual Diagnosis of GLM model with real data 
library(dplyr)
library(ggplot2)
library(ggfortify)
library(tibble)
library(gt)


#data <- read.csv("TeamData.csv")
data <- read.csv("Teams.csv")
#Lagged ROW column 
data <- data %>% 
  arrange(Team, Year) %>%
  group_by(Team) %>%
  mutate(ROW_prev_actual = dplyr::lag(ROW)) %>%
  ungroup()
model_data <- data %>% filter(!is.na(ROW_prev_actual))
View(data)

write.csv(data, "Teams.csv", row.names = FALSE)

#REAL GLM MODEL:
real_glm <- glm(
  ROW ~ poly(Gini,2) + ROW_prev_actual,
  family = poisson(link = "log"),
  data = model_data
)
summary(real_glm)

glm_summary <- as.data.frame(summary(real_glm)$coefficients)

write.csv(glm_summary, "glm_model_results.csv", row.names = FALSE)


autoplot(real_glm, which = 1:6, ncol = 2) +
  theme_minimal(base_family = "Abhaya Libre") +
  theme(
    plot.background = element_rect(fill = "#F7FAFC", color = NA),
    panel.background = element_rect(fill = "#F7FAFC", color = NA),
    panel.grid.major = element_line(color = "#A8D8FF"),
    panel.grid.minor = element_blank(),
    strip.background = element_rect(fill = "#A8D8FF", color = NA),
    strip.text = element_text(color = "#002244", size = 12, face = "bold"),
    axis.text = element_text(color = "#2D3748"),
    axis.title = element_text(color = "#002244", face = "bold"),
    plot.title = element_text(color = "#B22222", face = "bold", hjust = 0.5)
  )

cov2cor(vcov(real_glm))

update(real_glm, .~ . - poly(Gini,2))
anova(real_glm)
anova(update(real_glm, .~ROW_prev_actual+poly(Gini,2)))

#DEVIANCE RESIDUALS: 
res <- residuals(real_glm, type = "deviance")
fitted_vals <- fitted(real_glm)

ggplot(data.frame(Fitted = fitted_vals, Residuals = res), aes(x = Fitted, y = Residuals)) +
  geom_point() +
  geom_hline(yintercept = 0, linetype = "dashed") +
  theme_minimal() +
  labs(title = "Deviance Residuals vs Fitted Values")

#VALIDITY CHECKS: 

#Overdispersion: 
summary(real_glm)$deviance / summary(real_glm)$df.residual
#Influence:
influence_measures <- influence.measures(real_glm)
summary(influence_measures)
#plot(cooks.distance(real_glm), type = "h", main = "Cook's Distance")
cd <- cooks.distance(real_glm)
par(bg = "#F7FAFC")

plot(cd,
     type = "h",
     lwd = 2,
     col = "#002244",       
     main = "Cook's Distance",
     xlab = "Observation",
     ylab = "Cook's Distance",
     col.main = "#B22222",  
     col.lab = "#002244",   
     col.axis = "#2D3748",
     plot.background = element_rect(fill = "#F7FAFC", color = NA),
     panel.background = element_rect(fill = "#F7FAFC", color = NA),
)
top_n <- order(cd, decreasing = TRUE)[1:3]
text(x = top_n, y = cd[top_n], labels = top_n, pos = 3, col = "#B22222")

#OPTIMAL GINI CALCULATIONS: 
glm_raw <- glm(
  ROW ~ Gini + Gini2 + ROW_prev_actual,
  family = poisson(link = "log"),
  data = data
)
summary(glm_raw)

beta1 <- coef(glm_raw)["Gini"]
beta2 <- coef(glm_raw)["Gini2"]

Gini_optimal <- -beta1 / (2 * beta2)
Gini_optimal

#GLM Results Table
glm_summary <- summary(real_glm)$coefficients
glm_table <- as.data.frame(glm_summary)
glm_table %>%
  gt() %>%
  tab_header(
    title = "Poisson GLM Coefficients",
    subtitle = "Model: ROW ~ poly(Gini, 2) + ROW_prev_actual"
  ) %>%
  fmt_number(
    columns = c(Estimate, `Std. Error`, `z value`, `Pr(>|z|)`),
    decimals = 4
  )

glm_summary <- summary(real_glm)$coefficients
glm_table <- as.data.frame(glm_summary)

glm_table %>%
  gt() %>%
  tab_header(
    title = md("**Poisson GLM Coefficients**"),
  ) %>%
  fmt_number(
    columns = c(Estimate, `Std. Error`, `z value`, `Pr(>|z|)`),
    decimals = 4
  ) %>%
  tab_style(
    style = cell_borders(
      sides = "top",
      color = "#B22222",
      weight = px(3)
    ),
    locations = cells_column_labels(everything())
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
    heading.align = "center",
  )
