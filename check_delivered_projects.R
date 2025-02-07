# Takes, as input, the csv file output by check_delivered_projects.py
# and creates two plots with the data.

# Load necessary libraries
library(ggplot2)
library(dplyr)

# Read the data (replace 'your_data.csv' with your actual data file)
# Assuming your data file is a CSV, if it's not adjust accordingly
data <- read.csv('',sep=",", stringsAsFactors = FALSE)

# Inspect the data
str(data)
head(data)

# Convert Date to Date type and handle any conversion issues
data$Date <- as.Date(data$Date, format="%m/%d/%Y")
if (any(is.na(data$Date))) {
  stop("There are invalid date entries. Please check the 'Date' column.")
}

# Ensure Amount is numeric and handle any non-numeric values
data$Amount <- as.numeric(data$Amount)
if (any(is.na(data$Amount))) {
  stop("There are non-numeric values in the 'Amount' column. Please check and clean the data.")
}

# Convert Date to Date type
data$Date <- as.Date(data$Date, format="%Y-%m-%d")

# Arrange data by Informatician and Date
data <- data %>%
  arrange(Date, Informatician)

# Calculate cumulative sum of Amount by Informatician
data <- data %>%
  group_by(Informatician) %>%
  mutate(cumulative_amount = cumsum(Amount))

# Plot the data
ggplot(data, aes(x = Date, y = cumulative_amount, color = Informatician)) +
  geom_line() +
  labs(title = "Cumulative Sum of Invoice Amounts Over Time by Informatician",
       x = "Date",
       y = "Cumulative Sum of Amount") +
  theme_minimal()

data <- data %>%
  group_by(Informatician) %>%
  mutate(cumulative_projects = cumsum(!is.na(Quote)))

# Plot the data
ggplot(data, aes(x = Date, y = cumulative_projects, color = Informatician)) +
  geom_line() +
  labs(title = "Cumulative Number of Projects Over Time by Informatician",
       x = "Date",
       y = "Cumulative Number of Projects") +
  theme_minimal()

