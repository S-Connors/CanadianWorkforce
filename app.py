import json
import pandas as pd
from zipfile import ZipFile

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc



#-------------------------------------------------------------------------------

# Add the DataFrame
geojson = json.load(open('georef-canada-province.geojson'))

df = pd.read_csv('statcanada.csv.gz',compression='gzip')


df = df.get(['REF_DATE','GEO','Labour force characteristics',
     'North American Industry Classification System (NAICS)','Sex','Age group',
     'VALUE'])
df = df.dropna(subset = ['VALUE'])
df['VALUE'] = df['VALUE'] * 1000

# find both sexes and drop them
bothsex = df.index[ df.loc[:,'Sex'] == 'Both sexes']
df.drop(bothsex,axis = 'index', inplace=True)

# find females
f = df.copy()
f = f.loc[f.Sex == 'Females']
f.drop('Sex',axis='columns', inplace=True)
f.rename(columns = {'VALUE':'value_F'}, inplace=True)

# find males, merge and add new column
m = df
m = m.loc[m['Sex']== 'Males']
m.drop('Sex', axis = 'columns', inplace=True)
m.rename(columns = {'VALUE':'value_m'}, inplace=True)
df = f.merge(m, how = 'outer')

# new col total
df['Total']= df['value_F'] + df['value_m']

# new col female percent
df['Percent_F'] = df['value_F'] / df['Total']
df['Percent_F'] = df['Percent_F'] * 100
df['Percent_F'] = df['Percent_F'].round(2)

# new col male percent
df['Percent_M'] = df['value_m'] / df['Total']
df["Percent_M"] = df["Percent_M"] * 100
df['Percent_M'] = df['Percent_M'].round(2)

# adding sex back in
ff = df.copy()
ff = ff[['REF_DATE','GEO','Labour force characteristics',
        'North American Industry Classification System (NAICS)',
        'value_F','Age group','Percent_F','Total']]
ff['Sex'] = 'Female'

# creating one spot for ALL values
ff['Value'] = ff['value_F']
ff.drop('value_F', axis = 'columns', inplace=True)

# making one col for percent while keeping female % its own
ff['Percent'] = ff['Percent_F']

# adding sex back in
dd = df.copy()
dd = dd[['REF_DATE','GEO','Labour force characteristics',
        'North American Industry Classification System (NAICS)',
        'value_m','Age group','Percent_M','Total']]
dd['Sex'] = 'Male'

# creating one spot for ALL values
dd['Value'] = dd['value_m']
dd.drop('value_m', axis = 'columns', inplace=True)

# making one col for percent
dd['Percent'] = dd['Percent_M']
dd.drop('Percent_M', axis = 'columns', inplace=True)

# make into one df
df = ff.merge(dd, how = 'outer')

# add token for themes
token = 'pk.eyJ1Ijoic3RlcGg0NzMyIiwiYSI6ImNsM3ZteDdzdjJtZWEzaW9leXVuejB4djYifQ.WIadkBsq3np49mTByYvSTw'
px.set_mapbox_access_token(token)

#-------------------------------------------------------------------------------

# Themes for bootstrap
# https://www.bootstrapcdn.com/bootswatch/
app = Dash(__name__,
    external_stylesheets=[dbc.themes.MINTY],
    # Meta_taga allows to resize for phone
    meta_tags=[
        {'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'}
        ]
    )

#declare your server for gunicorn to find
server = app.server

# Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div(
                'Canadian Workforce',
                style = {
                    'textAlign': 'center',
                    'color': '#383838',
                    'fontSize': 35,
                    'font-family':'Arial Black'
                    }
                ),
        xs=12, sm=12, md=12, lg=12, xl=12),
    ]),

    dbc.Row([
        dbc.Col(
            html.Div(
                '''Explore the history of Canadian women in the
                workforce through the data collected by Statistics Canada.''',
                style={
                    'textAlign': 'center',
                    'color': '#636262',
                    'fontSize': 22
                    }
            ),
        xs=12, sm=12, md=12, lg=12, xl=12
        ),
    ]),

    dbc.Row([
        dbc.Col(
            html.Div('''Industries are sorted by the North American Industry Classification
                System (NAICS).''',
                style={
                    'textAlign': 'center',
                    'color' : 'grey',
                    'fontSize' : 19
                }
            ),
        xs=12, sm=12, md=12, lg=12, xl=12
        ),
    ]),

    dbc.Row([
        dbc.Col(
            html.Br()
        )
    ]),

    dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='sclt_job',
                    options=[
                        {'label':'All Industries',
                            'value':'Total, all industries'},
                        {'label':'Goods-producing sector',
                            'value':'Goods-producing sector'},
                        {'label':'Agriculture',
                            'value':'Agriculture [111-112, 1100, 1151-1152]'},
                        {'label':'Forestry, Fishing, Mining, Quarring, Oil and Gas',
                            'value':'Forestry, fishing, mining, quarrying, oil and gas [21, 113-114, 1153, 2100]'},
                        {'label':'Forestry, Logging and Support activities',
                            'value':'Forestry and logging and support activities for forestry [113, 1153]'},
                        {'label':'Fishing, Hunting and Trapping',
                            'value':'Fishing, hunting and trapping [114]'},
                        {'label':'Mining, Quarrying, and Oil and Gas extraction',
                            'value':'Mining, quarrying, and oil and gas extraction [21, 2100]'},
                        {'label':'Utilities',
                            'value':'Utilities [22]'},
                        {'label':'Construction',
                            'value':'Construction [23]'},
                        {'label':'Manufacturing',
                            'value':'Manufacturing [31-33]'},
                        {'label':'Durables',
                            'value':'Durables [321, 327, 331-339]'},
                        {'label':'Non-durabless',
                            'value':'Non-durables [311-316, 322-326]'},
                        {'label':'Services-producing sector',
                            'value':'Services-producing sector'},
                        {'label':'Wholesale and retail trade',
                            'value':'Wholesale and retail trade [41, 44-45]'},
                        {'label':'Wholesale trade',
                            'value':'Wholesale trade [41]'},
                        {'label':'Retail trade',
                            'value':'Retail trade [44-45]'},
                        {'label':'Transportation and warehousing',
                            'value':'Transportation and warehousing [48-49]'},
                        {'label':'Professional, scientific and technical services',
                            'value':'Professional, scientific and technical services [54]'},
                        {'label':'Finance, insurance, real estate, rental and leasing',
                            'value':'Finance, insurance, real estate, rental and leasing [52, 53]'},
                        {'label':'Finance and insurance',
                            'value':'Finance and insurance [52]'},
                        {'label':'Real estate and rental and leasing',
                            'value':'Real estate and rental and leasing [53]'},
                        {'label':'Business, building and other support services',
                            'value':'Business, building and other support services [55, 56]'},
                        {'label':'Educational services',
                            'value':'Educational services [61]'},
                        {'label':'Health care and social assistance',
                            'value':'Health care and social assistance [62]'},
                        {'label':'Information, culture and recreation',
                            'value':'Information, culture and recreation [51, 71]'},
                        {'label':'Accommodation and food services',
                            'value':'Accommodation and food services [72]'},
                        {'label':'Other services (except public administration)',
                            'value':'Other services (except public administration) [81]'},
                        {'label':'Public administration',
                            'value':'Public administration [91]'},
                        {'label':'Unclassified industries',
                            'value':'Unclassified industries'}
                    ],
                    multi=False,
                    value='Total, all industries',

                ),
            width=3),

            dbc.Col(
                dcc.Dropdown(
                    id='sclt_age',
                    value = '25 to 54 years',
                    options=[{'label':x, 'value':x}
                            for x in sorted(df['Age group'].unique())]
                ),
            width=3),

            dbc.Col(
                dcc.Dropdown(
                    id='sclt_prov',
                    options=[
                        {'label':'Alberta', 'value':'Alberta'},
                        {'label':'Newfoundland and Labrador', 'value':'Newfoundland and Labrador'},
                        {'label':'Prince Edward Island', 'value':'Prince Edward Island'},
                        {'label':'Nova Scotia', 'value':'Nova Scotia'},
                        {'label':'New Brunswick', 'value':'New Brunswick'},
                        {'label':'Quebec', 'value':'Quebec'},
                        {'label':'Ontario', 'value':'Ontario'},
                        {'label':'Manitoba', 'value':'Manitoba'},
                        {'label':'Saskatchewan', 'value':'Saskatchewan'},
                        {'label':'British Columbia', 'value':'British Columbia'}],
                    multi=False,
                    value='Alberta'
                ),
            width=3),

            dbc.Col(
                dcc.Dropdown(
                    id='sclt_labour',
                    options=[
                        {'label':'Unemployed', 'value':'Unemployment'},
                        {'label':'Part-time employment', 'value':'Part-time employment'},
                        {'label':'Full-time employment', 'value':'Full-time employment'}],
                    multi=False,
                    value='Full-time employment',
                    className='body'
                ),
            width=3),
        ]),

    dbc.Row(
        html.Br()
    ),

    dbc.Row(
        dbc.Col(
            dcc.Slider(
                min=1976,
                max=2021,
                marks={
                    1976: '1976',
                    1980: '1980',
                    1985: '1985',
                    1990: '1990',
                    1995: '1995',
                    2000: '2000',
                    2005: '2005',
                    2010: '2010',
                    2015: '2015',
                    2020: '2020',
                    2022: '2022'
                },
                dots=True,
                step = 1,
#                step={i: f'Label {i}' if i == 1 else str(i) for i in range(1976, 2022)},
                tooltip={"placement": "bottom", "always_visible": True},
                value=2020,
                id='year-slider'
            ),
        xs=12, sm=12, md=12, lg=12, xl=12),
    ),

    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id='bar-chart',
                figure={}
            ),
        style={"height": "10vh"},
        align="start",
        xs=12, sm=12, md=12, lg=4, xl=4),

        dbc.Col(
            dcc.Graph(
                id='cad_job_map',
                figure={},
            ),
        style={"height": "100%"},
        align="end",
        xs=12, sm=12, md=12, lg=8, xl=8),
    ],className="h-75")


    # dcc.Markdown('''
    #     >
    #     >Any society that fails to harness the energy and creativity of its
    #     >women is at a huge disadvantage in the modern world.
    #     >
    #     Tian Wei
    # '''),



], fluid=True)

