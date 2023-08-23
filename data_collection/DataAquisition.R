install.packages("dplyr")
install.packages("fitzRoy")
library(fitzRoy)
library(dplyr)

data<- fetch_fixture(season = 2023, comp = "AFLM")
head(data)
