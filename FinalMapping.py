from collections import defaultdict
import json
import folium
from matplotlib.ticker import MaxNLocator
from pyproj import crs
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from folium.plugins import HeatMap, MarkerCluster
import time
from folium import CustomIcon, Popup    
from branca.element import Template, MacroElement

def take_input(data_points, date_1, date_2, clusters):
    data_points = data_points
    date_1 = date_1
    date_2 = date_2
    clusters = clusters

    return data_points, date_1, date_2, clusters


def calculate_rows(date_1, date_2, data_points):
    number_years = date_2 - date_1
    number_rows = round((data_points * (23 / number_years)))
    if number_rows > len(pd.read_csv('output_people_more_adjusted_valid.csv')):
        number_rows = len(pd.read_csv('output_people_more_adjusted_valid.csv'))
        print('Maximum data points reached')
    
    return number_rows


def convert_file(filename, number_rows):
    # reads the csv file
    phones_csv = pd.read_csv(filename, nrows=number_rows)
    # uses geopandas to plot the longitude and lattitude values as geometry
    geometry = gpd.points_from_xy(phones_csv['longitude'], phones_csv['latitude'])
    # creates a special geopandas data frame to store the data frm the csv file
    geo_df = gpd.GeoDataFrame(phones_csv, geometry=geometry)
    # converts data fram to json format
    geojson_data = geo_df.to_json()
    # writes the data to a geojson file
    with open('output_phone_more_final.geojson', 'w') as f:
        f.write(geojson_data)
    # loads the geojson file for use in folium map
    with open('output_phone_more_final.geojson') as f:
        map_data = json.load(f)
    
    return map_data


def create_map():
    # Creates map with starting location and zoom and a scale bar
    m = folium.Map(location=[27.9879, 86.925], zoom_start=5, control_scale=True, tiles=folium.TileLayer(no_wrap=True))

    return m


def add_layers(m):
    # Create different marker layers and add them to map
    layer1 = folium.FeatureGroup(name='Apple Markers', show=False).add_to(m)
    layer2 = folium.FeatureGroup(name='Samsung Markers', show=False).add_to(m) 
    layer3 = folium.FeatureGroup(name='Huawei Markers', show=False).add_to(m)  
    layer4 = folium.FeatureGroup(name='Apple positive heat', show=False).add_to(m)
    layer5 = folium.FeatureGroup(name='Apple negative heat', show=False).add_to(m)
    layer6 = folium.FeatureGroup(name='Samsung positive heat', show=False).add_to(m)
    layer7 = folium.FeatureGroup(name='Samsung negative heat', show=False).add_to(m)
    layer8 = folium.FeatureGroup(name='Huawei positive heat', show=False).add_to(m)
    layer9 = folium.FeatureGroup(name='Huawei negative heat', show=False).add_to(m)
    layer10 = folium.FeatureGroup(name='Chloropleth', show=False).add_to(m)  
    layer11 = folium.FeatureGroup(name='All countries heat', show=False).add_to(m)  

    # Add the layer control to the map 
    folium.LayerControl().add_to(m)

    return layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9, layer10, layer11


def add_clusters(m):
    # Create different marker layers but with marker clustering and adds them to map
    layer1 = MarkerCluster(name='Apple Cluster Markers', show=False).add_to(m)
    layer2 = MarkerCluster(name='Samsung Cluster Markers', show=False).add_to(m) 
    layer3 = MarkerCluster(name='Huawei Cluster Markers', show=False).add_to(m)  
    layer4 = folium.FeatureGroup(name='Apple positive heat', show=False).add_to(m)
    layer5 = folium.FeatureGroup(name='Apple negative heat', show=False).add_to(m)
    layer6 = folium.FeatureGroup(name='Samsung positive heat', show=False).add_to(m)
    layer7 = folium.FeatureGroup(name='Samsung negative heat', show=False).add_to(m)
    layer8 = folium.FeatureGroup(name='Huawei positive heat', show=False).add_to(m)
    layer9 = folium.FeatureGroup(name='Huawei negative heat', show=False).add_to(m)
    layer10 = folium.FeatureGroup(name='Chloropleth', show=False).add_to(m)  
    layer11 = folium.FeatureGroup(name='All countries heat', show=False).add_to(m)  

    # Add the layer control to the map 
    folium.LayerControl().add_to(m)

    return layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9, layer10, layer11