#-------------------------------------------------------------------------------
# Callback

@app.callback(
#    [Output(component_id='my_output', component_property='children'),
    [Output(component_id='cad_job_map', component_property='figure'),
    Output(component_id='bar-chart', component_property='figure')],
    [Input(component_id='sclt_job', component_property='value'),
    Input(component_id='sclt_age', component_property='value'),
    Input(component_id='year-slider', component_property='value'),
    Input(component_id='sclt_prov', component_property='value'),
    Input(component_id='sclt_labour', component_property='value')])

def update_map(job,age,year,prov,labour):
    print([job, year, age, labour])
    print(type([job, year, age, labour]))

    dff = df.copy()
    dff = dff[dff["REF_DATE"] == year]
    dff = dff[dff['Age group'] == age]
    dff = dff[dff['North American Industry Classification System (NAICS)']==job]

    df3 = df.copy()
    df3 = df3[df3['Age group'] == age]
    df3 = df3[df3['North American Industry Classification System (NAICS)']==job]
    df3 = df3[df3['GEO'] == prov]
    df3 = df3[df3['Labour force characteristics'] == labour]

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html

    fig = px.choropleth_mapbox(
        dff,
        geojson = geojson,
        featureidkey="properties.prov_name_en",
        locations='GEO',
        color='Percent_F',
        opacity=0.5,
        color_continuous_scale=[
            [0, 'rgb(2, 10, 250)'],# bottom of scale
            [0.50, 'rgb(196, 157, 250)'],
            [1, 'rgb(250, 2, 163)']],# Top of scale

        template='seaborn',
        labels = {'Percent_F':'% of Females'},
        center = {'lat':54.1304, 'lon':-97.3468},
        zoom= 2.5,
        color_continuous_midpoint=50,
        range_color=[100,0],
        mapbox_style='light',
        title = f'''The percentage of females in industry by province in {year}'''

    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(autosize=True)
#    fig.update_layout(margin={"r":2,"t":2,"l":2,"b":2})

# https://plotly.com/python-api-reference/generated/plotly.express.bar

    fig2 = px.bar(
        df3,
        x ='Percent',
        y = 'REF_DATE',
        hover_data=['REF_DATE','Age group',
            'North American Industry Classification System (NAICS)','GEO',
            'Labour force characteristics'],
        labels= {'REF_DATE':'Year ',
                'Sex': 'Sex ',
                'Percent':'Percent ',
                'North American Industry Classification System (NAICS)': 'NAICS ',
                'REF_DATE':'Year ',
                'Labour force characteristics':'Employment ',
                'GEO':'Province ',
                'Age group': 'Age group '},
        color_discrete_map = {'Male':'rgb(15, 105, 250)', 'Female':'rgb(247, 87, 226)'},
        color='Sex',
        facet_col_spacing = 0,
        orientation = 'h',
        range_x = [0,100],
        title = f'Male vs Female in {prov}'
    )

    return fig, fig2

if __name__ == '__main__':
    server.run(debug=True)
