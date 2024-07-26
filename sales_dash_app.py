# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Read data
data = pd.read_csv('Online Sales Data.csv')

# Convert Columns to pandas dataframes and join them into their own frames
Dates = data['Date']
Dates = pd.to_datetime(Dates)
total_Rev = data['Total Revenue']
Dates_df = Dates.to_frame(name='Dates_df')
Total_rev_df = total_Rev.to_frame(name='Total_rev_df')
sales_by_month_data = pd.merge(Dates_df, Total_rev_df, left_index=True, right_index=True, how='outer')

# Set the Date column as the index
sales_by_month_data.set_index('Dates_df', inplace=True)

# Sort the totals by month and calculate the sum
sales_by_month = sales_by_month_data.resample('M').sum()

# Merge them by date
sales_by_date_data = pd.merge(Dates_df, Total_rev_df, left_index=True, right_index=True, how='outer')
# Set the Date column as the index
sales_by_date_data.set_index('Dates_df', inplace=True)
sales_by_date = sales_by_date_data.resample('D').sum()

# Make categories into a df
categories = data['Product Category']
categories_df = categories.to_frame(name='Categories')

# Merge it with revenue and sum them after grouping
total_Rev_by_category = pd.merge(categories_df, Total_rev_df, left_index=True, right_index=True, how='outer')
total_Rev_by_category_grouped = total_Rev_by_category.groupby('Categories')['Total_rev_df'].sum().reset_index()

# Convert regions to a df
regions = data['Region']
regions_df = regions.to_frame(name='Region')

# Join it with revenue 
Rev_by_region = pd.merge(regions_df, Total_rev_df, left_index=True, right_index=True, how='outer')

# Join that with date
Rev_by_region_dated = pd.merge(Rev_by_region, Dates_df, left_index=True, right_index=True, how='outer')
Rev_by_region_dated.set_index('Dates_df', inplace=True)

# Group by region
Rev_by_region_dated_grouped = Rev_by_region_dated.groupby('Region')

# get data for each group
North_America = Rev_by_region_dated_grouped.get_group('North America')
Europe = Rev_by_region_dated_grouped.get_group('Europe')
Asia = Rev_by_region_dated_grouped.get_group('Asia')

# Plot chart
region = px.line(North_America, x=North_America.index, y='Total_rev_df', title='Total Sales by Date')

# Add line for Europe
region.add_trace(go.Scatter(x=Europe.index, y=Europe['Total_rev_df'],
                    mode='lines',
                    name='Europe Data'))

# Add line for Asia
region.add_trace(go.Scatter(x=Asia.index, y=Asia['Total_rev_df'],
                    mode='lines',
                    name='Asia Data'))

# range slider
region.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

# Initialize the app
sales_dash_app = Dash()

# App layout
sales_dash_app.layout = html.Div([
    html.H2('Sales Data Visualization'),
    html.H2('Sales Data'),
    dash_table.DataTable(data=data.to_dict('records'), page_size=10),
    html.H2('Total Sales by Month'),
    dash_table.DataTable(data=sales_by_month.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.bar(sales_by_month, x=sales_by_month.index, y='Total_rev_df', title='Total Sales by Month')),
    html.H2('Total Sales by Date'),
    dash_table.DataTable(data=sales_by_month.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.line(sales_by_date, x=sales_by_date.index, y='Total_rev_df', title='Total Sales by Date')),
    html.H2('Total Sales by Product Category'),
    dash_table.DataTable(data=total_Rev_by_category_grouped.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.bar(total_Rev_by_category_grouped, x=total_Rev_by_category_grouped['Categories'], y=total_Rev_by_category_grouped['Total_rev_df'], title='Revenue grouped by Category')),
    html.H2('Total Sales by Region and Date'),
    dcc.Graph(figure=region),
    html.H2('Total sales by payment method'),
    dcc.Graph(figure=px.pie(data, values='Total Revenue', names='Payment Method', title='Percentage of Sales by Payment Method'))
])

# Run the app
if __name__ == '__main__':
    sales_dash_app.run(debug=True)