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
    html.H3('Filtres sur les lycées', className='text-white mt-3'),
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
    html.Div('Spécialité', className='mt-3'),
    dcc.Dropdown(
        id='specialite',
        options=[
            {'label': 'Toutes séries', 'value': 'Toutes series'},
            {'label': 'L', 'value': 'L'},
            {'label': 'ES', 'value': 'ES'},
            {'label': 'S', 'value': 'S'},
            {'label': 'Gnle', 'value': 'Gnle'},
            {'label': 'STI2D', 'value': 'STI2D'},
            {'label': 'STD2A', 'value': 'STD2A'},
            {'label': 'STMG', 'value': 'STMG'},
            {'label': 'STL', 'value': 'STL'},
            {'label': 'ST2S', 'value': 'ST2S'},
            {'label': 'S2TMD', 'value': 'S2TMD'},
            {'label': 'STHR', 'value': 'STHR'}
        ],
        placeholder='Choisir une spécialité'
    ),
    html.Div("Nom de l'établissement", className='mt-3'),
    dcc.Dropdown(
        id='uai',
        options=[{'label': etablissement, 'value': etablissement} for etablissement in all_etablissement],
        placeholder='Choisir un établissement'
    ),
    html.H3("Filtres du Barchart", className='mt-5'),
    html.Div("Année", className='mt-3'),
    dcc.Dropdown(
        id='annee',
        options=[{'label': str(annee), 'value': annee} for annee in sorted(dataframe_merged['Annee'].unique())],
        placeholder='Choisir une année'
    )
])

# Contenu principal avec les différents graphiques
content = html.Div([
    dbc.Row([
        dcc.Graph(id='map'),
        dcc.Graph(id='barchart')
    ]),
])

# Callback pour mise à jour de la carte
@app.callback(
    Output('map', 'figure'),
    Input('academie', 'value'),
    Input('department', 'value'),
    Input('city', 'value'),
    Input('specialite', 'value'),
    Input('uai', 'value'),
)
def update_map(academie, department, city, specialite, uai):
    """
    Affiche la carte des lycées en fonction des filtres
    """
    
    map_dataframe = dataframe_merged.copy()

    if academie:
        map_dataframe = map_dataframe[map_dataframe['Academie'] == academie]
    
    if department:
        map_dataframe = map_dataframe[map_dataframe['Departement'] == department]

    if city:
        map_dataframe = map_dataframe[map_dataframe['Nom_commune'] == city]
    
    if specialite:
        map_dataframe = map_dataframe[map_dataframe[f'Taux de reussite - {specialite}'] > 0]

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

# Callback pour mise à jour du barchart
@app.callback(
    Output('barchart', 'figure'),
    Input('uai', 'value'),
    Input('annee', 'value')
)
def update_barchart(selected_uai, selected_year):
    """
    Affiche le taux de réussite par série pour un établissement donné
    """

    if not selected_uai:
        return px.bar(title="Veuillez sélectionner un établissement")

    dataframe_taux_reussite = dataframe_merged[dataframe_merged['Nom_etablissement'] == selected_uai]

    if selected_year:
        dataframe_taux_reussite = dataframe_taux_reussite[dataframe_taux_reussite['Annee'] == selected_year]

    if dataframe_taux_reussite.empty:
        return px.bar(title="Aucune donnée disponible pour cet établissement")

    dataframe_taux_reussite = dataframe_taux_reussite.drop_duplicates(subset=['Annee'])

    taux_data = {
        "Catégorie": ["Toutes séries", "L", "ES", "S", "Gnle", "STI2D", "STD2A", "STMG", "STL", "ST2S", "S2TMD", "STHR"],
        "Taux de réussite": [
            dataframe_taux_reussite.iloc[0]['Taux de reussite - Toutes series'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - L'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - ES'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - S'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - Gnle'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - STI2D'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - STD2A'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - STMG'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - STL'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - ST2S'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - S2TMD'],
            dataframe_taux_reussite.iloc[0]['Taux de reussite - STHR']
        ]
    }

    taux_reussite_dataframe = pd.DataFrame(taux_data)

    fig = px.bar(
        taux_reussite_dataframe,
        x='Catégorie',
        y='Taux de réussite',
        text='Taux de réussite',
        title=f"Taux de réussite - {selected_uai} ({selected_year if selected_year else 'toutes années'})"
    )
    
    fig.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='inside'
    )
    
    fig.update_layout(
        yaxis_range=[0, 100],
        height=600
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
    Input('city', 'value'),
    Input('specialite', 'value')
)
def update_dropdowns(selected_academie, selected_dept, selected_city, selected_specialite):
    """
    Met à jour les dropdowns en fonction des différents filtres
    """

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

    # Filtrage des spécialités
    if selected_specialite:
        colonne_specialite = f'Taux de reussite - {selected_specialite}'
        if colonne_specialite in dataframe_dropdowns.columns:
            dataframe_dropdowns = dataframe_dropdowns[dataframe_dropdowns[colonne_specialite].notna() & (dataframe_dropdowns[colonne_specialite] > 0)]

    # Dropdown établissements final
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