def add_to_map(map_data, date_1, date_2, layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9, layer11):
    heat_data_apple_positive = []
    heat_data_apple_negative = []
    heat_data_samsung_positive = []
    heat_data_samsung_negative = []
    heat_data_huawei_positive = []
    heat_data_huawei_negative = []

    total_apple = 0
    total_samsung = 0
    total_huawei = 0
    
    # Add posts to the map as markers, gives markers certain data from the post and sets the colour based on the sentiment of the post
    # Adds markers to different layers based on brand/sentiment
    # accese the psosts from a geojson file called map data which contains all the posts
    for feature in map_data['features']:
        coordinates = feature['geometry']['coordinates']
        properties = [feature['properties']['brand'], feature['properties']['sentiment'], feature['properties']['date'], feature['properties']['country']]

        if properties[1] > 0 and properties[1] <= 0.2:
            color = "red"
        if properties[1] > 0.2 and properties[1] <= 0.4:
            color = 'orange'
        if properties[1] > 0.4 and properties[1] <= 0.6:
            color = 'lightgray'
        if properties[1] > 0.6 and properties[1] <= 0.8:
            color = 'lightgreen'
        if properties[1] > 0.8 and properties[1] <= 1:
            color = 'darkgreen'

        # Define the content of the popup with inline CSS to set the width
        popup_content = f'<div style="width: 125px;"><b>Post Sentiment: </b> {properties[1]}<br><b>Date: </b> {properties[2]}<br><b>Country:</b> {properties[3]}</div>'

        # Create the popup with the styled content
        popup = Popup(popup_content)


        if (int(properties[2]) >= date_1 and int(properties[2]) <= date_2):
            if properties[0] == 'Apple':
                    total_apple += 1
                    folium.Marker(location = [coordinates[0], coordinates[1]],  tooltip=properties[0], popup=popup, icon=folium.Icon(color=color,icon="a", prefix='fa'), max_width=500).add_to(layer1)
                    coordinates
                    if float(properties[1]) >= 0.5:   
                        heat_data_apple_positive.append([coordinates[0], coordinates[1], properties[1]])
                    else:
                        heat_data_apple_negative.append([coordinates[0], coordinates[1], properties[1]])
            elif properties[0] == 'Samsung':
                    total_samsung += 1                   
                    folium.Marker(location = [coordinates[0], coordinates[1]],  tooltip=properties[0], popup=popup, icon=folium.Icon(color=color,icon="s", prefix='fa'), max_width=500).add_to(layer2)
                    if float(properties[1]) >= 0.5:   
                        heat_data_samsung_positive.append([coordinates[0], coordinates[1], properties[1]])
                    else:
                        heat_data_samsung_negative.append([coordinates[0], coordinates[1], properties[1]])
            elif properties[0] == 'Huawei':
                    total_huawei += 1
                    folium.Marker(location = [coordinates[0], coordinates[1]],  tooltip=properties[0], popup=popup, icon=folium.Icon(color=color,icon="h", prefix='fa'), max_width=500).add_to(layer3)
                    if float(properties[1]) >= 0.5:   
                        heat_data_huawei_positive.append([coordinates[0], coordinates[1], properties[1]])
                    else:
                        heat_data_huawei_negative.append([coordinates[0], coordinates[1], properties[1]])
    
    # creates heatmaps for different brands/sentiments of posts

    HeatMap(heat_data_apple_positive, radius=30, blur=20, gradient={0: 'blue', 0.5: 'lime', 1: 'red'}).add_to(layer4)
    HeatMap(heat_data_apple_negative, radius=30, blur=20, gradient={0: 'blue', 0.5: 'lime', 1: 'red'}).add_to(layer5)
    HeatMap(heat_data_samsung_positive, radius=30, blur=20, gradient={0: 'blue', 0.5: 'lime', 1: 'red'}).add_to(layer6)
    HeatMap(heat_data_samsung_negative, radius=30, blur=20, gradient={0: 'blue', 0.5: 'lime', 1: 'red'}).add_to(layer7)
    HeatMap(heat_data_huawei_positive, radius=30, blur=20, gradient={0: 'blue', 0.5: 'lime', 1: 'red'}).add_to(layer8)
    HeatMap(heat_data_huawei_negative, radius=30, blur=20, gradient={0: 'blue', 0.5: 'lime', 1: 'red'}).add_to(layer9) 

    HeatMap(heat_data_apple_positive, radius=30, blur=20, gradient={0: '#004510', 0.5: '#17b31c', 1: '#62ff42'}).add_to(layer11)
    HeatMap(heat_data_samsung_positive, radius=30, blur=20, gradient={0: '#0e005c', 0.5: '#2b3bb3', 1: '#63edff'}).add_to(layer11)
    HeatMap(heat_data_huawei_positive, radius=30, blur=20, gradient={0: '#ff1100', 0.5: '#d46e33', 1: '#fad15f'}).add_to(layer11)

    return total_apple, total_samsung, total_huawei, heat_data_apple_positive, heat_data_apple_negative, heat_data_samsung_positive, heat_data_samsung_negative, heat_data_huawei_positive, heat_data_huawei_negative


