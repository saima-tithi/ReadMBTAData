"""This program parses data from Boston transportation system
API (https://api-v3.mbta.com/) and shows information about subway routes,
stops corresponding to those routes. Given a source and destination stop, 
it can also shows if there is a route possible between those stops, and 
if a route is possible then prints the ordered list of routes need to be 
taken.
"""

import requests
import argparse

class MBTADataReader:
    """Contains methods for retrieving data from MBTA API and shows the data.
    """

    routeId_list = []
    route_to_stops_dict = {}
    stop_set = set()

    def show_route_names(self):
        """This method makes a HTTP get request to retrieve subway routes data
        and shows the log names of all the subway routes.
        """

        # Here used the filter service of the API to filter route data corresponding
        # to only subway routes. As types of the subway routes are 0 and 1, 
        # 0 and 1 needs to be provided in the HTTP get request.
        resp = requests.get('https://api-v3.mbta.com/routes?filter[type]=0,1')
        
        if resp.status_code != 200:
            # This means something went wrong.
            print("Something went wrong with request GET /routes/. The response "
                + "status code is: %i" % resp.status_code)
            return
        
        server_data = resp.json()
        route_long_names = self.get_route_names(server_data)   
        print("The long names for all the subway routes (route type 0 and 1) are: "
            + str(route_long_names).strip("[]"))

    def get_route_names(self, json_data):
        """Helper method for show_route_names(). This method takes json data for 
        subway routes as input, parses the data, and returns long names of 
        the subway routes. Also saves route id for future use.
        """

        route_long_names = []
        
        for route_info in json_data["data"]:
            self.routeId_list.append(route_info["id"])
            route_long_names.append(route_info["attributes"]["long_name"])
        
        return route_long_names

    def show_stop_info(self):
        """This method loops through the route IDs retrieved in get_route_names()
        method and for each route retrieve the correspong stops. Then it prints 
        the total number of unique stops, the route with most stops, the route 
        with fewest stops, and the name of the stops which are wheelchair accessible.
        """

        resp_list = []
        for routeId in self.routeId_list:
            resp = requests.get('https://api-v3.mbta.com/stops?filter[route]=' + routeId +
            '&include=route')
            if resp.status_code != 200:
                # This means something went wrong.
                print("Something went wrong with request GET /stops/. The response status code is: %i" % resp.status_code)
            else:
                resp_list.append(resp.json())
        
        num_unique_stops = self.get_total_stops(resp_list)
        print("Total number of unique stops is: %i" % num_unique_stops)
        
        min_route, max_route = self.get_route_max_min_stops()
        print("The route with most stops is: %s" % max_route)
        print("The route with fewest stops is: %s" % min_route)

        accessible_stop_set = self.get_accessible_stops(resp_list)
        print("Stops which are wheelchair accessible are: " + str(accessible_stop_set).strip("{}"))

    def get_total_stops(self, resp_list):
        """Helper method for show_stop_info(). This method parses the server 
        responses containg stop information and saves all the unique stop ids. 
        It also creates a dictionary where key is the route id and value is all 
        the stops corresponding to this route.
        """
  
        for resp in resp_list:
            # each response belongs to one route
            # get the route id for this response
            route_key = resp["included"][0]["id"]
            for stop_info in resp["data"]:
                stop_name = stop_info["attributes"]["name"]
                self.stop_set.add(stop_name)
                self.route_to_stops_dict.setdefault(route_key,set()).add(stop_name)
        return len(self.stop_set)
        
    def get_route_max_min_stops(self):
        """Helper method for show_stop_info(). This method loops through the route 
        to stop dictionary. Check the total number of stops corresponding to each 
        route and finds the route with the most stops and the route with fewest 
        stops.
        """

        min = 0
        max = 0
        for route_key in self.route_to_stops_dict.keys():
            stop_count = len(self.route_to_stops_dict[route_key])
            if min == 0:
                min = stop_count
                min_route = route_key
            else:
                if (min > stop_count):
                    min = stop_count
                    min_route = route_key
            if max == 0:
                max = stop_count
                max_route = route_key
            else:
                if (max < stop_count):
                    max = stop_count
                    max_route = route_key
        return min_route, max_route

    def get_accessible_stops(self, resp_list): 
        """Helper method for show_stop_info(). This method parses the server 
        responses containg stop information and saves the stop names which 
        are wheelchair accessible.
        """

        accessible_stop_set = set()     
        for resp in resp_list:
            for stop_info in resp["data"]:
                if (stop_info["attributes"]["wheelchair_boarding"] == 1):
                    stop_name = stop_info["attributes"]["name"]
                    accessible_stop_set.add(stop_name)

        return accessible_stop_set

    def trip_src_to_dest_stop(self, src_stop, dest_stop, banned_stops):
        """This method takes a source stop, a destination stop, and a set of stop 
        names which are closed as inputs and tries to find if traveling from 
        source to destination is possible. If possible, then it prints the 
        ordered list of routes that need to be taken to travel from source to 
        destination.
        """

        needed_route_list = self.find_src_to_dest(src_stop, dest_stop, banned_stops)
        if (not needed_route_list):
            print("No route is possible.")
        else:
            route_num = len(needed_route_list)
            if (route_num == 1):
                print("The route needed is: %s" % needed_route_list[0])
            elif (route_num == 2):
                print("The two routes needed are: %s, then %s" % (needed_route_list[0], needed_route_list[1]))
            else:
                print("The routes needed are: " + str(needed_route_list).strip("[]"))

    def find_src_to_dest(self, src_stop, dest_stop, banned_stops):
        """Helper method for trip_src_to_dest_stop(). This method calculates the 
        routes needed to travel from source to destination. At first it checks if 
        source and destination stops are in the same route, then it returns that 
        route. If not, then it creates a dictionary where key is the route id and 
        value is all the routes which can be traveled from the key route. If two 
        route has any common stop, traveling from one route to another is possible. 
        After creating the dictionary, it tries to find if two routes can be used 
        to travel from source to destination where the first route contains the 
        source stop and the second route contains the destination stop. If it is not 
        possible to use two routes, then it takes each route which contains the 
        source stop and tries to find a path from this route to some other route 
        which contains the destination route.
        """

        needed_route_list = []
        route_with_src = []
        route_with_dest = []
        if (src_stop not in self.stop_set):
            print("The source stop name is invalid.")
            return
        if (dest_stop not in self.stop_set):
            print("The destination stop name is invalid.")
            return

        # check if source and destination are in the same route    
        for route_key in self.route_to_stops_dict:
            stop_set_for_route = self.route_to_stops_dict[route_key]
            stop_set_for_route = stop_set_for_route - banned_stops
            if (src_stop in stop_set_for_route and dest_stop in stop_set_for_route):
                needed_route_list.append(route_key)
                break
            elif (src_stop in stop_set_for_route):
                route_with_src.append(route_key)
            elif (dest_stop in stop_set_for_route):
                route_with_dest.append(route_key)       
                
        if (len(needed_route_list) == 1):
            # source and destination are in the same route, return it
            return needed_route_list
        else:
            # if there is no route with the source stop or there is no route 
            # with the destination stop then return
            if (not route_with_src or not route_with_dest):
                return 
            # create the route to routes dictionary
            route_to_routes_dict = {}
            for route_key1 in self.route_to_stops_dict:
                for route_key2 in self.route_to_stops_dict:
                    if (route_key1 != route_key2):
                        stop_set1 = self.route_to_stops_dict[route_key1]
                        stop_set2 = self.route_to_stops_dict[route_key2]
                        if (len(banned_stops) > 0):
                            stop_set1 = stop_set1-banned_stops
                            stop_set2 = stop_set2-banned_stops
                        if (len(stop_set1.intersection(stop_set2)) > 0):
                            route_to_routes_dict.setdefault(route_key1,set()).add(route_key2)

            # print(route_to_routes_dict)
            # check if there is a path containing two routes
            for route_key_src in route_with_src:
                for route_key_dest in route_with_dest:
                    if (route_key_dest in route_to_routes_dict[route_key_src]):
                        needed_route_list.append(route_key_src)
                        needed_route_list.append(route_key_dest)
                        break
            if (len(needed_route_list) == 2):
                return needed_route_list
            else:
                # there is no path containing two routes, call the recursive method 
                # find_routes with each route containing the source stop
                for route_key_src in route_with_src:
                    if (self.find_routes(route_key_src, route_with_dest, route_to_routes_dict, needed_route_list)):
                        break
                return needed_route_list

    def find_routes(self, route_key_src, route_with_dest, route_to_routes_dict, needed_route_list):
        """Helper recursive method for find_src_to_dest(). Starting from a route 
        with source route, for each route, it appends the route into the result 
        list, and then call this method again with the new route until a route 
        with destination stop is reached.
        """

        for route_key_dest in route_with_dest:
            if (route_key_dest in route_to_routes_dict[route_key_src]):
                needed_route_list.append(route_key_src)
                needed_route_list.append(route_key_dest)
                return True
        for related_route in route_to_routes_dict[route_key_src]:
            needed_route_list.append(route_key_src)
            self.find_routes(related_route, route_with_dest, route_to_routes_dict, needed_route_list)

