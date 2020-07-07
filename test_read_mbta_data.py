"""Tests for read_mbta_data module.
"""

import unittest
import json
import read_mbta_data as main_program

class TestReadMBTAData(unittest.TestCase):
    """Test class for MBTADataReader class.
    """

    def setUp(self):
        """Initialize the json files for route data and stops data.
        """

        self.route_data_file = "test_data/routes_data.json"
        self.stop_data_file1 = "test_data/stop_data_Red.json"
        self.stop_data_file2 = "test_data/stop_data_Mattapan.json"
        self.stop_data_file3 = "test_data/stop_data_Orange.json"
        self.my_data_reader = main_program.MBTADataReader()
    
    def test_route_data(self):
        """Read a json file containing route data and check if get_route_names()
        method is retuning the long names for the subway routes.
        """

        with open(self.route_data_file, "r") as route_file:
            route_data = json.load(route_file)
        route_names = self.my_data_reader.get_route_names(route_data)
        route_names = str(route_names).strip("[]")
        expected_route_names = "'Red Line', 'Mattapan Trolley', 'Orange Line', 'Green Line B', 'Green Line C', 'Green Line D', 'Green Line E', 'Blue Line'"
        self.assertEqual(route_names, expected_route_names)
        print("Testcase passed. Retrieved long names for subway routes.")

    def test_stop_data(self):
        """Read three json files containg stop information about three routes and 
        check if the total number of unique stops, the route with most stops, 
        the route with fewest stops, and the accessbile stops can be returned 
        accurately.
        """

        stop_data_list = []
        with open(self.stop_data_file1, "r") as stop_file1:
            stop_data = json.load(stop_file1)
            stop_data_list.append(stop_data)
        with open(self.stop_data_file2, "r") as stop_file2:
            stop_data = json.load(stop_file2)
            stop_data_list.append(stop_data)
        with open(self.stop_data_file3, "r") as stop_file3:
            stop_data = json.load(stop_file3)
            stop_data_list.append(stop_data)

        num_unique_stops = self.my_data_reader.get_total_stops(stop_data_list)
        self.assertEqual(num_unique_stops, 10)
        
        min_route, max_route = self.my_data_reader.get_route_max_min_stops()
        self.assertEqual(min_route, "Orange")
        self.assertEqual(max_route, "Red")

        accessible_stop_set = self.my_data_reader.get_accessible_stops(stop_data_list)
        self.assertEqual(len(accessible_stop_set), 10)
        print("Testcase passed. Got total unique stops, route with most stops, " +
            "route with fewest stops, and stops which are accessbile")

    def test_find_routes_src_dest(self):
        """Read three json files containg stop information about three routes and checks
        if find_src_to_dest() method is working properly. The test data contains 
        three routes, Red, Mattapan, and Orange. Here is the list of stops associated with each 
        route.
        Red -> {Alewife - Davis - Porter - Harvard - Central}
        Mattapan -> {Central - Kendall/MIT - Charles/MGH - Park Street}
        Orange -> {Park Street - Downtown Crossing - South Station}
        """

        stop_data_list = []
        with open(self.stop_data_file1, "r") as stop_file1:
            stop_data = json.load(stop_file1)
            stop_data_list.append(stop_data)
        with open(self.stop_data_file2, "r") as stop_file2:
            stop_data = json.load(stop_file2)
            stop_data_list.append(stop_data)
        with open(self.stop_data_file3, "r") as stop_file3:
            stop_data = json.load(stop_file3)
            stop_data_list.append(stop_data)

        self.my_data_reader.get_total_stops(stop_data_list)

        banned_stops = set()
        needed_route_list = self.my_data_reader.find_src_to_dest("Alewife", "Central", banned_stops)
        self.assertEqual(needed_route_list[0], "Red")
        print("Testcase passed. From 'Alewife' to 'Central' stop, the needed route "
            + "is Red.")

        needed_route_list = self.my_data_reader.find_src_to_dest("Kendall/MIT", "Downtown Crossing", banned_stops)
        self.assertEqual(needed_route_list[0], "Mattapan")
        self.assertEqual(needed_route_list[1], "Orange")
        print("Testcase passed. From 'Kendall/MIT' to 'Downtown Crossing' stop, "
            + "the needed routes are Mattapan, then Orange.")

        needed_route_list = self.my_data_reader.find_src_to_dest("Alewife", "Downtown Crossing", banned_stops)
        self.assertEqual(needed_route_list[0], "Red")
        self.assertEqual(needed_route_list[1], "Mattapan")
        self.assertEqual(needed_route_list[2], "Orange")
        print("Testcase passed. From 'Alewife' to 'Downtown Crossing' stop, the "
            + "needed routes are Red, then Mattapan, then Orange.")

    def test_find_routes_src_dest_closed_stops(self):
        """Read three json files containg stop information about three routes and checks
        if find_src_to_dest() method is working properly when given a list of closed 
        stops. The test data contains three routes, Red, Mattapan, and Orange. Here is the list of stops associated with each 
        route.
        Red -> {Alewife - Davis - Porter - Harvard - Central}
        Mattapan -> {Central - Kendall/MIT - Charles/MGH - Park Street}
        Orange -> {Park Street - Downtown Crossing - South Station}

        Here the stops Alewife and Central are considered as closed.
        """

        stop_data_list = []
        with open(self.stop_data_file1, "r") as stop_file1:
            stop_data = json.load(stop_file1)
            stop_data_list.append(stop_data)
        with open(self.stop_data_file2, "r") as stop_file2:
            stop_data = json.load(stop_file2)
            stop_data_list.append(stop_data)
        with open(self.stop_data_file3, "r") as stop_file3:
            stop_data = json.load(stop_file3)
            stop_data_list.append(stop_data)

        self.my_data_reader.get_total_stops(stop_data_list)

        banned_stops = set()
        banned_stops.add("Alewife")
        banned_stops.add("Central")

        needed_route_list = self.my_data_reader.find_src_to_dest("Alewife", "Central", banned_stops)
        self.assertFalse(needed_route_list)
        print("Testcase passed. From 'Alewife' to 'Central' stop, no route is "
            + "possible as 'Alewife' and 'Central' are closed.")

        needed_route_list = self.my_data_reader.find_src_to_dest("Davis", "Harvard", banned_stops)
        self.assertEqual(needed_route_list[0], "Red")
        print("Testcase passed. From 'Davis' to 'Harvard' stop, the needed route is "
            + "Red. 'Alewife' and 'Central' are closed.")

        needed_route_list = self.my_data_reader.find_src_to_dest("Kendall/MIT", "Downtown Crossing", banned_stops)
        self.assertEqual(needed_route_list[0], "Mattapan")
        self.assertEqual(needed_route_list[1], "Orange")
        print("Testcase passed. From 'Kendall/MIT' to 'Downtown Crossing' stop, the "
            + "needed routes are Mattapan, then Orange. 'Alewife' and 'Central' are closed.")

        needed_route_list = self.my_data_reader.find_src_to_dest("Alewife", "Downtown Crossing", banned_stops)
        self.assertFalse(needed_route_list)
        print("Testcase passed. From 'Alewife' to 'Downtown Crossing' stop, " +
            "no route is possible as 'Alewife' and 'Central' are closed.")

if __name__ == '__main__':
    unittest.main()