# display number of negative vs positive posts for each brand for data on the graph
# def pi_chart_sentiment(total_brand_positve, total_brand_negative, brand):
#     labels = [f'Positive: {len(total_brand_positve)}', f'Negative: {len(total_brand_negative)}']
#     slices = [len(total_brand_positve), len(total_brand_negative)]
#     colours = ['g', 'r']
#     fig, ax = plt.subplots()
#     ax.pie(slices, colors=colours, autopct='%1.1f%%')
#     plt.gca().axes.get_xaxis().set_visible(False)
#     plt.gca().axes.get_yaxis().set_visible(False)
#     plt.title(f'Positive Vs Negative posts for: {brand}')
#     plt.legend(labels, loc='upper left')
#     plt.savefig('static/images/graph2.png')

def pi_chart_sentiment_apple(total_brand_positve, total_brand_negative, brand):
    labels = [f'Positive: {len(total_brand_positve)}', f'Negative: {len(total_brand_negative)}']
    slices = [len(total_brand_positve), len(total_brand_negative)]
    colours = ['g', 'r']
    fig, ax = plt.subplots()
    ax.pie(slices, colors=colours, autopct='%1.1f%%')
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.title(f'Positive Vs Negative posts for: {brand}')
    plt.legend(labels, loc='upper left')
    plt.savefig('static/images/graph4.png')

def pi_chart_sentiment_samsung(total_brand_positve, total_brand_negative, brand):
    labels = [f'Positive: {len(total_brand_positve)}', f'Negative: {len(total_brand_negative)}']
    slices = [len(total_brand_positve), len(total_brand_negative)]
    colours = ['g', 'r']
    fig, ax = plt.subplots()
    ax.pie(slices, colors=colours, autopct='%1.1f%%')
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.title(f'Positive Vs Negative posts for: {brand}')
    plt.legend(labels, loc='upper left')
    plt.savefig('static/images/graph5.png')

def pi_chart_sentiment_huawei(total_brand_positve, total_brand_negative, brand):
    labels = [f'Positive: {len(total_brand_positve)}', f'Negative: {len(total_brand_negative)}']
    slices = [len(total_brand_positve), len(total_brand_negative)]
    colours = ['g', 'r']
    fig, ax = plt.subplots()
    ax.pie(slices, colors=colours, autopct='%1.1f%%')
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.title(f'Positive Vs Negative posts for: {brand}')
    plt.legend(labels, loc='upper left')
    plt.savefig('static/images/graph6.png')

# displays total number of posts per brand
def bar_chart(total_apple, total_samsung, total_huawei):
    brands = ['Apple', 'Samsung', 'Huawei']
    counts = [total_apple, total_samsung, total_huawei]
    bar_colors = ['tab:green', 'tab:blue', 'tab:red']    
    fig, ax = plt.subplots()
    ax.bar(brands, counts, label=brands, color=bar_colors)
    plt.title('Number of posts per brand')
    plt.legend(loc='upper left')
    plt.savefig('static/images/graph3.png')
    #plt.show()
     

# displays top 10 countries with the most posts if true and least posts if false
def number_posts(all_countries, flag):
    countries = []
    post_numbers = []
    countries_posts = {}  # Dictionary to store countries and their total number of posts

    # Iterate through each country's dictionary
    for country, brands_dict in all_countries.items():
        total_posts = 0
        # Iterate through each brand's sentiments list
        for brand_sentiments in brands_dict.values():
            total_posts += len(brand_sentiments) // 2  # Divide by 2 to account for sentiment and date pairs
        countries_posts[country] = total_posts

    # Sort countries by number of posts in descending order
    sorted_countries = sorted(countries_posts.items(), key=lambda x: x[1], reverse=True)

    # if true gives most 10 countries, if flase gives 10 least countries
    if flag:
        for country, posts_count in sorted_countries[:10]:
            countries.append(country)
            post_numbers.append(posts_count)
        fig, ax = plt.subplots()
        plt.title('10 countries with the most posts')
        ax.bar(countries, post_numbers, label=countries)
        plt.legend(loc='upper left')
        plt.savefig('static/images/graph2.png')

    else:
        for country, posts_count in sorted_countries[-10:]:
            countries.append(country)
            post_numbers.append(posts_count)
        fig, ax = plt.subplots()
        plt.title('10 countries with the least posts')
        ax.bar(countries, post_numbers, label=countries)
        plt.legend(loc='upper left')
        plt.savefig('static/images/graph7.png')


  
    #plt.show()
    

