import streamlit as st # v0.69
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
import pydeck as pdk
from pathlib import Path
import pydeck as pdk
import os
import gdown
import geopy
from geopy.distance import geodesic
import joblib
import datetime
import requests
import json
#functions 
def find_postal(add):
    url= "https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=Y&pageNum=1&searchVal="+ add        
    response = requests.get(url)
    try:
        data = json.loads(response.text) 
    except ValueError:
        print('JSONDecodeError')
        pass
    
    return data
    
def find_nearest(house, amenity, radius=2):
    results = {}
    for index,flat in enumerate(house.iloc[:,0]):
        flat_loc = (house.iloc[index,1],house.iloc[index,2])
        flat_amenity = ['','',100,0]
        amenity_2km = pd.DataFrame({'lat':[], 'lon':[]})

        for ind, eachloc in enumerate(amenity.iloc[:,0]):
            amenity_loc = (amenity.iloc[ind,1],amenity.iloc[ind,2])
            distance = geodesic(flat_loc,amenity_loc)
            distance = float(str(distance)[:-3])

            if distance <= radius:
                flat_amenity[3] += 1
                amenity_2km = pd.concat([amenity_2km, pd.DataFrame({'name': [eachloc], 'lat': [amenity_loc[0]], 'lon': [amenity_loc[1]]})], ignore_index=True)

            if distance < flat_amenity[2]:
                flat_amenity[0] = flat
                flat_amenity[1] = eachloc
                flat_amenity[2] = distance

        results[flat] = flat_amenity
    return results, amenity_2km

def dist_from_location(house, location):
    results = {}
    
    for index,flat in enumerate(house.iloc[:,0]):
        flat_loc = (house.iloc[index,1],house.iloc[index,2])
        flat_amenity = ['',100]
        distance = geodesic(flat_loc,location)
        distance = float(str(distance)[:-3])
        flat_amenity[0] = flat
        flat_amenity[1] = distance
        results[flat] = flat_amenity
    return results

#GUI
st.set_page_config(layout="wide")

st.title('HDB Price prediction!')

with st.form('User Input HDB Features'):
    floor_area = st.slider("Floor Area (sqm)", 34, 280, 93)
    
    flat_address = st.text_input("Flat Address or Postal Code", '760296')

    town = st.selectbox('Town', list(['ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH',
                                      'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG', 'CLEMENTI',
                                      'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST',
                                      'KALLANG/WHAMPOA', 'MARINE PARADE', 'QUEENSTOWN', 'SENGKANG',
                                      'SERANGOON', 'TAMPINES', 'TOA PAYOH', 'WOODLANDS', 'YISHUN',
                                      'LIM CHU KANG', 'SEMBAWANG', 'BUKIT PANJANG', 'PASIR RIS', 'PUNGGOL']),
                        index=10)
    flat_model = st.selectbox('Flat Model', list(['Model A', 'Improved', 'Premium Apartment', 'Standard',
                                                  'New Generation', 'Maisonette', 'Apartment', 'Simplified',
                                                  'Model A2', 'DBSS', 'Terrace', 'Adjoined flat', 'Multi Generation',
                                                  '2-room', 'Executive Maisonette', 'Type S1S2']), index=0)
    flat_type = st.selectbox('Flat Type', list(['2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE']), index=2)
    storey = st.selectbox('Storey', list(['01 TO 03', '04 TO 06', '07 TO 09', '10 TO 12', '13 TO 15',
                                          '16 TO 18', '19 TO 21', '22 TO 24', '25 TO 27', '28 TO 30',
                                          '31 TO 33', '34 TO 36', '37 TO 39', '40 TO 42', '43 TO 45',
                                          '46 TO 48', '49 TO 51']), index=3)
    lease_commence_date = st.selectbox('Lease Commencement Date', list(reversed(range(1966, 2017))), index=1)
    submitted1 = st.form_submit_button(label='Submit HDB 🔎')


#model_link = 'https://drive.google.com/uc?id=1wfZUYf0N_LlHtr2kTbTvHaHb0fFwzyhO&export=download'
#explainer_link = 'https://drive.google.com/uc?id=16ZKWI7rH7X8Zq64Ft0OKYsKW_kFewUCa&export=download'
model_link = 'https://drive.google.com/u/0/uc?id=17WuPxfOx2Y0GZTf1tff-3aL_UzF89q8k&export=download' # hosted on GD
explainer_link = 'https://drive.google.com/u/0/uc?id=1SRY7LNPGQRlm7lJcqjdttijemadwyIkk&export=download' # hosted on GD

@st.cache_resource() 
def load_model(model_link, explainer_link):
    if not os.path.exists('model'):
        os.makedirs('model')
    model_path = "model/rf_compressed.pkl"
    explainer_path = "model/shap_explainer.pkl"
    if not os.path.exists(model_path):
        with st.spinner("Downloading model, this may take awhile! \n Please do not close."):
            gdown.download(model_link, model_path)
    if not os.path.exists(explainer_path):
        with st.spinner("Downloading model, this may take awhile! \n Please do not close."):
            gdown.download(explainer_link, explainer_path)
    rfr = joblib.load(model_path)
    explainer = joblib.load(explainer_path)
    return rfr, explainer

