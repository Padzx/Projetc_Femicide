import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Carregue o DataFrame a partir do arquivo CSV
file = 'df_fem.csv'
df_fem_copy = pd.read_csv(file)

app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.H1("Análise Sobre o Feminicídio em São Paulo (2015-2022)", style={'text-align':'center',
                                                               'font-family': 
                                                               'Arial, sans-serif', 
                                                               'font-size': '30px'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[
            {'label': str(year), 'value': year} for year in df_fem_copy['ANO_BO'].unique()
        ],
        value=df_fem_copy['ANO_BO'].max(),
        multi=False
    ),
    
    html.Div([
        html.Div([
            dcc.Graph(id='pie-chart', 
                      style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='bar-chart', style={'width': '48%', 'display': 'inline-block'}),
        ]),
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='line-chart', style={'width': '48%', 'display': 'inline-block',}),
            dcc.Graph(id='bar-municipios', style={'width':'48%', 'display': 'inline-block',}),
        ]),
    ]),

    html.Div([
        dcc.Graph(id='donut-chart', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='bar-media-idade', style={'width': '48%', 'display': 'inline-block'}),
    ]),
])

# Função para criar gráfico de rosca (donut chart) com o total de mortes
def create_donut_chart(total_deaths):
    fig = px.pie(
        names=['Mortes'],
        values=[total_deaths],
        hole=0.6,  # Especifica o tamanho do "buraco" no meio do gráfico para criar o efeito de rosca
        title='Total de Mortes em Todos os Anos',
        color_discrete_sequence= ['#808080']
    )
    return fig

# Função para calcular a média de idade por ano
def calcular_media_idade_por_ano(dataframe):
    media_idade = dataframe.groupby('ANO_BO')['IDADE_PESSOA'].mean().reset_index()
    return media_idade

# Callback para atualizar os gráficos
@app.callback(
    [Output('pie-chart', 'figure'), Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'), Output('donut-chart', 'figure'), Output('bar-media-idade', 'figure'),
     Output('bar-municipios', 'figure')],
    [Input('year-dropdown', 'value')]
)
def update_charts(selected_year):
    filtered_df = df_fem_copy[df_fem_copy['ANO_BO'] == selected_year]

    # Atualize o gráfico de pizza
    fig_pie = px.pie(filtered_df, names='COR_PELE', values='Nº DE VÍT HD',
                     title=f'Mortes por Cor de Pele em {selected_year}',
                     color_discrete_sequence=['#E3C097','#CD853F','#50301E','#E9D581','black','red'])

    # Organize as profissões em ordem decrescente com números somados e limite a 10 profissões
    profissoes_mais_mortes = (
        filtered_df.groupby('PROFISSAO')['Nº DE VÍT HD']
        .sum()
        .reset_index()
        .sort_values(by='Nº DE VÍT HD', ascending=False)
        .head(10)  # Limita às 10 profissões com mais mortes
    )

    # Inverta a ordenação para começar no lado esquerdo
    fig_bar = px.bar(
        profissoes_mais_mortes[::-1], x='Nº DE VÍT HD', y='PROFISSAO',
        title=f'Profissões com Mais Mortes em {selected_year}',
        labels={'Nº DE VÍT HD': 'Número de Mortes'},
        color_discrete_sequence=['#8A7C9B']
    )

    # Agrupe e acumule os valores de morte por município de acordo com o ano selecionado
    municipios_mais_mortes = (
        df_fem_copy[df_fem_copy['ANO_BO'] == selected_year]
        .groupby('MUNICIPIO_CIRCUNSCRICAO')['Nº DE VÍT HD']
        .sum()
        .reset_index()
        .sort_values('Nº DE VÍT HD', ascending=False)
        .head(10)  # Limita aos 10 municípios com mais mortes
    )

    fig_bar_delegacias = px.bar(
        municipios_mais_mortes, x='MUNICIPIO_CIRCUNSCRICAO', y='Nº DE VÍT HD',
        title=f'Municípios com Mais Mortes de Feminicídio em {selected_year}',
        labels={'Nº DE VÍT HD': 'Número de Mortes'},
     
    )

    # Agrupe e acumule os valores de morte por mês de acordo com o ano selecionado
    mortes_por_mes = (
        df_fem_copy[df_fem_copy['ANO_BO'] == selected_year]
        .groupby('MÊS ESTATISTICA')['Nº DE VÍT HD']
        .sum()
        .reset_index()
    )

    # Defina a ordem dos meses
    ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio',
                      'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mortes_por_mes['MÊS ESTATISTICA'] = pd.Categorical(mortes_por_mes['MÊS ESTATISTICA'],
                                                       categories=ordered_months, ordered=True)
    

    # Classifique o DataFrame com base na ordem dos meses
    mortes_por_mes = mortes_por_mes.sort_values('MÊS ESTATISTICA')

    fig_line = px.line(
        mortes_por_mes, x='MÊS ESTATISTICA', y='Nº DE VÍT HD',
        title=f'Mortes por Mês em {selected_year}',
        markers=True,
        color_discrete_sequence=['#FF6961']
    )

    # Calcule o número total de mortes em todos os anos
    total_deaths = df_fem_copy['Nº DE VÍT HD'].sum()

    # Crie o gráfico de rosca (donut chart) com o total de mortes
    fig_donut = create_donut_chart(total_deaths)

    # Calcule a média de idade por ano
    media_idade_por_ano = calcular_media_idade_por_ano(df_fem_copy)

    # Crie um gráfico de barras para a média de idade por ano
    fig_bar_media_idade = px.bar(media_idade_por_ano, x='ANO_BO', y='IDADE_PESSOA', title='Média de Idade por Ano',
                                 color_discrete_sequence=['#534d85'])

    # Agrupe e acumule os valores de morte por município para o gráfico de barras de municípios
    municipios_mortes = (
        df_fem_copy[df_fem_copy['ANO_BO'] == selected_year]
        .groupby('MUNICIPIO_CIRCUNSCRICAO')['Nº DE VÍT HD']
        .sum()
        .reset_index()
        .sort_values(by='Nº DE VÍT HD', ascending=False)
    )

    # Limite aos 10 municípios com mais mortes
    municipios_mortes = municipios_mortes.head(10)

    fig_bar_municipios = px.bar(
        municipios_mortes[::-1], x='Nº DE VÍT HD', y='MUNICIPIO_CIRCUNSCRICAO',
        title=f'Municípios com Mais Mortes em {selected_year}',
        labels={'Nº DE VÍT HD': 'Número de Mortes'},
        color_discrete_sequence=['#003A4D']
    )

    return fig_pie, fig_bar, fig_line, fig_donut, fig_bar_media_idade, fig_bar_municipios

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
