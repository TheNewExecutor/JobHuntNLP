# JobHuntNLP
A notebook with scripts to scrape Glassdoor job descriptions and analyze them for sector counts, in-demand skills, and keywords.

This project was run using the Anaconda distribution on Windows 10.

## Installation and Setup
1. Install [Python](https://www.python.org/downloads/) and [Anaconda](https://www.anaconda.com/distribution/)

2. Open the Anaconda cmd prompt and look at its path. Move the JobHuntNLP.yml file to there.

3. Create a new environment using the countries.yml file by typing in: 

`conda env create -f JobHuntNLP.yml`

If the JobHuntNLP.yml is not in the right folder, then its full path must be specified:

`conda env create -f C:\folder1\folder2\...\JobHuntNLP.yml`

4. Activate the environment via:

`conda activate JobHuntNLP`

5. Open up Jupyter in that environment by typing in:

`python -m notebook`

## How to Use This Notebook

You will need a valid Glassdoor account for the login.

Sections 1-2 introduce the problems addressed.

Section 3 saves the job links of a given search into a dictionary. If you've obtained this dictionary already, and are not performing a new search, you can simply proceed to Section 4.

Section 4 saves the job data into a CSV file and this can take as long as a few hours depending on the search size. If you've already obtained this file from a search and do not wish to perform another search, you may skip to Section 5.

## Troubleshooting Tips

If an error occurs regarding the **Twisted Reactor** try restarting the notebook kernel.
