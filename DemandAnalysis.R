install.packages("tidyverse")
install.packages("lubridate")
install.packages("leaflet")
library(tidyverse)
library(lubridate)
library(leaflet)

# Read in the data
demand <- read_csv('demandDataByStore.csv')
demand_gather <- gather(demand, key="Date", value=Demand, ends_with("2020"))

# Filter out days with zero demand
demand_gather = filter(demand_gather, Demand > 0)

# Pass in date format into lubridate
demand_gather$Date = parse_date_time(demand_gather$Date,"dmy")

# Create a factor with the days of the week
demand_gather$Day = as.factor(wday(demand_gather$Date, label = TRUE))


# Box plot of demands across each store
g=ggplot(data = demand_gather, mapping=aes(x = Day, y = Demand))
g+geom_boxplot(aes(fill=Store), position=position_dodge(1))+
  labs(title="Daily Demand by Store Grouped Box Plot")

# Summary of boxplot
demand_gather %>%
  group_by(Day,Store) %>%
  summarise(Min = min(Demand, na.rm=TRUE),
            Max = max(Demand, na.rm=TRUE),
            Median = median(Demand, na.rm=TRUE),
            Mean = mean(Demand, na.rm=TRUE),
            LQ = quantile(Demand, 0.25, na.rm=TRUE),
            UQ = quantile(Demand, 0.75, na.rm=TRUE),
            IQRange = IQR(Demand, na.rm=TRUE)) %>%
  write.table(file = "dmnd_boxplot_stats.csv", row.names = FALSE)


# Summarise day by day averages
demand_grouped = group_by(demand_gather,Day,Store)
demand_summarised = summarise(filter(demand_grouped, Demand>0), MD=mean(Demand,
                                                                        na.rm = TRUE))
demand_summarised

# Summarise day-by-day avg demands, by location and store
demand_grouped_loc = group_by(demand_gather,Day,Store,Location)
demand_summarised_loc = summarise(demand_grouped_loc, Mean_Demand = ceiling(mean(Demand,
                                                                                 na.rm = TRUE)),
                                  Std_Dev = round(sd(Demand, na.rm = TRUE),3))

write.table(demand_summarised_loc , file = "dmnd_avgs.csv", row.names = FALSE)
