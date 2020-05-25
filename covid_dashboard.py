import pandas as pd
import streamlit as st
import pydeck as pdk

st.title('Covid-19 mini-dashboard')
st.write('## Country timeline')

st.sidebar.markdown("### view datasheet?")
checkbox_rawdata = st.sidebar.checkbox('show raw data')
checkbox_data = st.sidebar.checkbox('show aggregated data')



@st.cache()
def load_all(filepath_dict):
    df_list = []
    for k,v in filepath_dict.items():
        df_list.append(pd.read_csv(v))
        df_list[-1]['id'] = k
    df = pd.concat(df_list)
    df = df.melt(id_vars=list(df.columns[:4])+['id'],
                 var_name='date',
                 value_name='cnt')
    df.rename(columns=dict(Lat='lat',Long='lon'),
              inplace=True)
    df['date'] = pd.to_datetime(df.date)
    return df

fpath_dict = dict(
    deaths=r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
    comfirmed=r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
    recovered=r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

st.sidebar.markdown('### select dataset: ')
df = load_all(fpath_dict)
name = st.sidebar.selectbox(
    "Choose dataset", list(fpath_dict.keys()), 0
)


if checkbox_rawdata:
    "### raw data"
    st.write(df)


data_area = df.groupby(['Country/Region','id','date']).cnt.agg('sum')
cumul = st.checkbox('cumulate data up to now.', True)


if checkbox_data:
    "### aggregated data"
    st.write(data_area)

country_list = list(data_area.index.levels[0].astype(str))
countries = st.multiselect(
    "Choose countries", country_list, ["Netherlands", "Belgium"]
)

data_areaplot = data_area.loc[countries, name , :].droplevel(1).unstack(level=0)

if not cumul:
    data_areaplot = data_areaplot.diff()

data_areaplot.columns.name = None
st.area_chart(data_areaplot)
# st.area_chart(data_areaplot.sort_values(by='cnt', axis=1, ascending=False))

datestrs = list(data_area.index.levels[-1].astype(str))
date_idx = st.slider('Select date in range '+ str(datestrs[0]) + ' - ' + str(datestrs[-1]),0,len(datestrs)-1)
datestr = datestrs[date_idx]
data_geoplot = df.loc[(df.id==name) & (df.date==datestr), ['lat', 'lon', 'cnt']]

st.write('## Day-by-day map')
st.write("Selected time: " + pd.Timestamp(datestr).day_name()  + ' ' + datestr)

scale_radius = st.slider('radius scaling', value=1, min_value=1, max_value=10)
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={"latitude": 50.76, "longitude": 4, "zoom": 1},
    layers=[pdk.Layer(
        "ScatterplotLayer",
        data=data_geoplot,
        get_position=["lon", "lat"],
        get_color=[200, 30, 0, 160],
        get_radius=['cnt'],
        radius_scale=scale_radius,
    )]
)
)