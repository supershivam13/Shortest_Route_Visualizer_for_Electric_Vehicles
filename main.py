# Importing required modules


import streamlit as st
from streamlit_folium import folium_static
import folium as f,folium
import osmnx as ox
import networkx as nx
import geopy
import geopandas
import requests
import json
import geopandas as gpd
import numpy as np
import random
import matplotlib.pyplot as plt


#************************  MAIN WEB-APPLICATION STARTS HERE   ***********************************************#

# Main application starts

# Display image at top
st.image('./map.jpg')

# Display the Title and header of the application
st.title("Shortest Route for Electric Vehicles")
st.header('Using Python OSMNX and Folium Library')
st.write(' ')

# First Selectbox to select the input method by the users
input_method = st.sidebar.selectbox("Select the Input method",("Place Name", "Coordinates","Waiting Time"))

# Second Selectbox to select the network type of the graph by the users
network_value = st.sidebar.selectbox("Select the Network type",("Walk","Drive","Bike","All"))

# Changing the network_value to the suitable format according to the selection by the user
if network_value=='Walk':
    network_value='walk'
elif network_value=='Drive':
    network_value='drive'
elif network_value=='Bike':
    network_value='bike'
else:
    network_value='all'
    
# Third Selectbox to select the algorithm to be used for the calculation of shortest_path
algo_type = st.sidebar.selectbox("Select the Algorithm type",("Dijkstra’s Algorithm","Bellman-Ford Algorithm"))

# Changing the algo_type to the suitable format according to the selection by the user
if algo_type=='Dijkstra’s Algorithm':
    algo_value='dijkstra'
else:
    algo_value='bellman-ford'

# Initialising four variables input1,input2,input3,input4 to store the value of the coordinates(lattitude,longitude)
# of source and destination respectively.
input1 = 0.0000   # source's lattitude
input2 = 0.0000   # source's longitude
input3 = 0.0000   # destination's lattitude
input4 = 0.0000   # destination's longitude

colors  = ['blue', 'orange', 'green','yellow','purple']

