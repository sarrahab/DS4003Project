# %% [markdown]
# ### Assignment #5: Basic UI--Sarrah Abdulali
# 
# DS4003 | Spring 2024
# 
# Objective: Practice buidling basic UI components in Dash. 
# 
# Task: Build an app that contains the following components user the gapminder dataset: `gdp_pcap.csv`. [Info](https://www.gapminder.org/gdp-per-capita/)
# 
# UI Components:
# A dropdown menu that allows the user to select `country`
# - The dropdown should allow the user to select multiple countries
# - The options should populate from the dataset (not be hard-coded)
# A slider that allows the user to select `year`
# - The slider should allow the user to select a range of years
# - The range should be from the minimum year in the dataset to the maximum year in the dataset
# A graph that displays the `gdpPercap` for the selected countries over the selected years
# - The graph should display the gdpPercap for each country as a line
# - Each country should have a unique color
# - The graph should have a title and axis labels in reader friendly format
#  
# 
# (2) Write Callback functions for the slider and dropdown to interact with the graph
# 
# This means that when a user updates a widget the graph should update accordingly.
# The widgets should be independent of each other. 
# Layout:
# - Use a stylesheet
# - There should be a title at the top of the page
# - There should be a description of the data and app below the title (3-5 sentences)
# - The dropdown and slider should be side by side above the graph and take up the full width of the page
# - The graph should be below the dropdown and slider and take up the full width of the page
# Submission:
# - Deploy your app on Render. 
# - In Canvas, submit the URL to your public Github Repo (made specifically for this assignment)
# - The readme in your GitHub repo should contain the URL to your Render page. 
# 
# 
# **For help you may use the web resources and pandas documentation. No co-pilot or ChatGPT.**

# %%
#import dependencies
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output

# %%
#read in the dataset and then see first five rows of the dataframe df
df = pd.read_csv('gdp_pcap.csv')
df.head()

# %%
# conversion function to thousands, with check for type
def convert_k_to_thousand(value):
    if isinstance(value, str) and value.endswith('k'):
        return float(value[:-1]) * 1000
    return value

# function to convert all values to float values, otherwise return original value
def try_convert_to_float(x):
    try:
        return float(x)
    except ValueError:
        return x

# apply function to each element in df
df = df.applymap(try_convert_to_float)

# apply the above conversion only to specific columns excluding the first one since it has countries
for column in df.columns[1:]:  # exclude first column by slicing df.columns[1:]
    df[column] = df[column].apply(convert_k_to_thousand)


df.head()



# %%
# explore the dataset using pandas
# get the number of rows and columns
df.shape

# %%
# data types of the columns
df.dtypes

# %%
# distinct values in the name column
df['country'].unique()

# %%
# how many observations for each distinct value in the name column
df['country'].value_counts()

# %% [markdown]
# ONTO THE DASH

# %% [markdown]
# (1) UI Components:
# A dropdown menu that allows the user to select `country`
# - The dropdown should allow the user to select multiple countries
# - The options should populate from the dataset (not be hard-coded)
# A slider that allows the user to select `year`
# - The slider should allow the user to select a range of years
# - The range should be from the minimum year in the dataset to the maximum year in the dataset
# A graph that displays the `gdpPercap` for the selected countries over the selected years
# - The graph should display the gdpPercap for each country as a line
# - Each country should have a unique color
# - The graph should have a title and axis labels in reader friendly format
#  
# 
# (2) Write Callback functions for the slider and dropdown to interact with the graph
# 
# This means that when a user updates a widget the graph should update accordingly.
# The widgets should be independent of each other. 
# Layout:
# - Use a stylesheet
# - There should be a title at the top of the page
# - There should be a description of the data and app below the title (3-5 sentences)
# - The dropdown and slider should be side by side above the graph and take up the full width of the page
# - The graph should be below the dropdown and slider and take up the full width of the page

# %%
# import external stylesheet using class code below

stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = dash.Dash(__name__, external_stylesheets=stylesheets) # initialize the app
server = app.server

# %%
# extract the year columns only (since 'country' is technically the first column in df)
year_cols = df.columns.tolist()[1:]  # convert it to a list and skip the first 'country' column

# convert year columns to integers and get the minimum and maximum year
min_yr = int(year_cols[0])
max_yr = int(year_cols[-1])

# callback to update the graph based on user inputs from dropdown and slider
@app.callback(
    Output('gdp-per-capita-graph', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-range-slider', 'value')]
)
def update_graph(selected_countries, year_range):
    # filter the DataFrame based on selected countries and year range
    selections = df[df['country'].isin(selected_countries)]
    # melt the dataframe to have a long format for plotting with plotly
    selections = selections.melt(id_vars=['country'], value_vars=year_cols, var_name='Year', value_name='GDP per Capita')
    # filter the melted dataframe for the selected year range
    selections = selections[selections['Year'].astype(int).between(year_range[0], year_range[1])]
    
    # create the figure with plotly express line chart for the selected data
    fig = px.line(
        selections, 
        x='Year', 
        y='GDP per Capita', 
        color='country',
        title='GDP per Capita Over Selected Years',
        labels={'GDP per Capita': 'GDP per Capita (current US $)'}
    )
    
    return fig

app.layout = html.Div([
    # app title
    html.H1('GDP per Capita Analysis of Different Countries  Over Time', style={'textAlign': 'center'}),
    # app description in 3 sentences
    html.P('''
        This application allows for interactive analysis of GDP per Capita data for over 190 countries in the world. 
        You can see how GDP per Capita has changed over time if you choose to select some countries in the dropdown and a year range in the slider. 
        The line graph gives a clear visual of trends and comparisons across different nations!
    ''', style={'textAlign': 'center'}),
    # container for dropdown + slider
    html.Div([
        # dropdown to select countries!
        html.Div([
            dcc.Dropdown(
                options=[{'label': country, 'value': country} for country in df['country']],
                value=df['country'].tolist(),  # default value as all countries!
                multi=True,  # allow multiple countries' selections
                id='country-dropdown'
            )
        ], style={'display': 'inline-block', 'width': '49%'}),
        # slider for selecting year range!
        html.Div([
            dcc.RangeSlider(
                id='year-range-slider',
                min=min_yr,
                max=max_yr,
                value=[min_yr, max_yr],  # default value is the full range
                marks= {year: str(year) if year % 100 == 0 else '' for year in range(min_yr, max_yr, 51)},  # for user friendliness, tick marks every 50 years and a year text label every 100 years
                step=1,  # slider moves in increments of 1 year
                tooltip={"placement": "bottom", "always_visible":True},
                allowCross=False,  # prevents the sliders from crossing over each other / user can't select invalid range
            )
        ], style={'display': 'inline-block', 'width': '49%'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px'}),
    # container for graph!
    html.Div([
        dcc.Graph(id='gdp-per-capita-graph')
    ], style={'width': '100%', 'padding': '10px'})
])

# run the app
if __name__ == '__main__':
    #appy.run(jupyter_mode='tab', debug=True)
    # i changed the code above to reflect what professor wanted us to do!
    app.run_server(debug=True) #run the server

# %%



