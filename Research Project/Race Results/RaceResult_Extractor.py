from requests import *
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import *
import os
import time

def ExtractPage(ID, year, race, roundNo):
    # CreateURL and access webpage
    url = "https://fiaresultsandstatistics.motorsportstats.com/results/"
    raceURL = url + str(year) + "-" + race.replace(' ', '-').lower() + "/classification"

    resp = get(raceURL)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")  # Success debug message

        # Create data file
        data = soup.find_all("td", {"class": "_2sWDi"})
        filename = os.path.dirname(__file__) + "\\" + str(ID) + "-" + str(roundNo) + "-" + str(year) + "-" + race.replace(' ', '-') + ".txt"
        newFile = open(filename, 'w')

        newFile.write("ID\tRoundNo\tYear\tRace\tPos\tNo\tDriver\tNat\tTeam\tLaps\tTime\tGap\tInterval\tKph\tBest\tLap\n")

        n = 0
        
            
        try:  # Checks if the user entered a valid Grand Prix and then writes its results onto a text file
            pos = 0
            for i in data:
                datum = i.text
                #print(i.string)
                if n == 0:
                    newFile.write(str(ID) + "\t" + str(roundNo) + "\t" + str(year) + "\t" + race + "\t")
                    pos = pos + 1
                    datum = pos
                    newFile.write(str(datum) + "\t")
                    n = n + 1
                elif n < 11:
                    if(n == 4):
                        datum = SetConstructorName(datum)
                    newFile.write(str(datum) + "\t")
                    n = n + 1
                else:
                    newFile.write(str(datum) + "\n")
                    n = 0

            newFile.close()
            print("Done - File Ready")

        except Exception as e:
            newFile.close()
            if os.path.exists(filename):
                os.remove(filename)

            
            print(year, race, "does not exist or\n", e, )

    else:
        print("Code", resp.status_code, "Accessing FIA Website: FAILED")  # Failure debug message

def BatchExtractor(start, end):
    startYear = start
    endYear = end

    n = 0

    for i in range(startYear, endYear + 1):
        baseURL = "https://fiaresultsandstatistics.motorsportstats.com/results/" + str(i) + "-british-grand-prix/classification/"

        resp = get(baseURL)

        if resp.status_code == 200:
            print("Code", resp.status_code, "Accessing FIA Website: SUCCESS")
            soup = BeautifulSoup(resp.text, "html.parser")  # Success debug message

            # Create data file
            data = soup.find_all("a", {"class": "_3AdU8"})
            try:
                k = 1
                for j in data:
                    j=j.string
                    if "Season Test" not in j:
                        print("Accessing Data for the", i, j)
                        ExtractPage(n, i, j, k)
                        time.sleep(0)
                        n = n + 1
                        k = k + 1

            except:
                print("Error")

        print("Loading the", i+1, "season...")
        time.sleep(0)