def legend(m):
    legend_html = '<div style="position: fixed; bottom: 50px; left: 10px; z-index:9999;">'

    # Read the content of the HTML file containing the legend
    with open('templates/legend.html', 'r') as f:
        legend_content = f.read()
    
    # Append the content of the legend HTML to the legend_html variable
    legend_html += legend_content
    legend_html += '</div>'

    m.get_root().html.add_child(folium.Element(legend_html))


def cholorpleth(map_data, date_1, date_2, layer10):
    # # sturcutre of all countries dictionary containg country as key, value as a dictionary of brands 
    # # brands as keys and and list of sentiments and dates alternating as values in new dict-> Alergia: {Apple: [0.3, 2021, 0.1, 2013], Samsung: [0.2, 2000, 0.7, 2024], Huawei: [0.3, 2019, 0.7, 2012]}
    all_countries = {}

    # # Sets country_geo as the geogson file containg the geographical data for each country needed to create the cholorpleth outlines
    with open('countries.geojson') as handle:
        country_geo = json.loads(handle.read())

    # loops through posts, if the country from the post not in the all countries dict, adds country to dict as key and adds brands for that key
    # Then adds sentiments of post as values for each brand in the country and dates of posts, alternately
    # if country in dict appends sentiment of post to list of all the sentiments for that country for each brand
    for feature in map_data['features']:
        post_date = feature['properties']['date']

        if (int(post_date) >= date_1 and int(post_date) <= date_2):


            country = feature['properties']['country']
            brand = feature['properties']['brand']

            if feature['properties']['country'] not in all_countries:
                all_countries[feature['properties']['country']] = {'Apple': [], 'Samsung': [], 'Huawei': []}
                all_countries[country][brand] = [feature['properties']['sentiment']]
                all_countries[country][brand].append(feature['properties']['date'])

            else:
                all_countries[country][brand].append(feature['properties']['sentiment'])
                all_countries[country][brand].append(feature['properties']['date'])


    # loops through dict of countries and sentiments, for each country finds it geographical data adds it to the map as a polygon and gives the polygon 
    # a colour based on its brand
    for place in all_countries:
        for country in country_geo['features']:
            if country['properties']['ADMIN'] == place:
                current_country = country
                break

        sentiment_date_list_Apple = all_countries[place]['Apple']
        sentiment_date_list_Samsung = all_countries[place]['Samsung']
        sentiment_date_list_Huawei = all_countries[place]['Huawei']

        sentiment_Apple = 0
        sentiment_Samsung = 0
        sentiment_Huawei = 0

        # works out average sentiment for each brand per country
        if len(sentiment_date_list_Apple) > 0:
            sentiment_Apple = round(sum(sentiment_date_list_Apple[0::2]) / (len(sentiment_date_list_Apple)/2), 2)
        if len(sentiment_date_list_Samsung) > 0:        
            sentiment_Samsung = round(sum(sentiment_date_list_Samsung[0::2]) / (len(sentiment_date_list_Samsung)/2), 2)
        if len(sentiment_date_list_Huawei) > 0:       
            sentiment_Huawei = round(sum(sentiment_date_list_Huawei[0::2]) / (len(sentiment_date_list_Huawei)/2), 2)

        # Define the content of the popup with inline CSS to set the width
        popup_content2 = f'<div style="width: 200px;"><b>Country: </b> {place}<br><b>Average Apple sentiment: </b> {sentiment_Apple}<br><b>Average Samsung sentiment: </b> {sentiment_Samsung}<br><b>Average Huawei sentiment: </b> {sentiment_Huawei}</div>'

        # Create the popup with the styled content
        popup2 = Popup(popup_content2)

        # plots each countries shape and sets colour based on brand with most positive sentiment
        if ((sentiment_Apple >= sentiment_Huawei) and (sentiment_Apple >= sentiment_Samsung)):
            folium.GeoJson(current_country, name='countries', style_function=lambda x: {"fillColor": "green"}, popup=popup2).add_to(layer10)

        elif ((sentiment_Samsung >= sentiment_Huawei) and (sentiment_Samsung >= sentiment_Huawei)):
            folium.GeoJson(current_country, name='countries', style_function=lambda x: {"fillColor": "blue"}, popup=popup2).add_to(layer10)

        elif ((sentiment_Huawei >= sentiment_Apple) and (sentiment_Huawei >= sentiment_Samsung)):
            folium.GeoJson(current_country, name='countries', style_function=lambda x: {"fillColor": "red"}, popup=popup2).add_to(layer10)
    
    return all_countries


