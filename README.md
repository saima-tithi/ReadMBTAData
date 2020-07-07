# ReadMBTAData:
Data Reader for Boston Tranportaion System (MBTA)

# Requirements:
This program is written in Python 3.7, so Python 3 needs to be installed in the user's machine. This program uses `requests` library for HTTP request. It can be installed using the following command:

```pip install requests```

# Input Parameters:
1. --stop1 source_stop: the stop name for the source stop, optional input.
2. --stop2 destination_stop: the stop name for the destination stop, optional input.
3. --mode mode: the default mode is normal, if user specifies the mode as covid19, then some stops will be considered as closed.
4. -h, --help: show the help message and exit.


# Running and Testing the Program:
The program can be run using the following command:

```python read_mbta_data.py```

Here, the program will get subway routes information from the API and will show the long names of the routes. It will also get the stop information corresponding to those routes. Then it will show total number of unique stops, the route with the most stops, the route with the fewest stops, and the stop names which are wheelchair accessible.

If user wants to find routes from a source stop to a destination stop, the program needs two input parameters, `--stop1` which is the source stop and `--stop2` which is the destination stop. Here is the command:

```python read_mbta_data.py --stop1 "Alewife" --stop2 "Central"```

If user wants to find routes from a source stop to a destination stop in covid19 mode, where some stops are closed (stops with a name with any word starting with C, O, V, I, or D will be closed), then `--mode` parameter needs to be set as 'covid19'. Here is the command:

```python read_mbta_data.py --stop1 "Alewife" --stop2 "Central" --mode covid19```

A test script named test_read_mbta_data.py is given with the program. This test script reads from the json files given in test_data folder and checks if the output of the program matches the desired output.

The test script can be run using the following command:

```python -m unittest```