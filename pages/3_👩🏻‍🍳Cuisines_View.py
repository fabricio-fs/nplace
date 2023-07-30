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

#*=========================================================================================
#*=========================================================================================

df = pd.read_csv('zomato.csv')

# # 1 - DATA CLEANING

df1 = clean_data(df)

# Unique restaurant name
df2 = df1.copy()
df2['restaurant_name_id'] = df2['restaurant_name'] + '-' + df2['restaurant_id'].astype(str)

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
    col1, col2 = st.columns([1,2])
    col1.image(image, width=70)
    col2.markdown('# Nplace')


    st.sidebar.markdown('## Filters')                 
    filter_label = df1['country_name'].unique().tolist()
    default_label = ['Brazil', 'Canada', 'Australia', 'South Africa', 'New Zeland', 'England']
    countries = st.sidebar.multiselect(
                            'Select countries',
                            filter_label,
                            default= default_label)
    
    st.sidebar.markdown('---') 
    
    cuisines_label = df1['cuisines'].unique().tolist()
    default_label = ['Home-made', 'BBQ', 'Brazilian', 'Italian', 'American', 'Japanese', 'Arabian']
    cuisines = st.sidebar.multiselect(
                            'Select cuisine types',
                            cuisines_label,
                            default= default_label)
    st.sidebar.markdown('---') 
    
#* Restaurants slider filter    
    top_restaurants_slider = st.sidebar.slider(
                        'Select how many restaurants to show',
                        value=10,
                        min_value=1,
                        max_value=20
                        )    

#* Countries Filter
df1 = df1[df1['country_name'].isin(countries)]

#* cuisines Filter
df1 = df1[df1['cuisines'].isin(cuisines)]

##-----------------------------------------
# Streamlit Cuisines View
##-----------------------------------------

with st.container():
    st.markdown('# Cuisines View')
    st.markdown('## Top restaurants from the main cuisine types')

with st.container():

    cols = st.columns(5)
    # Best restaurant - Italian
    df_aux = df2[df2['cuisines'] == 'Italian'][['restaurant_id', 'restaurant_name_id', 'aggregate_rating', 'country_name', 'city', 'average_cost_for_two', 'currency']].sort_values(by='aggregate_rating', ascending=False)    
    df_aux = df_aux[df_aux['aggregate_rating'] == df_aux['aggregate_rating'].max()].sort_values(by='restaurant_id')
    rating = df_aux['aggregate_rating'].tolist()[0]
    restaurant = df_aux['restaurant_name_id'].tolist()[0].split('-')[0]
    country = df_aux['country_name'].tolist()[0]    
    city = df_aux['city'].tolist()[0]
    cost = df_aux['average_cost_for_two'].tolist()[0]
    currency = df_aux['currency'].tolist()[0]
    
    cols[0].metric(label=f"Italian: {restaurant}", value=f"{rating} / 5", help=f"Country: {country}  \nCity: {city}  \nCost for two: {cost}({currency})")
    
    # Best restaurant - American
    df_aux = df2[df2['cuisines'] == 'American'][['restaurant_id', 'restaurant_name_id', 'aggregate_rating', 'country_name', 'city', 'average_cost_for_two', 'currency']].sort_values(by='aggregate_rating', ascending=False)    
    df_aux = df_aux[df_aux['aggregate_rating'] == df_aux['aggregate_rating'].max()].sort_values(by='restaurant_id')
    rating = df_aux['aggregate_rating'].tolist()[0]
    restaurant = df_aux['restaurant_name_id'].tolist()[0].split('-')[0]
    country = df_aux['country_name'].tolist()[0]    
    city = df_aux['city'].tolist()[0]
    cost = df_aux['average_cost_for_two'].tolist()[0]    
    currency = df_aux['currency'].tolist()[0]
    
    cols[1].metric(label=f"American: {restaurant}", value=f"{rating} / 5", help=f"Country: {country}  \nCity: {city}  \nCost for two: {cost}({currency})")
    
    # Best restaurant - Arabian
    df_aux = df2[df2['cuisines'] == 'Arabian'][['restaurant_id', 'restaurant_name_id', 'aggregate_rating', 'country_name', 'city', 'average_cost_for_two', 'currency']].sort_values(by='aggregate_rating', ascending=False)    
    df_aux = df_aux[df_aux['aggregate_rating'] == df_aux['aggregate_rating'].max()].sort_values(by='restaurant_id')
    rating = df_aux['aggregate_rating'].tolist()[0]
    restaurant = df_aux['restaurant_name_id'].tolist()[0].split('-')[0]
    country = df_aux['country_name'].tolist()[0]    
    city = df_aux['city'].tolist()[0]
    cost = df_aux['average_cost_for_two'].tolist()[0]   
    currency = df_aux['currency'].tolist()[0]
    
    cols[2].metric(label=f"Arabian: {restaurant}", value=f"{rating} / 5", help=f"Country: {country}  \nCity: {city}  \nCost for two: {cost}({currency})")
    
    # Best restaurant - Japanese
    df_aux = df2[df2['cuisines'] == 'Japanese'][['restaurant_id', 'restaurant_name_id', 'aggregate_rating', 'country_name', 'city', 'average_cost_for_two', 'currency']].sort_values(by='aggregate_rating', ascending=False)    
    df_aux = df_aux[df_aux['aggregate_rating'] == df_aux['aggregate_rating'].max()].sort_values(by='restaurant_id')
    rating = df_aux['aggregate_rating'].tolist()[0]
    restaurant = df_aux['restaurant_name_id'].tolist()[0].split('-')[0]
    country = df_aux['country_name'].tolist()[0]    
    city = df_aux['city'].tolist()[0]
    cost = df_aux['average_cost_for_two'].tolist()[0] 
    currency = df_aux['currency'].tolist()[0]
    
    cols[3].metric(label=f"Japanese: {restaurant}", value=f"{rating} / 5", help=f"Country: {country}  \nCity: {city}  \nCost for two: {cost}({currency})")
    
    # Best restaurant - Home-made
    df_aux = df2[df2['cuisines'] == 'Home-made'][['restaurant_id', 'restaurant_name_id', 'aggregate_rating', 'country_name', 'city', 'average_cost_for_two', 'currency']].sort_values(by='aggregate_rating', ascending=False)    
    df_aux = df_aux[df_aux['aggregate_rating'] == df_aux['aggregate_rating'].max()].sort_values(by='restaurant_id')
    rating = df_aux['aggregate_rating'].tolist()[0]
    restaurant = df_aux['restaurant_name_id'].tolist()[0].split('-')[0]
    country = df_aux['country_name'].tolist()[0]    
    city = df_aux['city'].tolist()[0]
    cost = df_aux['average_cost_for_two'].tolist()[0]
    currency = df_aux['currency'].tolist()[0]
        
    cols[4].metric(label=f"Home-made: {restaurant}", value=f"{rating} / 5", help=f"Country: {country}  \nCity: {city}  \nCost for two: {cost}({currency})")