def trendline(trendline_country, all_countries):
# plots brand sentiment over time for each brand in each country

    if (len(all_countries[trendline_country]['Apple']) > 0):
        x_apple, y_apple = calc_plots(all_countries[trendline_country]['Apple'])
        plt.plot(x_apple, y_apple, 'g-', label='Apple')

    if (len(all_countries[trendline_country]['Samsung']) > 0):
        x_samsung, y_samsung = calc_plots(all_countries[trendline_country]['Samsung'])
        plt.plot(x_samsung, y_samsung, 'b-', label='Samsung')

    if (len(all_countries[trendline_country]['Huawei']) > 0):       
        x_huawei, y_huawei = calc_plots(all_countries[trendline_country]['Huawei'])
        plt.plot(x_huawei, y_huawei, 'r-', label='Huawei')

    # plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(range(2000,2025,2))
    plt.legend(loc='upper left')
    plt.xlabel('Date')
    plt.ylabel('Sentiment')
    plt.title(f'Average sentiment for {trendline_country} per year')
    plt.grid()
    #plt.show()


def calc_plots(data_points):
    # Works out plot line for each brands sentiment over time

    # Separate scores and dates
    scores = data_points[::2]
    dates = data_points[1::2]

    # Pair scores with dates
    score_date_pairs = list(zip(scores, dates))

    # Sort the pairs based on dates
    sorted_pairs = sorted(score_date_pairs, key=lambda x: x[1])

    # creates dictionary out of sorted pairs
    sentiment_per_year = defaultdict(list)

    # loops thorugh sorted pairs, adds each year as a key in a dictionary and all the sentiment to each year 
    for sentiment, year in sorted_pairs:
        sentiment_per_year[year].append(sentiment)
    
    # loops through the dictionary and finds the average of the sentiments for each year
    for year, sentiments in sentiment_per_year.items():
        sentiment_per_year[year] = (sum(sentiments) / len(sentiments))

    # converts the dictionary into list
    sorted_pairs = list(sentiment_per_year.items())

    # Unpack the sorted pairs back into separate lists
    sorted_scores, sorted_dates = zip(*sorted_pairs)

    x1 = sorted_scores
    y1 = sorted_dates

    return x1, y1



def main(data_points, date_1, date_2, clusters):

    data_points, date_1, date_2, clusters = take_input(data_points, date_1, date_2, clusters)

    number_rows = calculate_rows(date_1, date_2, data_points)

    map_data = convert_file('output_people_more_adjusted_valid.csv', number_rows)

    m = create_map()

    if clusters == 'm':
        layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9, layer10, layer11 = add_layers(m)
    elif clusters == 'c':
        layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9, layer10, layer11 = add_clusters(m)

    total_apple, total_samsung, total_huawei, heat_data_apple_positive, heat_data_apple_negative, heat_data_samsung_positive, heat_data_samsung_negative, heat_data_huawei_positive, heat_data_huawei_negative = add_to_map(map_data, date_1, date_2, layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9, layer11)
    legend(m)

    all_countries = cholorpleth(map_data, date_1, date_2, layer10)

    bar_chart(total_apple, total_samsung, total_huawei)
    pi_chart_sentiment_apple(heat_data_apple_positive, heat_data_apple_negative, 'Apple')
    pi_chart_sentiment_samsung(heat_data_samsung_positive, heat_data_samsung_negative, 'Samsung')
    pi_chart_sentiment_huawei(heat_data_huawei_positive, heat_data_huawei_negative, 'Huawei')
    number_posts(all_countries, True)
    # number_posts(all_countries, False)


    m.save('templates/map2.html')


