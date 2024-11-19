import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt



# Import van311 service request data
service_requests = pd.read_csv('/Users/ay/Desktop/Project2/service_requests_final.csv')

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


import pandas as pd
import altair as alt
import streamlit as st



# Convert timestamps to datetime
service_requests['Service request open timestamp'] = pd.to_datetime(
    service_requests['Service request open timestamp'], errors='coerce'
)

# Add time-based columns
service_requests['month'] = service_requests['Service request open timestamp'].dt.month
service_requests['weekday'] = service_requests['Service request open timestamp'].dt.weekday
service_requests['hour'] = service_requests['Service request open timestamp'].dt.hour

# Aggregate counts for top 20 request types
top_20_request_types = (
    service_requests['Service request type']
    .value_counts()
    .head(20)
    .index
)

filtered_data = service_requests[service_requests['Service request type'].isin(top_20_request_types)]

# Prepare data for visualization
category_trends = (
    filtered_data.groupby(['Category', 'Service request type', 'month', 'weekday', 'hour'])
    .size()
    .reset_index(name='Count')
)

# Altair selection filters
category_selection = alt.selection_single(
    fields=['Category'], 
    bind=alt.binding_select(options=list(category_trends['Category'].unique()), name="Select Category: ")
)

# Combine time metrics into a single column
folded_data = category_trends.melt(
    id_vars=['Category', 'Service request type', 'Count'],
    value_vars=['month', 'weekday', 'hour'],
    var_name='Time Metric',
    value_name='Value'
)

# Define the chart
time_chart = alt.Chart(folded_data).transform_filter(
    category_selection
).mark_line(point=True).encode(
    x=alt.X('Value:O', title='Time Metric'),
    y=alt.Y('Count:Q', title='Number of Requests'),
    color='Service request type:N',
    tooltip=['Service request type', 'Time Metric', 'Value', 'Count']
).properties(
    title="Service Request Trends by Selected Time Metric",
    width=800,
    height=400
).add_selection(
    category_selection
)

# Streamlit to display the chart
st.altair_chart(time_chart, use_container_width=True)