with st.container():
    cols = st.columns(2)
    
    with cols[0]:
        # Cuisines best rating
        df_aux = df2[['cuisines', 'aggregate_rating']].groupby('cuisines').mean().sort_values('aggregate_rating', ascending=False).reset_index().head(top_restaurants_slider)
        fig = px.bar(df_aux, x='cuisines', y='aggregate_rating',text_auto=True, title=f'Top {top_restaurants_slider} best cuisine type', labels={'cuisines': 'Cuisines', 'aggregate_rating':'Mean rating'}) 
        st.plotly_chart(fig, use_container_width=True)
        
    with cols[1]:
        # Cuisines worst rating
        df_aux = df2[df2['rating_text'] != 'Not rated']
        df_aux = df_aux[['cuisines', 'aggregate_rating']].groupby('cuisines').mean().sort_values('aggregate_rating').reset_index().head(top_restaurants_slider)
        fig = px.bar(df_aux, x='cuisines', y='aggregate_rating',text_auto=True, title=f'Top {top_restaurants_slider} worst cuisine type', labels={'cuisines': 'Cuisines', 'aggregate_rating':'Mean rating'}) 
        st.plotly_chart(fig, use_container_width=True)
        
with st.container():
    cols = st.columns(2)

    with cols[0]:
        st.markdown(f'### Top {top_restaurants_slider} best restaurants')
        #Top restaurants per cuisine
        df_aux = df1[['restaurant_id', 'restaurant_name', 'country_name', 'cuisines', 'aggregate_rating', 'votes']].sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True]).head(top_restaurants_slider)
        st.dataframe(df_aux, hide_index=True)
    with cols[1]:
        st.markdown(f'### Top {top_restaurants_slider} worst restaurants')
        #Top worst restaurants per cuisine
        df_aux = df1[df1['rating_text'] != 'Not rated']
        df_aux = df_aux[['restaurant_id', 'restaurant_name', 'country_name', 'cuisines', 'aggregate_rating', 'votes']].sort_values(['aggregate_rating', 'restaurant_id'], ascending=[True, True]).head(top_restaurants_slider)
        st.dataframe(df_aux, hide_index=True)