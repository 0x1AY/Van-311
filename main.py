import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt



# Import van311 service request data
service_requests = pd.read_csv('https://raw.githubusercontent.com/0x1AY/Van-311/refs/heads/main/data/service_requests_final.csv')

# Display unique service request types
service_requests['Service request type'].unique()

st.title('Project 2')
st.header('Improving Vancouver’s 311 Service Efficiency Using Data Analytics')
# st.subheader('By Aminu Yiwere')

st.header('Executive Summary')
st.write("The 311 service in Vancouver is a crucial resource for residents to report local issues, request city services, and obtain information. However, increasing demand has highlighted inefficiencies in handling requests, responding to inquiries, and managing contact center operations. This project aims to analyze the 311 service data to uncover patterns, identify service bottlenecks, and recommend solutions to enhance the efficiency and quality of the 311 system.")
st.write("The primary goals are to understand public concerns, improve response efficiency, optimize contact center performance, and forecast future service demand. By leveraging datasets on service requests, inquiry volumes, and contact center metrics, this analysis provides a data-driven foundation for actionable improvements.")


# Identify and categorize request types
request_types = service_requests['Service request type'].unique()
# Example categorization (customize as needed)
categories = {
    'Garbage': ['Abandoned Recyclables Case', 'Garbage Pickup'],
    'Maintenance': ['Street Light Out', 'Pothole Repair'],
    # Add more categories as needed
}

# Determine most frequent request types
st.header("20 Most Frequent Request types")






df = service_requests

# Count occurrences of service request types and categories
service_request_counts = (
    df.groupby(["Service request type", "Category"])
    .size()
    .reset_index(name="Count")
)

# Sort by count and select top 20
top_20 = service_request_counts.sort_values(by="Count", ascending=False).head(20)

# Plot with Plotly
fig = px.bar(
    top_20,
    x="Service request type",
    y="Count",
    color="Category",
    title="Top 20 Service Request Types by Category",
    labels={"Service request type": "Service Request Type", "Count": "Number of Requests"},
    text="Count",
)

# Customize layout
fig.update_layout(
    xaxis_tickangle=45,
    xaxis_title="Service Request Type",
    yaxis_title="Count",
    legend_title="Category",
    height=600,
    width=900
)

# Display in Streamlit
st.plotly_chart(fig)

# Prepare data for visualization
# Aggregate counts for month, weekday, and hour
monthly_trends = service_requests.groupby('month').size().reset_index(name='Count')
monthly_trends['Metric'] = 'Month'

weekly_trends = service_requests.groupby('weekday').size().reset_index(name='Count')
weekly_trends['Metric'] = 'Weekday'

hourly_trends = service_requests.groupby('hour').size().reset_index(name='Count')
hourly_trends['Metric'] = 'Hour'

# Combine data into a single DataFrame
monthly_trends.rename(columns={'month': 'Value'}, inplace=True)
weekly_trends.rename(columns={'weekday': 'Value'}, inplace=True)
hourly_trends.rename(columns={'hour': 'Value'}, inplace=True)
combined_data = pd.concat([monthly_trends, weekly_trends, hourly_trends], ignore_index=True)

# Define Altair dropdown selection
selection = alt.selection_single(
    fields=['Metric'], 
    bind=alt.binding_select(options=['Month', 'Weekday', 'Hour'], name="Time Period: "),
    value='Month'  # Set the initial value using the value argument
)
# Create the chart
chart = alt.Chart(combined_data).mark_line(point=True).encode(
    x=alt.X('Value:O', title='Time'),
    y=alt.Y('Count:Q', title='Number of Requests'),
    color=alt.Color('Metric:N', legend=None),
    tooltip=['Value', 'Count']
).add_selection(
    selection
).transform_filter(
    selection
).properties(
    title="Service Request Trends by Time",
    width=800,
    height=400
)

# Display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)




service_requests['Service request open timestamp'] = pd.to_datetime(
    service_requests['Service request open timestamp'], errors='coerce'
)

