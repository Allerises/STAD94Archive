library(tidyverse)
library(ggrepel)
library(MASS)

#Find the files in the project directory
standing_files <- list.files(path = "./Championship Standings", pattern = ".txt", full.names = T)
race_files <- list.files(path = "./Race Results", pattern = ".txt", full.names = T)
quali_files <- list.files(path = "./Quali Results", pattern = ".txt", full.names = T)

#Read them into the software
standings_results <- lapply(standing_files, read_tsv)
race_results <- lapply(race_files, read_tsv)
quali_results <- lapply(quali_files, read_tsv)

#Binding data into a single table
standings_results %>% bind_rows() -> standings_results
race_results <- do.call("rbind", race_results)
quali_results <- do.call("rbind", quali_results)

#Remove unnecessary variables
race_results %>% select(ID:Team) %>% select(!c(No, Nat)) -> race_results
quali_results %>% select(ID:Gap) %>% select(!c(Nat, Pos, No, Laps, Time, Team)) -> quali_results

#modify standings table to extract data from race table
standings_results$Points %>% replace_na(0) -> standings_results$Points
standings_results %>% rename(C_Points = Points) -> standings_results

#Combine data
race_results %>% left_join(quali_results, by = c("Year", "Race", "Driver")) -> RQ_Combined
race_results %>% left_join(standings_results, by = c("Year", "Driver")) -> standings_results

#Manipulate combined race table
RQ_Combined %>% rename(ID = ID.x, RoundNo = RoundNo.x, QualiGap = Gap) -> RQ_Combined #Rename the cols
RQ_Combined$QualiGap %>% replace_na(0) -> RQ_Combined$QualiGap #Set gap to 0 for polesitters
RQ_Combined %>% drop_na(ID.y, RoundNo.y) -> RQ_Combined #Remove rows with missing data
RQ_Combined %>% select(!c(ID.y, RoundNo.y)) -> RQ_Combined #Remove quali ID cols
RQ_Combined %>% mutate(across(QualiGap, as.double)) -> RQ_Combined #Turn quali positions to doubles

#Manipulate combined standings table
standings_results %>% select(c(Year, Driver, Team, Pos.y, C_Points)) %>% rename(Pos = Pos.y) -> standings_results
standings_results %>% drop_na(Pos, C_Points) -> standings_results
standings_results %>% distinct(Year, Driver, Team, Pos, C_Points) -> standings_results
standings_results %>% relocate(Team, .before = Driver) -> standings_results
standings_results %>% arrange(Team) %>% arrange(Year) -> standings_results

#Create unified ID
RQ_Combined %>% mutate(RaceID = str_c(Year, "-", Race, "-", Team)) %>%
  select(!c(ID, RoundNo, Year, Race, Team))-> RQ_Combined

RQ_Combined  %>% relocate(RaceID, .before = Pos) %>% 
  relocate(Driver, .before = Pos) %>% 
  arrange(RaceID) -> RQ_Combined

#Export table to python
write.table(RQ_Combined, file = 'RQ_Combined.txt', quote=FALSE, sep='\t', col.names = F)

#Import properly widened table back in
widened_results <- read_tsv("ActuallyWideResults.txt")
relative_results <- read_tsv("SingleDriverRelative.txt")

relative_results %>% group_by(Driver) %>%
  summarise(Number_of_Races = n(),
            Mean_Relative_Finishing_Position = mean(RelativePos),
            Mean_Relative_Qualifying_Gap = mean(RelativeQuali)) -> RQ_summary

#Drivers with fewer than 22 races in their career are cut off
RQ_summary %>% arrange(Number_of_Races) %>% filter(Number_of_Races >= 22) -> RQ_summary

#Removing reserve drivers and establishing which team a driver started the season in
standings_results %>% arrange(Pos) %>% arrange(Team) %>% arrange(Year) -> standings_results
standings_results %>% mutate(ID = row_number()) %>% relocate(ID, .before = Year) -> standings_results

