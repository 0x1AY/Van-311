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


# 	Closure and Fulfillment Analysis:


# more analysis

# Calculate closure summary
closure_summary = (
    service_requests.groupby("Category_cr")
    .size()
    .reset_index(name="Count")
)

# Calculate percentages
closure_summary["Percentage"] = (closure_summary["Count"] / closure_summary["Count"].sum()) * 100

# Display summary table
st.title("Closure and Fulfillment Analysis")
# st.subheader("Summary of Closure Categories")
# st.dataframe(closure_summary)

# Visualize closure categories distribution (Bar Chart)
# st.subheader("Distribution of Closure Categories")
# fig_bar = px.bar(
#     closure_summary,
#     x="Category_cr",
#     y="Count",
#     text="Percentage",
#     title="Closure Categories Distribution",
#     labels={"Category_cr": "Closure Category", "Count": "Number of Requests"},
#     color="Category_cr",
# )
# fig_bar.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
# st.plotly_chart(fig_bar, use_container_width=True)

# Visualize closure categories breakdown (Pie Chart)
st.subheader("Closure Categories Breakdown")
fig_pie = px.pie(
    closure_summary,
    names="Category_cr",
    values="Count",
    # title="Closure Categories Breakdown",
    color="Category_cr",
    hole=0.4,
)
st.plotly_chart(fig_pie, use_container_width=True)

# Filters for Category and Local Area
st.subheader("Explore Closure Patterns by Filters")
selected_category = st.selectbox("Filter by Service Request Category", ["All"] + list(service_requests["Category"].unique()))
selected_local_area = st.selectbox("Filter by Local Area", ["All"] + list(service_requests["Local area"].unique()))

# Apply filters
filtered_data = service_requests.copy()
if selected_category != "All":
    filtered_data = filtered_data[filtered_data["Category"] == selected_category]
if selected_local_area != "All":
    filtered_data = filtered_data[filtered_data["Local area"] == selected_local_area]

# Recalculate closure summary based on filters
filtered_closure_summary = (
    filtered_data.groupby("Category_cr")
    .size()
    .reset_index(name="Count")
)
filtered_closure_summary["Percentage"] = (filtered_closure_summary["Count"] / filtered_closure_summary["Count"].sum()) * 100

# Display filtered summary table
st.subheader("Filtered Closure Summary")
st.dataframe(filtered_closure_summary)

# Trends Over Time
st.subheader("Closure Trends Over Time")
trend_data = (
    filtered_data.groupby(["month", "Category_cr"])
    .size()
    .reset_index(name="Count")
)

fig_trends = px.line(
    trend_data,
    x="month",
    y="Count",
    color="Category_cr",
    title="Closure Categories Over Time",
    labels={"month": "Month", "Count": "Number of Requests", "Category_cr": "Closure Category"},
)
st.plotly_chart(fig_trends, use_container_width=True)



# Convert timestamps to datetime and remove timezone info
service_requests['Service request open timestamp'] = pd.to_datetime(
    service_requests['Service request open timestamp'], errors='coerce'
).dt.tz_localize(None)

service_requests['Service request close date'] = pd.to_datetime(
    service_requests['Service request close date'], errors='coerce'
).dt.tz_localize(None)

# Calculate completion time (in days)
service_requests['Completion Time (days)'] = (
    service_requests['Service request close date'] - service_requests['Service request open timestamp']
).dt.total_seconds() / (24 * 3600)  # Convert seconds to days

# Filter out requests without completion dates or negative durations
service_requests = service_requests[service_requests['Completion Time (days)'] >= 0]

# Completion Time by Request Type
completion_by_type = (
    service_requests.groupby('Category')['Completion Time (days)']
    .mean()
    .reset_index()
    .rename(columns={'Completion Time (days)': 'Avg Completion Time (days)'})
)

# Completion Time by Neighborhood
completion_by_neighborhood = (
    service_requests.groupby('Local area')['Completion Time (days)']
    .mean()
    .reset_index()
    .rename(columns={'Completion Time (days)': 'Avg Completion Time (days)'})
)

