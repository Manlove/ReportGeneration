# Load required packages
library(ggplot2)
library(dplyr)

projects <- read.csv("/Users/lmanlove/Downloads/Services Analysis Tracker.csv")
# Filter for projects with status "invoiced" and invoice date in 2024
invoiced_projects_2024 <- projects %>% filter(Status == "Invoiced",format(as.Date(DeliveryDate, format = "%m/%d/%Y"), "%Y") == "2024")

# Create a histogram with weekly bins
ggplot(invoiced_projects_2024, aes(x = as.Date(DeliveryDate, format = "%m/%d/%Y"))) +
  geom_histogram(binwidth = 30.44, color = "black", fill = "skyblue") +
  labs(title = "Monthly Histogram of Delivered Projects in 2024",
       x = "Delivery Date",
       y = "Number of Projects") +
  scale_x_date(date_labels = "%b %y", date_breaks = "1 month") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))
