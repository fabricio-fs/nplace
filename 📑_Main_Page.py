import pandas as pd
import inflection
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from PIL import Image
#-----------------------------------------
# 0.0 - Functions
#-----------------------------------------

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def country_name(country_id):
    COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
    return COUNTRIES[country_id]

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
    
def color_name(color_code):
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    return COLORS[color_code]

def clean_data (df1):
    #-----------------------------------------
    # 1.1 - Rename Columns
    #-----------------------------------------
    df1 = rename_columns(df1)

    #1.1.1 change columns
    df1['country_code'] = df1['country_code'].apply(lambda x: country_name(x))
    df1 = df1.rename(columns = {'country_code':'country_name'})

    df1['price_range'] = df1['price_range'].apply(lambda x: create_price_type(x))
    df1 = df1.rename(columns = {'price_range':'price_type'})

    df1['rating_color'] = df1['rating_color'].apply(lambda x: color_name(x))

    #-----------------------------------------
    # 1.2 - Clean Na
    #-----------------------------------------
    df1['cuisines'] = df1['cuisines'].fillna('Unspecified')


    #-----------------------------------------
    # 1.3 - Drop Duplicates
    #-----------------------------------------
    df1 = df1.drop_duplicates()


    #-----------------------------------------
    # 1.4 - Business Restrictions
    #-----------------------------------------

    #* 1 - Only one cuisine type considered per restaurant
    df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    return df1


@st.cache_data
def convert_df(df):   
    return df.to_csv().encode('utf-8')


def restaurants_map(df1):
    df_aux = df1[['restaurant_id', 'restaurant_name', 'average_cost_for_two', 'cuisines', 'aggregate_rating', 'latitude', 'longitude', 'rating_color']]
    map_ = folium.Map(location=[30,30], zoom_start=1)
    marker_cluster = MarkerCluster().add_to(map_)
    for index, location_info in df_aux.iterrows(): 
        restaurant_name = df1['restaurant_name'][index]
        price_for_two = '{0:,}'.format(df1['average_cost_for_two'][index])
        cuisine = df1['cuisines'][index]
        rating = df1['aggregate_rating'][index]
        currency = df1['currency'][index]
        html = f"""
        <b>{restaurant_name}</b><br>
        <br>
        <b>Price:</b> {price_for_two} ({currency}) average for two.<br>
        <b>Type:</b> {cuisine}<br>
        <b>Rating:</b> {rating} / 5.0
        """
        iframe=folium.IFrame(html, width=400, height=120)
        folium.Marker([location_info['latitude'],  
                    location_info['longitude']],                
                    popup= folium.Popup(iframe),               
                    icon=folium.Icon(color=location_info['rating_color'], icon='cutlery')).add_to(marker_cluster)
    return folium_static(map_, width=1300, height=600)

#*========================================================================================
#*========================================================================================

df = pd.read_csv('zomato.csv')

# # 1 - DATA CLEANING

df1 = clean_data(df)


#*========================================================================================
#* Streamlit Design
#*========================================================================================

st.set_page_config(layout="wide")
make_map_responsive= """
<style>
    [title~="st.iframe"] { width: 100%}
</style>
"""

st.markdown(make_map_responsive, unsafe_allow_html=True)
##-----------------------------------------
# Streamlit Sidebar
##-----------------------------------------
image = Image.open('orange_logo.png')
#image_path = "/home/fabriciofs/repos/ftc/ftc_project/images/orange_logo.png"          

with st.sidebar:
    cols = st.columns([1,2,3])

    cols[1].image(image, width=100)



    st.sidebar.markdown('## Filters')                 

    filter_label = df1['country_name'].unique().tolist()
    default_label = ['Brazil', 'Canada', 'Australia', 'South Africa', 'New Zeland', 'England']
    countries = st.sidebar.multiselect(
                            'Select countries',
                            filter_label,
                            default= default_label)
    
    # Download data button

    csv = convert_df(df1)

    st.download_button(
        label="Download data",
        data=csv,
        file_name='Nplace.csv',
        mime='text/csv',
    )

#* Countries Filter
df_static = df1.copy()
df1 = df1[df1['country_name'].isin(countries)]

##-----------------------------------------
# Streamlit Main
##-----------------------------------------
with st.container():
    st.header('Welcome to Nplace marketplace Dashboard')
    st.markdown('### Here you will find interactive dashboards with the main information about the marketplace')
    st.markdown('')
    
with st.container():
    # Static metrics
    cols = st.columns(5)   
    with cols[0]:

        st.metric(label='Registered Restaurants', value='{0:,}'.format(len(df_static)).replace(",","."))
        
    with cols[1]:

        st.metric(label='Registered Countries', value=df_static['country_name'].nunique())
        
    with cols[2]:

        st.metric(label="Registered Cities", value=df_static['city'].nunique())
        
    with cols[3]:

        st.metric(label="Total Ratings", value='{0:,}'.format(df_static['votes'].sum()).replace(",","."))
        
    with cols[4]:

        st.metric(label="Cuisine types", value='{0:,}'.format(df_static['cuisines'].nunique()).replace(",","."))


with st.container():
    # Folium Map
    restaurants_map(df1)
    

    

