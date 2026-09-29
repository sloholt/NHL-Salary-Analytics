#Simulating ROW Data using a Generalized Method of Moments model 

library(dplyr)
library(gmm)

data <- read.csv("TeamData.csv")

simulate_row <- function(beta1, beta2, alpha, sigma_eps = 5){
  
  data <- data %>% arrange(Team, Year)
  data$ROW_sim <- NA 
  teams <- unique(data$Team)
  team_effects <- rnorm(length(teams), mean = 0, sd = 1)
  names(team_effects) <- teams
  
  
  for (team in teams){ 
    team_data <- data %>% filter(Team == team) #all rows for current team 
    
    for (i in 1:nrow(team_data)){
      year <- team_data$Year[i]
      idx <- which(data$Team == team & data$Year == year)
      
      if (year == min(team_data$Year)){ #keeping actual ROW for first year 
        data$ROW_sim[idx] <- team_data$ROW[i]
      }else { 
        #For al other years, simulate the ROW with the previous years simulated ROW 
        prev_sim <- data$ROW_sim[data$Team == team & data$Year == (year - 1)]
        gini <- team_data$Gini[i]
        gini2 <- team_data$Gini2[i]
        eta_i <- team_effects[team]
        epsilon <- rnorm(1, mean = 0, sd = sigma_eps)
        
        mu <- alpha * prev_sim + beta1 * gini + beta2 * gini2 + eta_i + epsilon
        data$ROW_sim[idx] <- pmax(mu, 0)      }
    }
    
  }
  return(data)
}


one_ROW_sim_gmm <- function(data){
  #lagged and transformed variables
  data <- data %>%
    arrange(Team, Year) %>%
    group_by(Team) %>%
    mutate(
      ROW_prev = lag(ROW),
    ) %>%
    ungroup()
  
  gmm_data <- data %>%
    select(ROW, Gini, Gini2, ROW_prev) %>%
    na.omit()
  
  #Starting coef from real GMM 
  ols_fit <- lm(ROW ~ Gini + Gini2 + ROW_prev, data = gmm_data)
  summary(ols_fit)
  
  alpha <- min(coef(ols_fit)[4], 0.8)
  #alpha <- coef(ols_fit)[4]
  beta1 <- coef(ols_fit)[2]
  beta2 <- coef(ols_fit)[3]

  #Simulate data 
  #sim_data <- simulate_row(beta1 = beta1, beta2 = beta2, alpha = alpha)
  sim_data <- simulate_row(beta1 = 100, beta2 = -100, alpha = 0)
  cor(sim_data$ROW_sim, dplyr::lag(sim_data$ROW_sim))
  

  gmm_sim <- sim_data %>%
    arrange(Team, Year) %>%
    group_by(Team) %>%
    mutate(
      ROW_prev_sim = lag(ROW_sim),
      ROW_lag_sim = lag(ROW_sim, 2),
      Gini2 = Gini^2
    ) %>%
    ungroup() %>%
    select(ROW_sim, Gini, Gini2, ROW_prev_sim, ROW_lag_sim) %>%
    na.omit()
  
  #Moment conditions
  gmm_moments <- function(theta, data){
    y <- data$ROW_sim
    x <- cbind(1, data$Gini, data$Gini2, data$ROW_prev_sim)
    z <- cbind(1, data$Gini, data$Gini2, data$ROW_lag_sim)
    res <- as.numeric(y - x %*% theta)
    moments <- res * z
    return(moments)
  }
  
  #GMM 
  theta_start <- rep(0, 4)
  gmm_model <- gmm(g = gmm_moments, x = gmm_sim, t0 = theta_start)
  return(gmm_model)
}

sim_result <- one_ROW_sim_gmm(data)
summary(sim_result)



