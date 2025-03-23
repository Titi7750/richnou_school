import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Chargement des données
annuaire_education_dataframe = pd.read_csv('data/fr-en-annuaire-education.csv', sep=';')
indicateur_resultat_lycee_dataframe = pd.read_csv('data/fr-en-indicateurs-de-resultat-des-lycees-gt_v2.csv', sep=';')

# Fusion et filtrage initial
dataframe_merged = pd.merge(annuaire_education_dataframe, indicateur_resultat_lycee_dataframe, left_on='Identifiant_de_l_etablissement', right_on='UAI')
dataframe_merged = dataframe_merged[dataframe_merged['Region'] == 'ILE-DE-FRANCE']
dataframe_merged = dataframe_merged[dataframe_merged['Type_etablissement'] == 'Lycée']

# Valeurs uniques pour dropdowns
all_academie = sorted(dataframe_merged['Academie'].unique())
all_departement = sorted(dataframe_merged['Departement'].unique())
all_etablissement = sorted(dataframe_merged['Nom_etablissement'].unique())
all_commune = sorted(dataframe_merged['Nom_commune'].unique())

# Initialisation de l'app
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

# Sidebar avec les filtres
sidebar = html.Div([
    html.H2('Filtres', className='text-white mt-3'),
    html.Div('Académie'),
    dcc.Dropdown(
        id='academie',
        options=[{'label': academie, 'value': academie} for academie in all_academie],
        placeholder='Choisir une académie'
    ),
    html.Div('Département', className='mt-3'),
    dcc.Dropdown(
        id='department',
        options=[{'label': departement, 'value': departement} for departement in all_departement],
        placeholder='Choisir un département'
    ),
    html.Div('Nom de commune', className='mt-3'),
    dcc.Dropdown(
        id='city',
        options=[{'label': commune, 'value': commune} for commune in all_commune],
        placeholder='Choisir une commune'
    ),
    html.Div("Nom de l'établissement", className='mt-3'),
    dcc.Dropdown(
        id='uai',
        options=[{'label': etablissement, 'value': etablissement} for etablissement in all_etablissement],
        placeholder='Choisir un établissement'
    )
])

# Contenu principal avec les différents graphiques
content = html.Div([
    dbc.Row([
        dcc.Graph(id='map'),
        dcc.Graph(id='barchart'),
        dcc.Graph(id='pie_year')
    ]),
])

# Callback pour mise à jour de la carte
@app.callback(
    Output('map', 'figure'),
    Input('academie', 'value'),
    Input('department', 'value'),
    Input('city', 'value'),
    Input('uai', 'value'),
)
def update_map(academie, department, city, uai):
    map_dataframe = dataframe_merged.copy()

    if academie:
        map_dataframe = map_dataframe[map_dataframe['Academie'] == academie]
    
    if department:
        map_dataframe = map_dataframe[map_dataframe['Departement'] == department]

    if city:
        map_dataframe = map_dataframe[map_dataframe['Nom_commune'] == city]

    if uai:
        map_dataframe = map_dataframe[map_dataframe['Nom_etablissement'] == uai]

    fig = px.scatter_mapbox(
        map_dataframe,
        lat='latitude',
        lon='longitude',
        zoom=10,
        height=600,
        hover_name='Nom_etablissement'
    )
    fig.update_layout(mapbox_style="open-street-map")

    if not map_dataframe.empty:
        fig.update_layout(
            mapbox_center={
                "lat": map_dataframe['latitude'].mean(),
                "lon": map_dataframe['longitude'].mean()
            }
        )

    return fig

# Callback pour mise à jour des dropdowns
@app.callback(
    Output('department', 'options'),
    Output('department', 'value'),
    Output('city', 'options'),
    Output('city', 'value'),
    Output('uai', 'options'),
    Output('uai', 'value'),
    Input('academie', 'value'),
    Input('department', 'value'),
    Input('city', 'value')
)
def update_dropdowns(selected_academie, selected_dept, selected_city):
    dataframe_dropdowns = dataframe_merged.copy()

    if selected_academie:
        dataframe_dropdowns = dataframe_dropdowns[dataframe_dropdowns['Academie'] == selected_academie]

    # Départements filtrés par académie
    departements = sorted(dataframe_dropdowns['Departement'].unique())
    dept_options = [{'label': departement, 'value': departement} for departement in departements]
    updated_dept = selected_dept if selected_dept in departements else None

    if updated_dept:
        dataframe_dropdowns = dataframe_dropdowns[dataframe_dropdowns['Departement'] == updated_dept]

    # Communes filtrées par académie + département
    communes = sorted(dataframe_dropdowns['Nom_commune'].unique())
    city_options = [{'label': commune, 'value': commune} for commune in communes]
    updated_city = selected_city if selected_city in communes else None

    if updated_city:
        dataframe_dropdowns = dataframe_dropdowns[dataframe_dropdowns['Nom_commune'] == updated_city]

    # Établissements filtrés
    etabs = sorted(dataframe_dropdowns['Nom_etablissement'].unique())
    uai_options = [{'label': etablissement, 'value': etablissement} for etablissement in etabs]

    return dept_options, updated_dept, city_options, updated_city, uai_options, None

# Layout final
app.layout = dbc.Container([
    dbc.Row(
        [
            dbc.Col(sidebar, width=3, className='bg-success'),
            dbc.Col(content, width=9)
        ],
        style={"height": "100vh"}
    ),
], fluid=True)

# Lancement
if __name__ == '__main__':
    app.run_server(debug=True)