# if the user selected the input_method as coordinates
if input_method=='Coordinates':

    # Display text
    st.write("""
    Enter the coordinate of the Source
    """)

    # Activated two columns for input of lattitude and longitude of source
    col1, col2 = st.beta_columns(2)
    with col1:
        input1 = st.number_input('Source Lattitude Coordinates')
    with col2:
        input2 = st.number_input('Source Longitude Coordinates')

    # Display the stored values of input by the user to double-check the given inputs
    st.write("Lattitude:",input1,"Longitude:", input2)

    # Display text
    st.write("""
    Enter the coordinate of the Destination
    """)

    # Activated two columns for input of lattitude and longitude of destination
    col1, col2 = st.beta_columns(2)
    with col1:
        input3 = st.number_input('Destination Lattitude Coordinates')
    with col2:
        input4 = st.number_input('Destination Longitude Coordinates')

    # Display the stored values of input by the user to double-check the given inputs
    st.write("Lattitude:",input3,"Longitude:", input4)

    # A Radio button with three options to select the map_type by the user 
    map_type = st.radio(
    'Select map type',
    ['OpenStreetMap', 'CartodbPositron','StamenTerrain']
    )

    # Slider to take the value of k from the user to plot k shortest routes
    k = st.select_slider('Select number of shortest paths', options=[1,'2','3','4','5'])
    k_paths=int(k)

    # Slider to select the distance range between source and destination by the user ( in Kms )
    range = st.select_slider('Select distance range ( in Km )', options=[10,'20','30','40','50','60','70','80','90','100'])

    # Converting the selection of the user in integer from string, and changing it into metres
    range_value=int(range)
    range_value*=1000

    # Display the input in metres to double-check the given inputs
    st.write("Distance range in metres:",range_value)

    # When the button is clicked, it will return a true boolean value 
    # which makes the inside code of if statement to execute
    if st.button('Show me the Way'):

        # try and except blocks to handle the errors during the process of generation of maps with shortest routes
        try:
            # Configure OSMnx by setting the default global settings’ values
            ox.config(use_cache=True, log_console=True)

            # Creating a graph from OSMNX within some distance of source point
            G = ox.graph_from_point((input1, input2),dist=range_value,network_type=network_value,simplify=False)
            
            # adding edge speeds for all the nodes present in the graph G
            G = ox.speed.add_edge_speeds(G)

            # adding edge travel times for all the nodes present in the graph G
            G = ox.speed.add_edge_travel_times(G)

            # getting the nearest node from the source coordinates in the graph G generated above
            orig = ox.get_nearest_node(G, (input1, input2))

            # getting the nearest node from the destination coordinates in the graph G generated above
            dest = ox.get_nearest_node(G, (input3, input4))
            

            # shortest_path() function generates the shortest path between the orgin and source
            # and store the path in a 'route' named variable according to the algorithm
            # selected by the user and all computations are based on travel time
            route = nx.shortest_path(G, orig, dest, 'travel_time',method=algo_value)
            
            # Plotting the shortest route on the folium map named 'route_map' and coloring it red
            route_map = ox.plot_route_folium(G, route,route_color='red',tiles=map_type,weight=5)

            # Now, generating k number of shortest_path
            k_paths = k_paths - 1
            routes = ox.k_shortest_paths(G, orig, dest, k=k_paths, weight='length')
                
            # Plotting the other shortest_routes other than the main shortest route
            ind = 0
            for x in routes:
                if (x!=route):
                    route_map = ox.plot_route_folium(G, x,route_color=colors[ind],route_map=route_map,tiles=map_type,weight=2)
                    ind = ind + 1

            # Putting a blue folium Marker on the source coordinates with proper tooltip
            tooltip1 = "Source"
            folium.Marker(
            [input1, input2], popup="Source", tooltip=tooltip1,icon=folium.Icon(color='blue')).add_to(route_map)

            # Putting a red folium Marker on the destination coordinates with proper tooltip
            tooltip2 = "Destination"
            folium.Marker(
            [input3, input4], popup="Destination", tooltip=tooltip2,icon=folium.Icon(color='red')).add_to(route_map)

            # Displaying the final map with shortest_path plotted and markers placed on the correct locations
            folium_static(route_map)
            st.write("The shortest among all k paths is indicated by red color.")
        
        # if some error occurs during the generation of maps, then this except block will execute
        except:

            # Displaying the error message with some suggestions
            st.image('./error.png')
            st.error('Sorry ! No Graph exists for the given inputs.')
            st.text("Please try again with some other input values.")
            
        
