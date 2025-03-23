import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

annuaire_education_dataframe = pd.read_csv('data/fr-en-annuaire-education.csv', sep=';')
indicateur_resultat_lycee_dataframe = pd.read_csv('data/fr-en-indicateurs-de-resultat-des-lycees-gt_v2.csv', sep=';')

dataframe_merged = pd.merge(annuaire_education_dataframe, indicateur_resultat_lycee_dataframe, left_on='Identifiant_de_l_etablissement', right_on='UAI')
dataframe_merged = dataframe_merged[dataframe_merged['Region'] == 'ILE-DE-FRANCE']
dataframe_merged = dataframe_merged[dataframe_merged['Type_etablissement'] == 'Lycée']

all_etablissement = sorted(dataframe_merged['Nom_etablissement'].unique())
all_commune = sorted(dataframe_merged['Nom_commune'].unique())

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
sidebar = html.Div([
    html.H2('Filtres', className='text-white'),
    html.Div('Département'),
    dcc.Dropdown(
        id='department',
        # options=,
        # value=
    ),
    html.Div('Nom de commune', className='mt-3'),
    dcc.Dropdown(
        id='city',
        options=all_commune,
        value=all_commune
    ),
    html.Div('Nom de l\'établissement', className='mt-3'),
    dcc.Dropdown(
        id='uai',
        options=all_etablissement,
        value=all_etablissement
    )
])

content = html.Div([
    dbc.Row([
        dcc.Graph(id='map'),
        dcc.Graph(id='barchart'),
        dcc.Graph(id='pie_year')
    ]),
])

@app.callback(
    Output('map', 'figure'),
    Input('uai', 'value'),
    Input('city', 'value')
)
def update_map(uai, city):
    map_dataframe = dataframe_merged[(dataframe_merged['Nom_etablissement'] == uai) & (dataframe_merged['Nom_commune'] == city)]
    fig = px.scatter_mapbox(
        map_dataframe,
        lat='latitude',
        lon='longitude',
        zoom=12,
        height=600
        # hover_data=['UAI', 'Adresse_1', 'Adresse_3']
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig

app.layout = dbc.Container([
    dbc.Row(
        [
            dbc.Col(sidebar, width=3, className='bg-success'),
            dbc.Col(content, width=9)
        ],
        style={"height": "100vh"}
    ),
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)