# Completion Time by Month
service_requests['month'] = service_requests['Service request open timestamp'].dt.month
completion_by_month = (
    service_requests.groupby('month')['Completion Time (days)']
    .mean()
    .reset_index()
    .rename(columns={'Completion Time (days)': 'Avg Completion Time (days)'})
)

# Streamlit Dashboard
st.title("Request Completion Time Analysis")

# Display Completion Time by Request Type
st.subheader("Average Completion Time by Request Category")
fig_type = px.bar(
    completion_by_type,
    x="Category",
    y="Avg Completion Time (days)",
    # title="Average Completion Time by Request Category",
    labels={"Service request type": "Request Type", "Avg Completion Time (days)": "Average Completion Time (days)"},
    text="Avg Completion Time (days)"
)
fig_type.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig_type.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_type, use_container_width=True)

# Display Completion Time by Neighborhood
st.subheader("Average Completion Time by Neighborhood")
fig_neighborhood = px.bar(
    completion_by_neighborhood,
    x="Local area",
    y="Avg Completion Time (days)",
    # title="Average Completion Time by Neighborhood",
    labels={"Local area": "Neighborhood", "Avg Completion Time (days)": "Average Completion Time (days)"},
    text="Avg Completion Time (days)"
)
fig_neighborhood.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig_neighborhood.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_neighborhood, use_container_width=True)

# Display Completion Time by Month
st.subheader("Average Completion Time by Month")
fig_month = px.line(
    completion_by_month,
    x="month",
    y="Avg Completion Time (days)",
    # title="Average Completion Time by Month",
    labels={"month": "Month", "Avg Completion Time (days)": "Average Completion Time (days)"},
    markers=True
)
st.plotly_chart(fig_month, use_container_width=True)


#  311 Inquiry Volume Dataset Analysis

#import inquiry volume data set
inquiry_volume = pd.read_csv("https://raw.githubusercontent.com/0x1AY/Van-311/refs/heads/main/data/3-1-1-inquiry-volume.csv", delimiter=";")

# Convert "Year Month" to datetime
inquiry_volume["Year Month"] = pd.to_datetime(inquiry_volume["Year Month"], format="%Y-%m")

# Inquiry Volume Trends
st.title("311 Inquiry Volume Dataset Analysis")
st.subheader("Inquiry Volume Trends")

# Aggregate volume by time
volume_trends = (
    inquiry_volume.groupby("Year Month")["Number of Records"]
    .sum()
    .reset_index()
)

# Line Chart: Volume Over Time
fig_trends = px.line(
    volume_trends,
    x="Year Month",
    y="Number of Records",
    title="Inquiry Volume Over Time",
    labels={"Year Month": "Year-Month", "Number of Records": "Number of Inquiries"},
    markers=True,
)
st.plotly_chart(fig_trends, use_container_width=True)

# Workforce Allocation Suggestion
st.subheader("Workforce Allocation Suggestions")
peak_month = volume_trends.loc[volume_trends["Number of Records"].idxmax()]
low_month = volume_trends.loc[volume_trends["Number of Records"].idxmin()]
st.write(f"**Peak Demand Month:** {peak_month['Year Month'].strftime('%B %Y')} with {peak_month['Number of Records']} inquiries.")
st.write(f"**Low Demand Month:** {low_month['Year Month'].strftime('%B %Y')} with {low_month['Number of Records']} inquiries.")
st.write(
    """
    **Workforce Allocation Strategies:**
    - Increase workforce during peak months to handle higher demand.
    - Reduce workforce or reallocate to other tasks during low-demand months.
    - Monitor historical trends for long-term planning.
    """
)

# Impact of Web/Chat Options
st.subheader("Impact of Alternative Channels (Web/Chat)")

# Filter for web and chat channels
channel_trends = (
    inquiry_volume.groupby(["Year Month", "Channel"])["Number of Records"]
    .sum()
    .reset_index()
)

