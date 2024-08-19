import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

fav_icon = Image.open(r"apoio_logo.jpg")

st.set_page_config(
    page_title="Patient Data Analysis",
    page_icon=fav_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv('dashboard_data.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def load_css():
    with open("style.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

load_css()
img = Image.open(r"apoio_logo.jpg")
st.image(img, width=300)
st.write("##")

df = load_data()

st.sidebar.title("Filters")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(df['date']).min())
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(df['date']).max())

selected_durations = st.sidebar.slider("Call Duration (in seconds)", min_value=df['duration'].min(), max_value=df['duration'].max(), value=(0.0, df['duration'].max()))

categories = df['category'].unique()
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

# countries = df['countryName'].unique()
# selected_countries = st.sidebar.multiselect("Country", countries, default=countries)

localities = df['province'].unique()
selected_localities = st.sidebar.multiselect("Province", localities, default=localities)

genders = df['gender'].unique()
selected_genders = st.sidebar.multiselect("Gender", genders, default=genders)

languages = df['language'].unique()
selected_languages = st.sidebar.multiselect("Language", languages, default=languages)

chattype = df['chatType'].unique()
selected_chattype = st.sidebar.multiselect("Chat Type", chattype, default=chattype)

filtered_df = df[
    (df['date'] >= pd.to_datetime(start_date)) &
    (df['date'] <= pd.to_datetime(end_date)) &
    (df['duration'] >= selected_durations[0]) &
    (df['duration'] <= selected_durations[1]) &
    (df['category'].isin(selected_categories)) &
    # (df['countryName'].isin(selected_countries)) &
    (df['province'].isin(selected_localities)) &
    (df['gender'].isin(selected_genders)) &
    (df['language'].isin(selected_languages)) &
    (df['chatType'].isin(selected_chattype))
]

st.write("### KPI Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Users", filtered_df['userId'].nunique())

with col2:
    st.metric("Total Calls", filtered_df['callId'].count())

with col3:
    st.metric("Total Chats", filtered_df['chatId'].count())

with col4:
    avg_duration = filtered_df['duration'].mean()
    st.metric("Avg Call Duration (sec)", f"{avg_duration:.2f}" if pd.notna(avg_duration) else "N/A")

with st.container():
    st.write("### Province-wise categories")
    bar_chart_fig = px.bar(
                filtered_df.groupby(['province', 'category']).size().reset_index(name='count'),
                x='province',
                y='count',
                color='category',
                barmode="stack",
                text_auto=True,
            )
    st.plotly_chart(bar_chart_fig, use_container_width=True)

    st.write("##")
    
    st.write("### Age distribution across Provinces")
    scatter_chart_fig = px.scatter(filtered_df, x='age', y='province', color='category', size='duration', log_x=True, size_max=60)
    st.plotly_chart(scatter_chart_fig, use_container_width=True)


    st.write("### Chat Type Distribution")
    pie_chart_fig = px.pie(filtered_df, names='chatType')
    st.plotly_chart(pie_chart_fig, use_container_width=True)

    st.write("### Age vs. Height/Weight with Category Hue")
    scatter_plot_fig = px.scatter(filtered_df, x='age', y='height', color='category', size='weight', hover_data=['weight'])
    st.plotly_chart(scatter_plot_fig, use_container_width=True)


    st.write("### Chats over Time")
    group_line = (
            filtered_df.groupby(["date"])
            .count()['chatId']
            .reset_index()
        )
    line_chart_fig = px.line(group_line, x='date', y='chatId')
    st.plotly_chart(line_chart_fig, use_container_width=True)

    st.write("### Geographical Distribution of Calls/Chats")

    grouped_df = filtered_df.groupby(['latitude', 'longitude', 'category', 'countryName', 'province', 'thoroughfare']).size().reset_index(name='num_cases')

    map_fig2 = px.scatter_mapbox(grouped_df, 
                                lat='latitude', 
                                lon='longitude', 
                                color='category', 
                                size='num_cases',
                                hover_name='countryName', 
                                hover_data=['province', 'thoroughfare', 'num_cases'],
                                mapbox_style="open-street-map", 
                                zoom=3)

    st.plotly_chart(map_fig2, use_container_width=True)

    # map_fig = px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude', color='category', size='duration',
    #                             hover_name='countryName', hover_data=['province', 'thoroughfare'],
    #                             mapbox_style="open-street-map", zoom=3)
    # st.plotly_chart(map_fig, use_container_width=True)

    
    # map_fig_chat = px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude', color='chatType', size='age',
    #                             hover_name='countryName', hover_data=['province', 'thoroughfare'],
    #                             mapbox_style="open-street-map", zoom=3)
    # st.plotly_chart(map_fig_chat, use_container_width=True)

    
    st.write("### Location Density of Calls")
    heatmap_fig = px.density_mapbox(filtered_df, lat='latitude', lon='longitude', z='duration',
                                    radius=10, center=dict(lat=-20, lon=36),
                                    mapbox_style="open-street-map", zoom=3)
    st.plotly_chart(heatmap_fig)

    
    st.write("### Province-wise drilldown")
    group_sun = (
            filtered_df.groupby(["province", "category", "chatType", 'gender'])
            .size()
            .reset_index(name="count")
        )
    sunburst_fig = px.sunburst(group_sun, path=['province', 'category', 'chatType', 'gender'], values='count',  width=700, height=700)
    st.plotly_chart(sunburst_fig, use_container_width=True)