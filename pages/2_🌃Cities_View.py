import pandas as pd
import inflection
import plotly.express as px
import streamlit as st
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

#*===================================================================================
#*===================================================================================

df = pd.read_csv('zomato.csv')

# # 1 - DATA CLEANING

df1 = clean_data(df)

#*========================================================================================
#* Streamlit Design
#*========================================================================================

st.set_page_config(layout="wide")
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
    
    st.sidebar.markdown('---')                 

#* Cities slider Filter
    top_cities_slider = st.sidebar.slider(
                        'Select how many cities to show',
                        value=10,
                        min_value=1,
                        max_value=20
                        )    


#* Countries Filter
df1 = df1[df1['country_name'].isin(countries)]


##-----------------------------------------
# Streamlit Cities View
##-----------------------------------------
with st.container():
    st.markdown('# Cities View')
    # Cities with the largest number of restaurants registered
    df_aux = df1[['city', 'restaurant_id', 'country_name']].groupby(['city', 'country_name']).nunique().sort_values('restaurant_id', ascending=False).reset_index().head(top_cities_slider)
    fig = px.bar(df_aux, x='city', y='restaurant_id',text_auto=True, title= f'Top {top_cities_slider} cities with largest number of restaurants registered', color = 'country_name', labels={'city': 'Cities', 'restaurant_id':'Restaurants', 'country_name': 'Countries'}) 
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    cols = st.columns(2)
    
    with cols[0]:
        # City with the largest number of restaurants with mean rating above 4 
        df_aux = df1[df1['votes'] != 0]
        df_aux = df_aux[df_aux['aggregate_rating'] >= 4][['city', 'restaurant_id', 'country_name']]
        df_aux = df_aux[['city', 'restaurant_id', 'country_name']].groupby(['city', 'country_name']).nunique().sort_values('restaurant_id', ascending=False).reset_index().head(top_cities_slider)
        fig = px.bar(df_aux, x='city', y='restaurant_id',text_auto=True, title= f'Top {top_cities_slider} cities with the largest number of restaurants with mean rating above 4', color = 'country_name', labels={'city': 'Cities', 'restaurant_id':'Restaurants', 'country_name':'Countries'}) 
        st.plotly_chart(fig, use_container_width=True)
    
    with cols[1]:
        df_aux = df1[df1['votes'] != 0]
        df_aux = df_aux[df_aux['aggregate_rating'] <= 2.5][['city', 'restaurant_id', 'country_name']]
        df_aux = df_aux[['city', 'restaurant_id', 'country_name']].groupby(['city', 'country_name']).nunique().sort_values('restaurant_id', ascending=False).reset_index().head(top_cities_slider)
        fig = px.bar(df_aux, x='city', y='restaurant_id',text_auto=True, title= f'Top {top_cities_slider} cities with the largest number of restaurants with mean rating below 2.5', color = 'country_name', labels={'city': 'Cities', 'restaurant_id':'Restaurants', 'country_name':'Countries'}) 
        st.plotly_chart(fig, use_container_width=True)
with st.container():
    # City that has the largest number of distinct cuisines
    df_aux = df1[['city', 'cuisines', 'country_name']].groupby(['city', 'country_name']).nunique().sort_values('cuisines', ascending=False).reset_index().head(top_cities_slider)
    fig = px.bar(df_aux, x='city', y='cuisines',text_auto=True, title= f'Top {top_cities_slider} cities with largest number of distinct cuisines', color = 'country_name', labels={'city': 'Cities', 'cuisines':'Cuisines', 'country_name':'Countries'}) 
    st.plotly_chart(fig, use_container_width=True)
