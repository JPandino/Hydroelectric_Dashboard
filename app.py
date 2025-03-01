from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from dash_bootstrap_templates import ThemeSwitchAIO

FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
app = Dash(__name__, external_stylesheets=FONT_AWESOME)
app.scripts.config.serve_locally = True
server = app.server
            
# ========== Styles ============ #
tab_card = {'height': '100%'}
main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor": "top",
               "y": 0.8,
               "xanchor": "left",
               "x": 0,
               "title": {"text": None},
               "font": {"color": "white"},
               "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l": 10, "r": 10, "t": 10, "b": 10}
}
config_graph = {"displayModeBar": False, "showTips": False}
color_escale = [
    #"#02ABED",
    "#4497E6",
    "#6E80D7",
    "#8D65BE",
    "#A2489B",
    "#AB2772",
    "#FEA195",
    "#EF889B",
    "#D574A6",
    "#AD68B2",
    "#7463B9",
    "#005FB6"]

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

# ===== Reading Data n Variables ====== #
# Data
df_result = pd.read_csv('var_decisao_UHE.csv')
#df_pld = pd.read_csv('cenarios_pld.csv')
data = pd.read_csv(r"C:\Users\Pesquisador\PycharmProjects\Web_APP_2.1\dados\base_dados\dados_teste_app.csv")

# Variables
steps = 168
uhe = pd.read_csv('dic.csv')
unit = eval(uhe["unit"][0])
e_q = eval(uhe["e_q"][0])
e_q_list = list(e_q.values())
k1 = uhe["k1"][0]
k2 = uhe["k2"][0]
M_acl = uhe["M_acl"][0]
P_acl = uhe["P_acl"][0]

"""uhe = {"Nome": "Usina Teste",
        "unit": ["A", "B", "C", "D"],
        "vmax": 5779,
        "vmin": 1974,
        "qsmax": 10030,
        "qmax": {"A": 372, "B": 372, "C": 372, "D": 372},
        "qmin": {"A": 50, "B": 50, "C": 50, "D": 50},
        "e_q": {"0": 1.15*0.95, "1": 1.15*0.98, "2": 1.15*0.95, "3": 1.15*0.98},
        "rate_q": 0.8,
        "C": 0.0036,
        "k1": 8.00,
        "k2": 1.,
        "k3": 1.,
        "M_acl": 300.0,
        "P_acl": 141.58}
"""
#VI = [3876.5]  #hm³
#VF = [3876.5]  #hm³

# ===== Manipulation Data ====== #
eixo_x = np.arange(steps)

turbine_list = [eval(sublista) for sublista in df_result["q"].to_list()]
turbine_unit = [[sublista[i] for sublista in turbine_list] for i in range(len(unit))]

stop_list = [eval(sublista) for sublista in df_result["i_off"].to_list()]
stop_unit = [[sublista[i] for sublista in stop_list] for i in range(len(unit))]
cost_stop = sum([sum(x) for x in zip(*stop_unit)])*k2

start_list = [eval(sublista) for sublista in df_result["i_st"].to_list()]
start_unit = [[sublista[i] for sublista in start_list] for i in range(len(unit))]
cost_start = sum([sum(x) for x in zip(*start_unit)])*k2

def replace_none(list):
    new_list = [None if value == 0 else value for value in list]

    return new_list

new_start_unit = []
for i, sublist in enumerate(start_unit):
    new_list = replace_none(sublist)
    new_start_unit.append(new_list)

energy_unit = [[turbine_unit[i][t] * e_q_list[i] for t in range(steps)] for i in range(len(unit))]
energy_total = [sum(x) for x in zip(*energy_unit)]

operation_list = [eval(sublista) for sublista in df_result["i_q"].to_list()]

#pld = df_pld["PLD"].tolist()
#pld = [pld[i:i + steps] for i in range(0, len(pld), steps)][0]
pld = data["affluence"].tolist()
profit_spot = [(energy_total[t] - M_acl) * pld[t] for t in range(steps)]
profit_acl = np.full(steps, M_acl * P_acl)
df_new = pd.DataFrame(list(zip(pld, profit_spot, profit_acl)), columns=['pld', 'profit_spot', 'profit_acl'])
total_profit = sum(df_new["profit_spot"]) + sum(df_new["profit_acl"])

cost_OM = sum(energy_total)*k1
cost_start_stop = cost_start + cost_stop

# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenamento de dataset
    # dcc.Store(id='dataset', data=df_store),

    # Layout
    # Row 1
    dbc.Row([
        # Column 1
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Legend("Optimizer CGH")
                        ], sm=8),
                        dbc.Col([
                            html.I(className='fa fa-tint', style={'font-size': '300%'})
                        ], sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])
                        ])
                    ], style={'margin-top': '10px'}),
                    dbc.Row([
                        html.H4("EBE"),
                        dbc.Button("Retornar", href="https://palevioletred-seahorse-893779.hostingersite.com", style={'width': '60%', 'margin-left': '10px'})
                    ], style={'margin-top': '30px'}),
                    dbc.Row([
                        html.P("Solicitar relatório semanal a partir dos dados fornecidos e dos resultados da otimização"),
                        dbc.Button("Relatório", href="https://palevioletred-seahorse-893779.hostingersite.com/confirmacao-relatorio-semanal/",
                                   target="_blank", style={'width': '60%'})
                    ], style={'position': 'absolute', 'justify-content': 'center', 'bottom': '20px', 'width': '95%'})
                ])
            ], style=tab_card)
        ], sm=4, lg=2),
        # Column 2
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col(
                            html.H5('')
                        )
                    ),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph1', className='dbc', config=config_graph)
                        ], sm=12),
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=5),
        # Column 3
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph3', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph4', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ], className='g-2 my-auto', style={'margin-top': '7px'})
        ], sm=12, lg=5)

    ], className='g-2 my-auto', style={'margin-top': '7px'}),
    # Row 2
    dbc.Row([
        # Column 1
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph0', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph5', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ], className='g-2 my-auto', style={'margin-top': '7px'}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph6', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ], className='g-2 my-auto', style={'margin-top': '7px'})
        ], sm=12, lg=3),


        # Column 2
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col(
                            html.H5('')
                        )
                    ),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph7', className='dbc', config=config_graph)
                        ], sm=12),
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=3),
        # Column 3
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col(
                            html.H5('')
                        )
                    ),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph8', className='dbc', config=config_graph)
                        ], sm=12),
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=6)

    ], className='g-2 my-auto', style={'margin-top': '7px'})

], fluid=True, style={'height': '100vh'})

