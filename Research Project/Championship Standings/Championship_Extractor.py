from requests import *
from bs4 import BeautifulSoup
from tkinter import *
import os
import time

def ExtractPage(year, race):
    # CreateURL and access webpage
    url = "https://fiaresultsandstatistics.motorsportstats.com/results/"
    raceURL = url + str(year) + "-" + race.replace(' ', '-').lower() + "/standings"

    resp = get(raceURL)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")  # Success debug message

        # Create data file
        data = soup.find("table", {"class": "_2Q90P"})
        filename = os.path.dirname(__file__) + "\\" + str(year) + "-" + "Championship-Standings" + ".txt"
        newFile = open(filename, 'w')

        newFile.write("Year\tPos\tDriver\tPoints\n")

        n = 0
        try:  # Checks if the user entered a valid Grand Prix and then writes its results onto a text file
            for i in data.findAll("td"):
                if n == 0:
                    newFile.write(str(year) + "\t" + i.text + "\t")
                    n = n + 1
                elif n < 2:
                    newFile.write(i.text + "\t")
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
            print(year, race, "does not exist")

    else:
        print("Code", resp.status_code, "Accessing FIA Website: FAILED")  # Failure debug message

def BatchExtractor():
    startYear = 2020
    endYear = 2019

    n = 0

    for i in range(endYear, startYear + 1):
        baseURL = "https://fiaresultsandstatistics.motorsportstats.com/results/" + str(i) + "-british-grand-prix/classification/"

        resp = get(baseURL)

        if resp.status_code == 200:
            print("Code", resp.status_code, "Accessing FIA Website: SUCCESS")
            soup = BeautifulSoup(resp.text, "html.parser")  # Success debug message

            # Create data file
            data = soup.find_all("a", {"class": "_3AdU8"})
            try:
                    ExtractPage(i, data[-2].text)
                    time.sleep(0)
                    n = n + 1

            except:
                print("Error")

        print("Loading the", i+1, "season...")
        time.sleep(0)
    return(n)

print(BatchExtractor(), "season standings successfully saved")