# Line Chart: Channel Popularity Over Time
fig_channels = px.line(
    channel_trends,
    x="Year Month",
    y="Number of Records",
    color="Channel",
    title="Inquiry Volume by Channel Over Time",
    labels={"Year Month": "Year-Month", "Number of Records": "Number of Inquiries", "Channel": "Channel"},
    markers=True,
)
st.plotly_chart(fig_channels, use_container_width=True)

# Popularity of Web/Chat Options
st.subheader("Channel Popularity Insights")
web_chat_trends = channel_trends[channel_trends["Channel"].isin(["Web", "Chat"])]
web_chat_total = web_chat_trends["Number of Records"].sum()
total_inquiries = inquiry_volume["Number of Records"].sum()

web_chat_percentage = (web_chat_total / total_inquiries) * 100
st.write(f"**Web/Chat Usage:** {web_chat_percentage:.2f}% of all inquiries.")
st.write(
    """
    **Observations:**
    - Track the growth of web and chat channels over time to assess digital adoption.
    - Consider shifting resources to support popular channels during peak times.
    """
)


# contact center metric analysis

contact_center_metrics = pd.read_csv("https://raw.githubusercontent.com/0x1AY/Van-311/refs/heads/main/data/3-1-1-contact-centre-metrics.csv", delimiter=";")



# Convert "Date" to datetime
contact_center_metrics["Date"] = pd.to_datetime(contact_center_metrics["Date"])

# Calculate percentage of calls handled vs. abandoned
contact_center_metrics["Handled Percentage"] = (
    contact_center_metrics["CallsHandled"] / contact_center_metrics["CallsOffered"]
) * 100
contact_center_metrics["Abandoned Percentage"] = (
    contact_center_metrics["CallsAbandoned"] / contact_center_metrics["CallsOffered"]
) * 100

# Aggregate metrics by month
contact_center_metrics["Year-Month"] = contact_center_metrics["Date"].dt.to_period("M").astype(str)  # Convert to string
monthly_metrics = contact_center_metrics.groupby("Year-Month").agg(
    {"CallsOffered": "sum", "CallsHandled": "sum", "CallsAbandoned": "sum",
     "AverageSpeedofAnswer": "mean", "ServiceLevel": "mean"}
).reset_index()

# Recalculate monthly percentages
monthly_metrics["Handled Percentage"] = (
    monthly_metrics["CallsHandled"] / monthly_metrics["CallsOffered"]
) * 100
monthly_metrics["Abandoned Percentage"] = (
    monthly_metrics["CallsAbandoned"] / monthly_metrics["CallsOffered"]
) * 100

# Streamlit Dashboard
st.title("311 Contact Centre Metrics Analysis")

# Call Handling Metrics
st.subheader("Call Handling Metrics: Handled vs. Abandoned")
fig_handled_abandoned = px.bar(
    monthly_metrics,
    x="Year-Month",
    y=["Handled Percentage", "Abandoned Percentage"],
    barmode="stack",
    title="Percentage of Calls Handled vs. Abandoned Over Time",
    labels={"value": "Percentage", "Year-Month": "Year-Month", "variable": "Metric"},
)
st.plotly_chart(fig_handled_abandoned, use_container_width=True)

# Average Response Times Over Time
st.subheader("Average Response Times Over Time")
fig_response_times = px.line(
    monthly_metrics,
    x="Year-Month",
    y="AverageSpeedofAnswer",
    title="Average Response Times Over Time",
    labels={"Year-Month": "Year-Month", "AverageSpeedofAnswer": "Average Speed of Answer (seconds)"},
    markers=True,
)
st.plotly_chart(fig_response_times, use_container_width=True)

# Performance Correlations
st.subheader("Performance Correlations")
correlation_metrics = contact_center_metrics[["CallsHandled", "AverageSpeedofAnswer", "ServiceLevel"]].corr()

st.write("**Correlation Matrix:**")
st.dataframe(correlation_metrics)

# Recommendations
st.subheader("Recommendations for Operational Efficiency")
st.write(
    """
    **Based on findings:**
    - Optimize workforce allocation during months with higher abandonment rates and response times.
    - Reduce average response times during peak call volumes to minimize customer frustration.
    - Monitor and improve service level to maintain call resolution quality.
    """
)