def SetConstructorName(Name):
    if ("Midland" in Name):
        return "Nidland"
    if ("Jordan" in Name):
        return "Jordan"
    if ("Brawn" in Name):
        return "Brawn"
    if ("Super Aguri" in Name):
        return "Super Aguri"
    if ("BAR" in Name):
        return "BAR"
    if ("Virgin" in Name):
        return "Virgin"
    if ("Manor" in Name):
        return "Manor"
    if ("Marussia" in Name):
        return "Marussia"
    if ("Caterham" in Name):
        return "Caterham"
    if ("Spyker" in Name):
        return "Spyker"
    if ("HRT" in Name):
        return "HRT"
    if ("Prost" in Name):
        return "Prost"
    if ("Minardi" in Name):
        return "Minardi"
    if ("Benneton" in Name):
        return "Benneton"
    if("Ferrari" in Name):
        return "Ferrari"
    if("McLaren" in Name):
        return "McLaren"
    if("Williams" in Name):
        return "Williams"
    if("Toyota" in Name):
        return "Toyota"
    if("Haas" in Name):
        return "Haas"
    if("Force India" in Name):
        return "Force India"
    if("Alfa Romeo" in Name or "Sauber" in Name):
        return "Sauber"
    if ("AlphaTauri" in Name or "Toro Rosso" in Name):
        return "Toro Rosso"
    if ("Red Bull" in Name):
        return "Red Bull"
    if("Racing Point" in Name or "Aston Martin" in Name):
        return "Aston Martin"
    if("Tyrrel" in Name):
        return "Tyrrel"
    if("Ligier" in Name):
        return "Ligier"
    if("Footwork" in Name):
        return "Footwork"
    if("Honda" in Name):
        return "Honda"
    if("Mercedes" in Name):
        return "Mercedes"
    if("Benetton" in Name):
        return "Benneton"
    if("Alpine" in Name or "Renault" in Name):
        return "Renault"
    if ("Lotus" in Name):
        return "Lotus"
    if("Arrows" in Name):
        return "Arrows"
    if("Lola" in Name):
        return "Lola"
    if("March" in Name):
        return "March"
    if("Jaguar" in Name):
        return "Jaguar"
    if("Larousse" in Name):
        return "Larousse"
    else:
        return Name
    


#Creating the GUI
root = tk.Tk()
root.title("Race Result Generation Utility")
#root.geometry("430x150")
root.resizable(False, False)

frame = tk.Frame(root)
options = {'padx': 5, 'pady': 5}

yearTitle = tk.Label(frame, text = "Year")
yearTitle.grid(column = 1, row = 0, sticky = 'S', **options)
raceTitle = tk.Label(frame, text = "Race")
raceTitle.grid(column = 2, row = 0, sticky = 'S', **options)

singleRace = tk.Label(frame, text = "Single Race")
singleRace.grid(column = 0, row = 1, sticky = 'W', **options)
SRYear = tk.IntVar()
SRYEntry = tk.Entry(frame, textvariable = SRYear)
SRYEntry.grid(column = 1, row = 1, **options)
SRRace = tk.StringVar()
SRREntry = tk.Entry(frame, textvariable = SRRace)
SRREntry.grid(column = 2, row = 1, **options)
SRButton = tk.Button(frame, text="Parse")
SRButton.grid(column = 3, row = 1, **options)
SRButton.configure(command = lambda: ExtractPage(-1, SRYear.get(), SRRace.get(), 0))

singleYear = tk.Label(frame, text = "Single Year")
singleYear.grid(column = 0, row = 2, sticky = 'W', **options)
SYYear = tk.IntVar()
SYYEntry = tk.Entry(frame, textvariable = SYYear)
SYYEntry.grid(column = 1, row = 2, **options)
SYButton = tk.Button(frame, text="Parse")
SYButton.grid(column = 3, row = 2, **options)
SYButton.configure(command = lambda: BatchExtractor(SYYear.get(), SYYear.get()))

startTitle = tk.Label(frame, text = "First Year")
startTitle.grid(column = 1, row = 3, sticky = 'S', **options)
endTitle = tk.Label(frame, text = "Last Year")
endTitle.grid(column = 2, row = 3, sticky = 'S', **options)

multiYear = tk.Label(frame, text = "Multiple Years")
multiYear.grid(column = 0, row = 4, sticky = 'W', **options)
MYStart = tk.IntVar()
MYSEntry = tk.Entry(frame, textvariable = MYStart)
MYSEntry.grid(column = 1, row = 4, **options)
MYEnd = tk.IntVar()
MYEEntry = tk.Entry(frame, textvariable = MYEnd)
MYEEntry.grid(column = 2, row = 4, **options)
MYButton = tk.Button(frame, text="Parse")
MYButton.grid(column = 3, row = 4, **options)
MYButton.configure(command = lambda: BatchExtractor(MYStart.get(), MYEnd.get()))

frame.grid(padx = 10, pady = 10)
root.mainloop()