# if the user selected the input_method as Place name
elif input_method=='Place Name':

    # Display text
    st.write("""
    Enter the name of the Source
    """)

    # take source as input
    place1 = st.text_input('Source')

    # Replacing the blankspaces in the source input string with '+' character 
    # to make it properly formatted to make API call using Google Geocoding API
    place1=place1.replace(" ","+")
    st.write('')

    # Display text
    st.write("""
    Enter the name of the Destination
    """)

    # take destination as input
    place2 = st.text_input('Destination')

    # # Replacing the blankspaces in the destination input string with '+' character 
    # to make it properly formatted to make API call using Google Geocoding API
    place2=place2.replace(" ","+")

    # A Radio button with three options to select the map_type by the user
    map_type = st.radio(
    'Select map type',
    ['OpenStreetMap', 'CartodbPositron','StamenTerrain']
    )

    # Slider to take the value of k from the user to plot k shortest routes
    k = st.select_slider('Select number of shortest paths', options=[1,'2','3','4','5'])
    k_paths=int(k)

    # Slider to select the distance range between source and destination by the user ( in Kms )
    range = st.select_slider('Select distance range ( in Km )', options=[10,'20','30','40','50','60','70','80','90','100'])

    # Converting the selection of the user in integer from string, and changing it into metres
    range_value=int(range)
    range_value*=1000

    # Display the input in metres to double-check the given inputs
    st.write("Distance range in metres:",range_value) 

    # When the button is clicked, it will return a true boolean value 
    # which makes the inside code of if statement to execute
    if st.button('Show me the Way'):

        # try and except blocks to handle the errors during the API calls and data retreival from Google Geocoding API.
        try:
            # url variable store urL ( to make use of Google Geocoding API later )
            url = 'https://maps.googleapis.com/maps/api/geocode/json?'

            # enter your api key here ( already generated one from Google Cloud Platform )
            api_key='AIzaSyCzxwd5wNZIL1PSFciGmZdlzK5o4h_0al8'

            # get method of requests module returns response object
            # API Call to get the response json for the source
            res_ob1 = requests.get(url+'address='+place1+'&key='+api_key)

            # json method of response object converts json format data into python format data
            results1 = res_ob1.json()['results']
            my_geo1 = results1[0]['geometry']['location']

            # Display the proper name of the Source according to the response received from the API call
            source_name_full = results1[0]['formatted_address']
            st.write("Source: ",source_name_full)

            # Display the retrieved lattitude and longitude of source from the API call
            st.write("Latitude:",my_geo1['lat'],"\n","Longitude:",my_geo1['lng'])
            input1 = my_geo1['lat']
            input2 = my_geo1['lng']


            # get method of requests module returns response object
            # API Call to get the response json for the destination
            res_ob2 = requests.get(url+'address='+place2+'&key='+api_key)

            # json method of response object converts json format data into python format data
            results2 = res_ob2.json()['results']
            my_geo2 = results2[0]['geometry']['location']

            # Display the proper name of the Destination according to the response received from the API call
            dest_name_full= results2[0]['formatted_address']
            st.write("Destination: ",dest_name_full)

            # Display the retrieved lattitude and longitude of destination from the API call
            st.write("Latitude:",my_geo2['lat'],"\n","Longitude:",my_geo2['lng'])
            input3 = my_geo2['lat']
            input4 = my_geo2['lng']

            # try and except blocks to handle the errors during the process of generation of maps with shortest routes
            try:
                # Configure OSMnx by setting the default global settings values
                ox.config(use_cache=True, log_console=True)

                # Creating a graph from OSMNX within some distance of source point
                G = ox.graph_from_point((input1, input2),dist=range_value,network_type=network_value,simplify=False)
                # ox.plot_graph(G,node_color='r')

                # # adding edge speeds for all the nodes present in the graph G
                G = ox.speed.add_edge_speeds(G)

                # # adding edge travel times for all the nodes present in the graph G
                G = ox.speed.add_edge_travel_times(G)

                # getting the nearest node from the source coordinates in the graph G generated above
                orig = ox.get_nearest_node(G, (input1, input2))

                # getting the nearest node from the destination coordinates in the graph G generated above
                dest = ox.get_nearest_node(G, (input3, input4))

                # shortest_path() function generates the shortest path between the orgin and source
                # and store the path in a 'route' named variable according to the algorithm
                # selected by the user and all computations are based on travel time
                route = nx.shortest_path(G, orig, dest, 'travel_time',method=algo_value)

                # Plotting the shortest route on the folium map named 'route_map' and coloring it red
                route_map = ox.plot_route_folium(G, route,route_color='red',tiles=map_type,weight=5)

                # Now, generating k number of shortest_path
                k_paths = k_paths - 1
                routes = ox.k_shortest_paths(G, orig, dest, k=k_paths, weight='length')
                
                # Plotting the other shortest_routes other than the main shortest route
                ind = 0
                for x in routes:
                    if (x!=route):
                        route_map = ox.plot_route_folium(G, x,route_color=colors[ind],route_map=route_map,tiles=map_type,weight=2)
                        ind = ind + 1

                # Putting a blue folium Marker on the source coordinates with proper tooltip
                tooltip1 = "Source"
                folium.Marker(
                [input1, input2], popup="Source", tooltip=tooltip1,icon=folium.Icon(color='blue')).add_to(route_map)

                # Putting a red folium Marker on the destinaton coordinates with proper tooltip
                tooltip2 = "Destination"
                folium.Marker(
                [input3, input4], popup="Destination", tooltip=tooltip2,icon=folium.Icon(color='red')).add_to(route_map)

                # Displaying the final map with shortest_path plotted and markers placed on the correct locations
                folium_static(route_map)
                st.write("The shortest among all k paths is indicated by red color.")

            # if some error occurs during the generation of maps, then this except block will execute 
            except:
                
                # Displaying the error message with some suggestions
                st.image('./error.png')
                st.error('Sorry ! No Graph exists for the given inputs.')
                st.text("Please try again with some other input values.")

        # if some error occurs in making API calls, then this except block will execute
        except:

            # Displaying the error message and possible reasons
            st.error("Error ! Could not fetch the coordinates of the given inputs.")
            st.write("""
            Possible Reasons:\n
            1) API Key is invalid or not active.\n 
            2) Input is invalid.
            """)