rfr, explainer = load_model(model_link, explainer_link)
coord = find_postal(flat_address)
try:
    flat_coord = pd.DataFrame({'address':[coord.get('results')[0].get('ADDRESS')],
                            'LATITUDE':[coord.get('results')[0].get('LATITUDE')], 
                            'LONGITUDE':[coord.get('results')[0].get('LONGITUDE')]})
except IndexError:
    st.error('Invalid address, re-enter a valid address.')
    pass
    
@st.cache_data()
def load_data(filepath):
    return pd.read_csv(filepath)

cpi = load_data('data/cpi_singapore.csv')
cpi['month'] = pd.to_datetime(cpi['month'], format='%Y %b')

supermarket_coord = load_data('data/supermarket_coordinates_clean.csv')
school_coord = load_data('data/school_coordinates_clean.csv')
hawker_coord = load_data('data/hawker_coordinates_clean.csv')
shop_coord = load_data('data/shoppingmall_coordinates_clean.csv')
park_coord = load_data('data/parks_coordinates_clean.csv')
mrt_coord = load_data('data/MRT_coordinates.csv')[['STN_NAME','Latitude','Longitude']]

## Get nearest and number of amenities in 2km radius
# Supermarkets
nearest_supermarket,supermarkets_2km = find_nearest(flat_coord, supermarket_coord)
flat_supermarket = pd.DataFrame.from_dict(nearest_supermarket).T
flat_supermarket = flat_supermarket.rename(columns={0: 'flat', 1: 'supermarket', 2: 'supermarket_dist',
                                                    3: 'num_supermarket_2km'}).reset_index().drop(['index'], axis=1)
supermarkets_2km['type'] = ['Supermarket']*len(supermarkets_2km)

# Primary Schools
nearest_school,schools_2km = find_nearest(flat_coord, school_coord)
flat_school = pd.DataFrame.from_dict(nearest_school).T
flat_school = flat_school.rename(columns={0: 'flat', 1: 'school', 2: 'school_dist',
                                        3: 'num_school_2km'}).reset_index().drop('index', axis=1)
schools_2km['type'] = ['School']*len(schools_2km)

# Hawker Centers
nearest_hawker,hawkers_2km = find_nearest(flat_coord, hawker_coord)
flat_hawker = pd.DataFrame.from_dict(nearest_hawker).T
flat_hawker = flat_hawker.rename(columns={0: 'flat', 1: 'hawker', 2: 'hawker_dist',
                                        3: 'num_hawker_2km'}).reset_index().drop('index', axis=1)
hawkers_2km['type'] = ['Hawker']*len(hawkers_2km)

# Shopping Malls
nearest_mall,malls_2km = find_nearest(flat_coord, shop_coord)
flat_mall = pd.DataFrame.from_dict(nearest_mall).T
flat_mall = flat_mall.rename(columns={0: 'flat', 1: 'mall', 2: 'mall_dist',
                                    3: 'num_mall_2km'}).reset_index().drop('index', axis=1)
malls_2km['type'] = ['Mall']*len(malls_2km)

# Parks
nearest_park,parks_2km = find_nearest(flat_coord, park_coord)
flat_park = pd.DataFrame.from_dict(nearest_park).T
flat_park = flat_park.rename(columns={0: 'flat', 1: 'park', 2: 'park_dist',
                                    3: 'num_park_2km'}).reset_index().drop(['index','park'], axis=1)
parks_2km['type'] = ['Park']*len(parks_2km)
parks_2km['name'] = ['Park']*len(parks_2km)

# MRT
nearest_mrt,mrt_2km = find_nearest(flat_coord, mrt_coord)
flat_mrt = pd.DataFrame.from_dict(nearest_mrt).T
flat_mrt = flat_mrt.rename(columns={0: 'flat', 1: 'mrt', 2: 'mrt_dist',
                                    3: 'num_mrt_2km'}).reset_index().drop('index', axis=1)
mrt_2km['type'] = ['MRT']*len(mrt_2km)

amenities = pd.concat([supermarkets_2km, schools_2km, hawkers_2km, malls_2km, parks_2km, mrt_2km])
amenities = amenities.rename(columns={'lat':'LATITUDE', 'lon':'LONGITUDE'})

# Distance from Dhoby Ghaut
dist_dhoby = dist_from_location(flat_coord, (1.299308, 103.845285))
flat_coord['dist_dhoby'] = [list(dist_dhoby.values())[0][1]]

flat_coord = pd.concat([flat_coord, flat_supermarket.drop(['flat'], axis=1), 
                        flat_school.drop(['flat'], axis=1),
                        flat_hawker.drop(['flat'], axis=1),
                        flat_mall.drop(['flat'], axis=1),
                        flat_park.drop(['flat'], axis=1),
                        flat_mrt.drop(['flat'], axis=1)],
                    axis=1)

