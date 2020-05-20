import pandas as pd
import streamlit as st
import pydeck as pdk


st.title('My first app')

@st.cache
def load_df(fpath):
    df_tmp = pd.read_csv(fpath)
    df = df_tmp.set_index([pd.Index(range(len(df_tmp))),'Province/State', 'Country/Region', 'Lat', 'Long']).transpose()
    df.index=pd.to_datetime(df.index)
    return df


@st.cache
def load_flat_df(fpath):
    df = pd.read_csv(fpath)
    df = df.rename(columns=dict(Long='lon', Lat='lat'))
    # df.index=pd.to_datetime(df_tmp.index)
    return df

fpath_dict = dict(deaths=r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
                  comfirmed=r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
                  recovered=r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
name = st.selectbox(
    "Choose dataset", ["deaths",'comfirmed','recovered'], 0
)
data_id = fpath_dict[name]

data_flat = load_flat_df(data_id)

st.sidebar.markdown("### view datasheet?")
checkbox_rawdata = st.sidebar.checkbox('show raw data')
if checkbox_rawdata:
    "### raw data"
    st.write(data_flat)
data_flat.rename(columns={"5/18/20":'test'},inplace=True)
data_multi_index = load_df(data_id)
data = data_multi_index.groupby(level='Country/Region', axis=1).aggregate('sum')

checkbox_data = st.sidebar.checkbox('show aggregated data')

cumul = st.checkbox('cumulate data up to now.',True)
if not cumul:
    data = data.diff()

if checkbox_data:
    "### aggregated data"
    st.write(data)
countries = st.multiselect(
    "Choose countries", list(data.columns), ["Netherlands", "Belgium"]
)



data_select = data.loc[:,countries]
data_select.columns.name = None
st.area_chart(data_select.sort_values(by=data_select.index[-1], axis=1, ascending=False))


"### Corona map"

select_time = st.selectbox(
    "Choose day", data_flat.columns[5:], (len(data_flat.columns)-6)
)


@st.cache
def get_data_at_time(time):
    data = data_flat.loc[:, ['lon', 'lat', time]].copy()
    return data
data_selected = get_data_at_time(select_time)

# st.map(data_flat.loc[:, ['lon', 'lat']])

scale_radius = st.slider('radius scaling',value=1,min_value=1,max_value=10)

st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={"latitude": 50.76, "longitude": 4, "zoom": 1},
        layers = [pdk.Layer(
            "ScatterplotLayer",
            data=data_selected,
            get_position=["lon", "lat"],
            get_color=[200, 30, 0, 160],
            get_radius=[select_time],
            radius_scale=scale_radius,
        )]
    )
)


#
# # st.line_chart(data.T)
# # #data /= 1000000.0
#
# # st.write(data.iloc[0,0])