else:

    # Display text
    st.write("""
    Enter the name of the Source
    """)

    # take source as input
    place1 = st.text_input('Source')

    # Replacing the blankspaces in the source input string with '+' character 
    # to make it properly formatted to make API call using Google Geocoding API
    place1=place1.replace(" ","+")
    st.write('')

    # Display text
    st.write("""
    Enter the name of the Destination
    """)

    # take destination as input
    place2 = st.text_input('Destination')

    # # Replacing the blankspaces in the destination input string with '+' character 
    # to make it properly formatted to make API call using Google Geocoding API
    place2=place2.replace(" ","+")

    # A Radio button with three options to select the map_type by the user
    map_type = st.radio(
    'Select map type',
    ['OpenStreetMap', 'CartodbPositron','StamenTerrain']
    )

    # Slider to take the value of k from the user to plot k shortest routes
    k = st.select_slider('Select number of shortest paths', options=[1,'2','3','4','5'])
    k_paths=int(k)

    # Slider to select the distance range between source and destination by the user ( in Kms )
    range = st.select_slider('Select distance range ( in Km )', options=[10,'20','30','40','50','60','70','80','90','100'])

    # Converting the selection of the user in integer from string, and changing it into metres
    range_value=int(range)
    range_value*=1000

    # Display the input in metres to double-check the given inputs
    st.write("Distance range in metres:",range_value) 

    # When the button is clicked, it will return a true boolean value 
    # which makes the inside code of if statement to execute
    if st.button('Show me the Way'):

        # try and except blocks to handle the errors during the API calls and data retreival from Google Geocoding API.
        try:
            # url variable store urL ( to make use of Google Geocoding API later )
            url = 'https://maps.googleapis.com/maps/api/geocode/json?'

            # enter your api key here ( already generated one from Google Cloud Platform )
            api_key='AIzaSyC3S0N05MSKjXr9PgN5_YSFX2WTHjSiA1w'

            # get method of requests module returns response object
            # API Call to get the response json for the source
            res_ob1 = requests.get(url+'address='+place1+'&key='+api_key)

            # json method of response object converts json format data into python format data
            results1 = res_ob1.json()['results']
            my_geo1 = results1[0]['geometry']['location']

            # Display the proper name of the Source according to the response received from the API call
            source_name_full = results1[0]['formatted_address']
            st.write("Source: ",source_name_full)

            # Display the retrieved lattitude and longitude of source from the API call
            st.write("Latitude:",my_geo1['lat'],"\n","Longitude:",my_geo1['lng'])
            input1 = my_geo1['lat']
            input2 = my_geo1['lng']


            # get method of requests module returns response object
            # API Call to get the response json for the destination
            res_ob2 = requests.get(url+'address='+place2+'&key='+api_key)

            # json method of response object converts json format data into python format data
            results2 = res_ob2.json()['results']
            my_geo2 = results2[0]['geometry']['location']

            # Display the proper name of the Destination according to the response received from the API call
            dest_name_full= results2[0]['formatted_address']
            st.write("Destination: ",dest_name_full)

            # Display the retrieved lattitude and longitude of destination from the API call
            st.write("Latitude:",my_geo2['lat'],"\n","Longitude:",my_geo2['lng'])
            input3 = my_geo2['lat']
            input4 = my_geo2['lng']

            try:
                # Configure OSMnx by setting the default global settings values
                ox.config(use_cache=True, log_console=True)

                # Creating a graph from OSMNX within some distance of source point
                G = ox.graph_from_point((input1, input2),dist=range_value,network_type=network_value,simplify=False)
                # ox.plot_graph(G,node_color='r')

                # # adding edge speeds for all the nodes present in the graph G
                G = ox.speed.add_edge_speeds(G)

                # # adding edge travel times for all the nodes present in the graph G
                G = ox.speed.add_edge_travel_times(G)

                # getting the nearest node from the source coordinates in the graph G generated above
                orig = ox.get_nearest_node(G, (input1, input2))

                # getting the nearest node from the destination coordinates in the graph G generated above
                dest = ox.get_nearest_node(G, (input3, input4))

                # shortest_path() function generates the shortest path between the orgin and source
                # and store the path in a 'route' named variable according to the algorithm
                # selected by the user and all computations are based on travel time
                routes = ox.k_shortest_paths(G, orig, dest, k=k_paths, weight='length')
                
                # a list of potential charging points considered
                node_points=[]


                # Extracting all the node points
                for r in routes: 
                    for a in r:
                        node_points.append(a)
                    
                # removing the duplicates nodes from all k shortest routes
                node_points=list(set(node_points))

                node_points2 = []
                
                # taking 50% of the node points to be charging stations only
                node_points2=(np.random.permutation(node_points).tolist())[0:int(len(node_points)*0.3)]

                # generating the random waiting time to the charging stations
                node_waiting_times = np.random.permutation( np.arange(len(node_points))).tolist()

                # making a dictionary to assign the node with random waiting time
                time_charge=dict(zip(node_points,node_waiting_times))

                # 0 waiting time means those node are not charging stations
                for c in node_points2:
                    time_charge[c]=0


                # a variable having a very high value
                min=1000000

                sum=0

                # a list to store the final shortest route based on waiting time
                shortest_route=[]

                # Now, generating k number of shortest_path
                routes = ox.k_shortest_paths(G, orig, dest, k=k_paths, weight='length')

                for z in routes:
                    for b in z:
                        sum=sum+time_charge[b]
                    
                    if(sum<min):
                        shortest_route=z
                        min=sum
                    
                    sum=0
                
                # Plotting the shortest route on the folium map named 'route_map' and coloring it red
                route_map = ox.plot_route_folium(G, shortest_route,route_color='red',tiles=map_type,weight=3)

                # Putting a blue folium Marker on the source coordinates with proper tooltip
                tooltip1 = "Source"
                folium.Marker(
                [input1, input2], popup="Source", tooltip=tooltip1,icon=folium.Icon(color='blue')).add_to(route_map)

                # Putting a red folium Marker on the destinaton coordinates with proper tooltip
                tooltip2 = "Destination"
                folium.Marker(
                [input3, input4], popup="Destination", tooltip=tooltip2,icon=folium.Icon(color='red')).add_to(route_map)

                # Displaying the final map with shortest_path plotted and markers placed on the correct locations
                folium_static(route_map)



                


            # if some error occurs during the generation of maps, then this except block will execute 
            except:
                
                # Displaying the error message with some suggestions
                st.image('./error.png')
                st.error('Sorry ! No Graph exists for the given inputs.')
                st.text("Please try again with some other input values.")

        # if some error occurs in making API calls, then this except block will execute
        except:

            # Displaying the error message and possible reasons
            st.error("Error ! Could not fetch the coordinates of the given inputs.")
            st.write("""
            Possible Reasons:\n
            1) API Key is invalid or not active.\n 
            2) Input is invalid.
            """)





#***************************************** WEB-APPLICATION ENDS HERE  ************************************#

   