# Flat Type
replace_values = {'2 ROOM':0, '3 ROOM':1, '4 ROOM':2, '5 ROOM':3, 'EXECUTIVE':4}
flat_coord['flat_type'] = replace_values.get(flat_type)

# Storey
flat_coord['storey_range'] = list(['01 TO 03','04 TO 06','07 TO 09','10 TO 12','13 TO 15',
                                            '16 TO 18','19 TO 21','22 TO 24','25 TO 27','28 TO 30',
                                            '31 TO 33','34 TO 36','37 TO 39','40 TO 42','43 TO 45',
                                            '46 TO 48','49 TO 51']).index(storey)

# Floor Area
flat_coord['floor_area_sqm'] = floor_area

# Lease commence date
flat_coord['lease_commence_date'] = lease_commence_date

# Region
d_region = {'ANG MO KIO':'North East', 'BEDOK':'East', 'BISHAN':'Central', 'BUKIT BATOK':'West', 'BUKIT MERAH':'Central',
    'BUKIT PANJANG':'West', 'BUKIT TIMAH':'Central', 'CENTRAL AREA':'Central', 'CHOA CHU KANG':'West',
    'CLEMENTI':'West', 'GEYLANG':'Central', 'HOUGANG':'North East', 'JURONG EAST':'West', 'JURONG WEST':'West',
    'KALLANG/WHAMPOA':'Central', 'MARINE PARADE':'Central', 'PASIR RIS':'East', 'PUNGGOL':'North East',
    'QUEENSTOWN':'Central', 'SEMBAWANG':'North', 'SENGKANG':'North East', 'SERANGOON':'North East', 'TAMPINES':'East',
    'TOA PAYOH':'Central', 'WOODLANDS':'North', 'YISHUN':'North'}
region_2 = {'region_East':[0], 'region_North':[0], 'region_North East':[0], 'region_West':[0]}
region = d_region.get(town)
if region == 'East': region_2['region_East'][0] += 1
elif region == 'North': region_2['region_North'][0] += 1
elif region == 'North East': region_2['region_North East'][0] += 1
elif region == 'West': region_2['region_West'][0] += 1

flat_coord = pd.concat([flat_coord, pd.DataFrame.from_dict(region_2)], axis=1)

replace_values = {'Model A':'model_Model A', 'Simplified':'model_Model A', 'Model A2':'model_Model A', 
                'Standard':'Standard', 'Improved':'Standard', '2-room':'Standard',
                'New Generation':'model_New Generation',
                'Apartment':'model_Apartment', 'Premium Apartment':'model_Apartment',
                'Maisonette':'model_Maisonette', 'Executive Maisonette':'model_Maisonette', 
                'Special':'model_Special', 'Terrace':'model_Special', 'Adjoined flat':'model_Special', 
                    'Type S1S2':'model_Special', 'DBSS':'model_Special'}
d = {'model_Apartment':[0], 'model_Maisonette':[0], 'model_Model A':[0], 'model_New Generation':[0], 'model_Special':[0]}
if replace_values.get(flat_model) != 'Standard': d[replace_values.get(flat_model)][0] += 1

df = pd.DataFrame.from_dict(d)
flat_coord = pd.concat([flat_coord, pd.DataFrame.from_dict(d)], axis=1)
flat_coord['selected_flat'] = [1]
flat1 = flat_coord[['flat_type', 'storey_range', 'floor_area_sqm', 'lease_commence_date',
    'school_dist', 'num_school_2km', 'hawker_dist', 'num_hawker_2km',
    'park_dist', 'num_park_2km', 'mall_dist', 'num_mall_2km', 'mrt_dist',
    'num_mrt_2km', 'supermarket_dist', 'num_supermarket_2km', 'dist_dhoby',
    'region_East', 'region_North', 'region_North East', 'region_West',
    'model_Apartment', 'model_Maisonette', 'model_Model A',
    'model_New Generation', 'model_Special']]

flats = pd.read_csv('data/flat_coordinates_clean.csv')[['LATITUDE','LONGITUDE','address']]
flats['selected_flat'] = [0.000001]*len(flats)
flats = pd.concat([flats, flat_coord[['LATITUDE', 'LONGITUDE', 'selected_flat', 'address']]], ignore_index=True)
flats[['LATITUDE', 'LONGITUDE', 'selected_flat']] = flats[['LATITUDE', 'LONGITUDE', 'selected_flat']].astype(float)
flats['type'] = ['HDB']*len(flats)
flats = flats.rename(columns={'address':'name'})
all_buildings = pd.concat([amenities,flats])

predict1 = rfr.predict(flat1)[0]

filtered_df = cpi[cpi['month'].dt.month == datetime.datetime.now().month]
cpi_value = filtered_df['cpi'].values[0]

st.header('Predicted Resale Price is **SGD$%s**.' % ("{:,}".format(int((predict1/100)*cpi_value))))
flat1.to_csv('tmp_csv.csv',index=False)