def main():
    myParser = argparse.ArgumentParser(description=__doc__)
    myParser.add_argument('--stop1', type=str, nargs='?', default="",
        help="the stop name for the source stop, optional input.")
    myParser.add_argument('--stop2', type=str, nargs='?', default="",
        help="the stop name for the destination stop, optional input.")
    myParser.add_argument('--mode', type=str, nargs='?', default="normal",
        help="the default mode is normal, if user specifies the mode as covid19, then some stops will be considered as closed.")

    args = myParser.parse_args()

    my_mbta_data_reader = MBTADataReader()
    my_mbta_data_reader.show_route_names()
    my_mbta_data_reader.show_stop_info()

    banned_stops = set()
    
    if (args.stop1 and args.stop2 and args.mode == "normal"):
        # normal mode where no stop is closed
        my_mbta_data_reader.trip_src_to_dest_stop(args.stop1, args.stop2, banned_stops)   
    elif (args.stop1 and args.stop2 and args.mode == "covid19"):
        # covid19 mode where some stops are closed
        # any stop with a name that includes a word starting with 
        # C, O, V, I, or D is closed.
        banned_chars = ['C', 'O', 'V', 'I', 'D']
        for stop_name in my_mbta_data_reader.stop_set:
            stop_name_words = stop_name.split()
            for word in stop_name_words:
                if (word[0] in banned_chars):
                    banned_stops.add(stop_name)
        my_mbta_data_reader.trip_src_to_dest_stop(args.stop1, args.stop2, banned_stops)

if __name__ == "__main__":
    main()