# ======== Callbacks ========== #
# Card 1
@app.callback(
    Output('graph1', 'figure'),
    #Output('graph2', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card1(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 1: Vazão turbinada n Start/stop por UG
    #color_escale = ["#00ACEB", "blue", "#00B140", "#007748"]

    fig1 = make_subplots(rows=3, cols=1, row_heights=[0.6, 0.2, 0.2], shared_xaxes=True, vertical_spacing=0.04)

    for i, val in enumerate(turbine_unit):
        fig1.add_trace(go.Bar(x=eixo_x, y=val,
                              name=f"turbine_UG{i}", marker={'color': color_escale[i]}), row=1, col=1)

    for i, val in enumerate(start_unit):
        fig1.add_trace(go.Bar(x=eixo_x, y=val,
                              name=f"start_UG{i}", marker={'color': color_escale[i]}), row=2, col=1)

    for i, val in enumerate(stop_unit):
        fig1.add_trace(go.Bar(x=eixo_x, y=val,
                              name=f"stop_UG{i}", marker={'color': color_escale[i]}), row=3, col=1)

    # Update xaxis properties
    fig1.update_xaxes(title_text="", row=1, col=1)
    fig1.update_xaxes(title_text="", showgrid=False, row=2, col=1)
    fig1.update_xaxes(title_text="<b>Horizonte de Planejamento</b> (horário)", showgrid=False, row=3, col=1)

    # Update yaxis properties
    fig1.update_yaxes(title_text="<b>Vazão</b> (m³/s)", row=1, col=1)
    fig1.update_yaxes(title_text="<b>Partidas</b>", showticklabels=False, row=2, col=1)
    fig1.update_yaxes(title_text="<b>Paradas</b>", showticklabels=False, row=3, col=1)

    fig1.update_layout(barmode='stack')
    fig1.update_layout(main_config, height=500, template=template, showlegend=False)

    return fig1

# Card 2
@app.callback(
    Output('graph3', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card2(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 3: Geração de energia por UG
    fig3 = go.Figure()

    for i, val in enumerate(energy_unit):
        fig3.add_trace(go.Bar(x=eixo_x, y=val, name=f"energy_UG{i}", marker={'color': color_escale[i]}))

    fig3.update_xaxes(title_text="<b>Horizonte de Planejamento</b> (horário)")
    fig3.update_yaxes(title_text="<b>Energia</b> (MWh)")
    fig3.update_layout(barmode='stack')
    fig3.update_layout(main_config, height=250, template=template, showlegend=False)

    return fig3

# Card 3
@app.callback(
    Output('graph4', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card3(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 4: Volumes e vertimentos
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(go.Scatter(x=eixo_x, y=df_result["v"], name="volume", marker={'color': color_escale[0]}),secondary_y=False)
    fig4.add_trace(go.Scatter(x=eixo_x, y=df_result["qs"], name="vertimento", marker={'color': color_escale[4]}),secondary_y=True)
    fig4.update_xaxes(title_text="Horizonte de Planejamento (horário)")
    fig4.update_yaxes(title_text="<b>Volume</b> (hm³)", secondary_y=False)
    fig4.update_yaxes(title_text="<b>Vertimento</b> (m³/s)", secondary_y=True)
    fig4.update_layout(main_config, height=250, template=template, showlegend=False)

    return fig4

# Card 0
@app.callback(
    Output('graph0', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card0(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 0: Indicator
    fig0 = go.Figure()
    fig0.add_trace(go.Indicator(
        mode="number",
        value=round(k2, 2),
        title={"text": "<span style='font-size:2.5em;color:gray'>Custo de Partida/Parada Mensurado</span>"},
        number={'prefix': "R$ ", 'font': {'size': 20}},
        domain={'x': [0, 1], 'y': [0, 0.5]}))
    fig0.update_layout(main_config, height=50, template=template, showlegend=False)

    return fig0

# Card 4
@app.callback(
    Output('graph5', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card4(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 5: Indicators
    fig5 = go.Figure()
    fig5.add_trace(go.Indicator(
        mode="number",
        value=round(cost_OM, 2),
        title={"text": "<span style='font-size:2.5em;color:red'>Custos - O&M</span>"},
        number={'prefix': "R$ ", 'font': {'size': 25}},
        domain={'x': [0, 1], 'y': [0.5, 0.9]}))
    fig5.add_trace(go.Indicator(
        mode="number",
        value=round(cost_start_stop, 2),
        title={"text": "<span style='font-size:2.5em;color:red'>Custo - Partidas e Paradas</span>"},
        number={'prefix': "R$ ", 'font': {'size': 25}},
        domain={'x': [0, 1], 'y': [0, 0.1]}))
    fig5.update_layout(main_config, height=125, template=template, showlegend=False)

    return fig5

# Card 5
@app.callback(
    Output('graph6', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card5(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 6: Indicators
    fig6 = go.Figure()
    fig6.add_trace(go.Indicator(
        mode='number',
        value=total_profit,
        title={"text": "<span style='font-size:2.5em;color:green'>Receita Total</span><br>"},
        number={'prefix': "R$ ", 'font': {'size': 30}},
        domain={'x': [0, 1], 'y': [0.5, 0.9]}))
    fig6.add_trace(go.Indicator(
        mode='number',
        value=sum(energy_total),
        title={"text": "<span style='font-size:2.5em;color:orange'>Energia Total</span><br>"},
        number={"valueformat": ".1f", "suffix": " MWh", 'font': {'size': 30}},
        domain={'x': [0, 1], 'y': [0, 0.2]}))
    fig6.update_layout(main_config, height=150, template=template, showlegend=False)

    return fig6

# Card 6
@app.callback(
    Output('graph7', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card6(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 7: Tempo em operação por UG
    time_turbine = [0.0] * len(operation_list[0])
    for sublista in operation_list:
        for i, valor in enumerate(sublista):
            time_turbine[i] += valor

    total_time = sum(time_turbine)
    labels = [f"UG{i}" for i in range(len(unit))]

    fig7 = go.Figure()
    fig7.add_trace(go.Pie(labels=labels, values=time_turbine, hole=.5))
    fig7.add_annotation(text=f'Tempo Total: {total_time}(hr)',
                        xref="paper", yref="paper",
                        font=dict(size=20, color='gray'),
                        align="center", bgcolor="rgba(0,0,0,0.8)",
                        x=0.0, y=0.0, showarrow=False)
    fig7.update_layout(main_config, height=400, template=template, showlegend=False)

    return fig7

# Card 7
@app.callback(
    Output('graph8', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def card7(toggle):
    template = template_theme1 if toggle else template_theme2

    # Graph 8: Receita vs Energia
    fig8 = make_subplots(specs=[[{"secondary_y": True}]])
    fig8.add_trace(go.Scatter(x=eixo_x, y=df_new["profit_spot"], marker={'color':color_escale[0]}, name="Receita MCP"),secondary_y=False,)
    fig8.add_trace(go.Scatter(x=eixo_x, y=df_new["profit_acl"], marker={'color':color_escale[3]}, name="Receita ACL"),secondary_y=False,)
    fig8.add_trace(go.Scatter(x=eixo_x, y=energy_total, mode='lines', marker={'color': color_escale[6]}, fill='tonexty',fillcolor='rgba(255, 0, 0, 0.2)', name="Energia"),secondary_y=True,)
    fig8.update_xaxes(title_text="Horizonte de Planejamento (horário)")
    fig8.update_yaxes(title_text="<b>Receita</b> (R$)", secondary_y=False)
    fig8.update_yaxes(title_text="<b>Energia</b> (MWh)", secondary_y=True)
    fig8.update_layout(main_config, height=400, template=template, showlegend=True)

    return fig8

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)