standings_results %>% slice(-c(11, 34, 37, 38, 43, 44, 46, 47, 71, 78, 83, 86, 91, 100, 109, 116, 119,
                               122, 125, 126, 135, 136, 139, 142, 151, 158, 163, 168, 173, 174,
                               193, 195, 199, 206, 233, 234, 237, 244, 249, 252, 261, 262, 275,
                               288, 291, 300, 303, 320, 343, 360, 389, 409, 413, 417, 425, 440, 445, 448,
                               449, 484, 489, 496, 501, 506, 517)) -> cut_standings

#Exporting standings table to generate relative results
cut_standings %>% mutate(ID = str_c(Year, "-", Team)) %>% select(c(ID, Driver, Pos, C_Points)) -> cut_standings

write.table(cut_standings, file = 'cut_standings.txt', quote = F, sep = '\t', row.names = F, col.names = F)

#Reimporting relative standings table
relative_standings <- read_tsv("RelativeStandings.txt")

#Generating means for driver standing stats
relative_standings %>% group_by(Driver) %>%
  summarise(Number_of_Seasons = n(),
            Mean_Relative_Championship_Position = mean(RelativePos),
            Mean_Relative_Points = mean(Relative_CP)) -> Relative_standings_summary

#Combining race & quali summaries with standings summary
RQ_summary %>% left_join(Relative_standings_summary, by = c("Driver")) -> RQS_summary
RQS_summary %>% relocate(Number_of_Seasons, .after = Number_of_Races) -> RQS_summary

#Get the number of years a driver has been at a time
cut_standings %>% 
  separate(ID, c("Year", "Team"), sep = '-') %>% 
  mutate(Partnership = str_c(Team, "-", Driver)) %>% 
  group_by(Partnership) %>% summarise(n = n()) -> stint_summary

#Will need some manual editing
stint_summary %>% 
  separate(Partnership, c("Team", "Driver"), sep = "-") -> stint_summary
write.table(stint_summary, file = "stintsummary.txt", quote = F, sep = '\t', row.names = F, col.names = T)

#bring back into R for more manual editing
stint_fixed_summary <- read_tsv("stintsummary.txt")
stint_fixed_summary %>% mutate(ID = row_number()) %>% relocate(ID, .before = Team) -> stint_fixed_summary

stint_fixed_summary %>% rows_update(tibble(ID = 6, Team = "Aston Martin", Driver = "Sergio P<e9>rez", n = 2)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 7, Team = "BAR", Driver = "Jacques Villeneuve", n = 4)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 26, Team = "Ferrari", Driver = "Kimi R<e4>ikk<f6>nen", n = 8)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 33, Team = "Force India", Driver = "Nico H<fc>lkenberg", n = 4)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 35, Team = "Force India", Driver = "Sergio P<e9>rez", n = 5)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 37, Team = "Haas", Driver = "Esteban Guti<e9>rrez", n = 1)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 64, Team = "Lotus", Driver = "Kimi R<e4>ikk<f6>nen", n = 2)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 82, Team = "McLaren", Driver = "Kimi R<e4>ikk<f6>nen", n = 2)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 86, Team = "McLaren", Driver = "Sergio P<e9>rez", n = 1)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 130, Team = "Renault", Driver = "Nico H<fc>lkenberg", n = 3)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 136, Team = "Sauber", Driver = "Esteban Guti<e9>rrez", n = 2)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 143, Team = "Sauber", Driver = "Kimi R<e4>ikk<f6>nen", n = 3)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 147, Team = "Sauber", Driver = "Nico H<fc>lkenberg", n = 1)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 152, Team = "Sauber", Driver = "Sergio P<e9>rez", n = 2)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 168, Team = "Toro Rosso", Driver = "S<e9>bastien Buemi", n = 3)) -> stint_fixed_summary
stint_fixed_summary %>% rows_update(tibble(ID = 194, Team = "Williams", Driver = "Nico H<fc>lkenberg", n = 1)) -> stint_fixed_summary

#Get drivers' average stint lengths
stint_fixed_summary %>% group_by(Driver) %>% summarise(Mean_Stint_Length = mean(n)) -> stint_fixed_summary
RQS_summary %>% left_join(stint_fixed_summary, by = "Driver") -> RQS_summary

