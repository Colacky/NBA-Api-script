# Small CLI script using NBA Api

### By Sebastian 'Colacky' Kołacki
<br>
<br>
<br>
<br>
<br>

## Contents:
1. Introduction
2. Short description of the project
3. Instructions
<hr>
<br>

### 1. Introduction<br>

Hi, I'm Sebastian and this is my attempt a small CLI script that uses a public api.<br>
It was fun and allowed me to learn a couple new things along the way.<br>

### 2. Short description of the project<br>

Script.py is a script that processes data from an external API.<br>
It's using two other scripts - sqlite.py and validators.py - as their names suggest,<br>
they are handling the database and input validation respectively.<br><hr>


### 3. Instructions<br>

There are 3 commands that script.py accepts:
- grouped-teams
- player-stats
- team-stats

<br>
<br>

**grouped-teams**<br>
doesn't take any additional parameters and prints out all the teams grouped by division<br>
**player-stats**<br>
takes a --name parameter and returns the tallest and heaviest player with first name<br>
or last name matching the --name parameter as well as showing their height and weight<br>
Please note: if you are trying to pass a two-part name ie. Trent Jr., please put it in<br>
quotation marks like so --name 'Trent Jr.'<br>
**team-stats**<br>
takes --season(int) and --output(optional) parameters and returns team stats for each team<br>
for a given season. --output is optional, and by default it will print out the results into<br>
the terminal. There are four available types of output: csv, json, sqlite and stdout(default)<br><hr>

#### **Examples**

- 'python script.py grouped-teams'
- 'python script.py player-stats --name 'Trent Jr.''
- 'python script.py player-stats --name john'
- 'python script.py team-stats --season 2020'
- 'python script.py team-stats --season 2021 --output sqlite'
