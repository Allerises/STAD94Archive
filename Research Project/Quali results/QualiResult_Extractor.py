from requests import *
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import *
import os
import time

def ExtractPage(ID, year, race, roundNo):
    # CreateURL and access webpage
    url = "https://fiaresultsandstatistics.motorsportstats.com"
    raceURL = url + "/results/" + str(year) + "-" + race.replace(' ', '-').lower() + "/classification"
    print(raceURL)

    resp = get(raceURL)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")  # Success debug message

        #Get to the qualifying results page
        data = soup("a", {"class": "uaJW4 _2j84j"})
        for i in data:
            if i.text == "Grid" or i.text == "Qualifying": #Some races only have one or the other
                qualiURL = url + i.get('href')
                print("Using", i.text)
                break
        resp = get(qualiURL)
        soup = BeautifulSoup(resp.text, "html.parser")

        #Access qualifying/grid table and create its file
        data = soup("td", {"class": "_2sWDi"})
        filename = os.path.dirname(__file__) + "\\" + str(ID) + "-" + str(roundNo) + "-" + str(year) + "-" + race.replace(' ', '-') + ".txt"
        newFile = open(filename, 'w')
        newFile.write("ID\tRoundNo\tYear\tRace\tPos\tNo\tDriver\tNat\tTeam\tLaps\tTime\tGap\tInterval\tKph\tBest\tLap\n")

        #Write to file
        n = 0
        try:
            for i in data:
                if n == 0:
                    newFile.write(str(ID) + "\t" +
                                  str(roundNo) + "\t" +
                                  str(year) + "\t" +
                                  race + "\t")
                    newFile.write(i.text + "\t")
                    n = n + 1
                elif n < 11:
                    datum = i.text
                    if "+" in datum:
                        newFile.write( datum[2:] + "\t")
                    else:
                        newFile.write(datum + "\t")
                    n = n + 1
                else:
                    newFile.write(i.text + "\n")
                    n = 0

            newFile.close()
            print("Done - File Ready")

        except:
            newFile.close()
            if os.path.exists(filename):
                os.remove(filename)
            print("Race does not exist")

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
                print("Error in BatchExtractor")

        print("Loading the", i+1, "season...")
        time.sleep(0)
    return(n)

#Creating the GUI
root = tk.Tk()
root.title("Qualifying Result Generation Utility")
#root.geometry("430x150")
root.resizable(False, False)

frame = tk.Frame(root)
options = {'padx': 5, 'pady': 5}

yearTitle = tk.Label(frame, text = "Year")
yearTitle.grid(column = 1, row = 0, sticky = 'S', **options)
raceTitle = tk.Label(frame, text = "Race")
raceTitle.grid(column = 2, row = 0, sticky = 'S', **options)

singleRace = tk.Label(frame, text = "Single Session")
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