# Extract time-based columns if not already present
if 'month' not in service_requests.columns:
    service_requests['month'] = service_requests['Service request open timestamp'].dt.month
if 'weekday' not in service_requests.columns:
    service_requests['weekday'] = service_requests['Service request open timestamp'].dt.weekday
if 'hour' not in service_requests.columns:
    service_requests['hour'] = service_requests['Service request open timestamp'].dt.hour

# Title
st.title("Service Request Dashboard")

# Summary Statistics
st.subheader("Summary of Service Requests")

total_requests = len(service_requests)
categories_count = service_requests["Category"].nunique()
neighborhoods_count = service_requests["Local area"].nunique()
most_common_category = service_requests["Category"].value_counts().idxmax()
most_common_neighborhood = service_requests["Local area"].value_counts().idxmax()

# Display summary statistics
st.metric("Total Requests", total_requests)
st.metric("Total Categories", categories_count)
st.metric("Total Neighborhoods", neighborhoods_count)
st.metric("Most Common Category", most_common_category)
st.metric("Most Common Neighborhood", most_common_neighborhood)

# Add a separator
st.markdown("---")

# Filter Section
st.subheader("Filter Service Requests")
selected_category = st.selectbox("Select a Category", ["All"] + list(service_requests["Category"].unique()))
selected_neighborhood = st.selectbox("Select a Neighborhood", ["All"] + list(service_requests["Local area"].unique()))

# Apply filters
filtered_data = service_requests.copy()
if selected_category != "All":
    filtered_data = filtered_data[filtered_data["Category"] == selected_category]
if selected_neighborhood != "All":
    filtered_data = filtered_data[filtered_data["Local area"] == selected_neighborhood]

# Neighborhood Summary
neighborhood_summary = (
    filtered_data.groupby(["Local area", "Latitude", "Longitude"])
    .size()
    .reset_index(name="Request Volume")
)

# Weekday Trends
weekday_trends = (
    filtered_data.groupby("weekday")
    .size()
    .reset_index(name="Request Volume")
)

# Time of Day Trends
hourly_trends = (
    filtered_data.groupby("hour")
    .size()
    .reset_index(name="Request Volume")
)

# Map Visualization
st.subheader("Request Volume by Neighborhood")
if not neighborhood_summary.empty:
    fig_map = px.scatter_mapbox(
        neighborhood_summary,
        lat="Latitude",
        lon="Longitude",
        size="Request Volume",
        color="Request Volume",
        hover_name="Local area",
        hover_data={"Latitude": False, "Longitude": False, "Request Volume": True},
        title="Request Volume by Neighborhood",
        color_continuous_scale="Viridis",
        zoom=11,
        height=600,
    )
    fig_map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.write("No data available for the selected filters.")

# Weekday Trend Visualization
st.subheader("Request Volume by Weekday")
if not weekday_trends.empty:
    fig_weekday = px.bar(
        weekday_trends,
        x="weekday",
        y="Request Volume",
        title="Requests by Weekday",
        labels={"weekday": "Weekday (0=Monday, 6=Sunday)", "Request Volume": "Number of Requests"},
        text="Request Volume",
    )
    fig_weekday.update_layout(xaxis_title="Weekday", yaxis_title="Request Volume")
    st.plotly_chart(fig_weekday, use_container_width=True)
else:
    st.write("No data available for the selected filters.")

# Time of Day Trend Visualization
st.subheader("Request Volume by Time of Day")
if not hourly_trends.empty:
    fig_hourly = px.bar(
        hourly_trends,
        x="hour",
        y="Request Volume",
        title="Requests by Hour of Day",
        labels={"hour": "Hour of Day", "Request Volume": "Number of Requests"},
        text="Request Volume",
    )
    fig_hourly.update_layout(xaxis_title="Hour of Day", yaxis_title="Request Volume")
    st.plotly_chart(fig_hourly, use_container_width=True)
else:
    st.write("No data available for the selected filters.")