#Remove drivers who have an average stint length of less than 2 years
RQS_summary %>% filter(Mean_Stint_Length >= 2) -> RQS_summary
RQS_summary %>% select(-c(Mean_Relative_Points)) -> RQS_summary

#create labels for notable drivers
RQS_summary %>% add_column(labels = NA) %>% relocate(labels, .before = Driver) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Lewis Hamilton", labels = "Lewis Hamilton")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Michael Schumacher", labels = "Michael Schumacher")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Kimi R<e4>ikk<f6>nen", labels = "Kimi Raikkonen")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Rubens Barrichello", labels = "Rubens Barrichello")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Sebastian Vettel", labels = "Sebastian Vettel")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Jarno Trulli", labels = "Jarno Trulli")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Fernando Alonso", labels = "Fernando Alonso")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Felipe Massa", labels = "Felipe Massa")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Mika Hakkinen", labels = "Mika Hakkinen")) -> RQS_summary
RQS_summary %>% rows_update(tibble(Driver = "Nelson Piquet Jr.", labels = "Nelson Piquet Jr.")) -> RQS_summary

#Creating graphs
RQS_summary %>% ggplot(aes(x = Mean_Stint_Length,y = Mean_Relative_Finishing_Position)) +
  geom_point() + geom_smooth(se=F, linetype = "dashed") +
  geom_smooth(method = "lm", colour = "yellow", size = 1.1) + geom_text_repel(aes(label = labels)) +
  ggtitle("Mean Stint length vs. Mean Relative Race Result (Higher is better)") +
  xlab("Mean Stint Length (Years)") + ylab("Mean Relative Race Result (Position Diff.)")
RQS_summary %>% ggplot(aes(x = Mean_Stint_Length, y = Mean_Relative_Qualifying_Gap)) +
  geom_point() + geom_smooth(se=F, linetype = "dashed") +
  geom_smooth(method = "lm", colour = "yellow", size = 1.1) + geom_text_repel(aes(label = labels)) +
  ggtitle("Mean Stint length vs. Mean Relative Qualifying Gap (Higher is better)") +
  xlab("Mean Stint Length (Years)") + ylab("Mean Relative Qualifying Gap (Sec. Diff.)")
RQS_summary %>% ggplot(aes(x = Mean_Stint_Length, y = Mean_Relative_Championship_Position)) +
  geom_point() + geom_smooth(se=F, linetype = "dashed") +
  geom_smooth(method = "lm", colour = "yellow", size = 1.1) + geom_text_repel(aes(label = Driver)) +
  ggtitle("Mean Stint length vs. Mean Relative Championship Position (Higher is better)") +
  xlab("Mean Stint Length (Years)") + ylab("Mean Relative Championship Position (Position Diff.)")
RQS_summary %>% ggplot(aes(x = Number_of_Races, y = Mean_Stint_Length)) +
  geom_point() + geom_smooth(se=F, linetype = "dashed") +
  geom_smooth(method = "lm", colour = "yellow", size = 1.1) + geom_text_repel(aes(label = Driver)) +
  ggtitle("Career Length vs. Mean Stint Length") +
  ylab("Mean Stint Length (Years)") + xlab("Career Length (Races Entered)")
RQS_summary %>% ggplot(aes(x=Mean_Stint_Length)) +
  geom_histogram(bins = 8, fill = "sky blue", colour = "dark grey", size = 1.2) +
  ggtitle("Mean Stint Length Histogram") + xlab("Mean Stint Length (Years)")

#getting correlation values for each graph
cor(RQS_summary$Mean_Stint_Length, RQS_summary$Mean_Relative_Finishing_Position)
cor(RQS_summary$Mean_Stint_Length, RQS_summary$Mean_Relative_Qualifying_Gap)
cor(RQS_summary$Mean_Stint_Length, RQS_summary$Mean_Relative_Championship_Position)
cor(RQS_summary$Number_of_Races, RQS_summary$Mean_Stint_Length)

#creating a LM with the data
summary(lm(Mean_Stint_Length ~ Mean_Relative_Finishing_Position + Mean_Relative_Qualifying_Gap + Mean_Relative_Championship_Position, data = RQS_summary))
