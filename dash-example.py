import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

data = pd.read_csv('gotchi.csv')
data['Value'] = data['BRS'] / data['Price (GHST)']

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Aavegotchi Baazaar Explorer"

app.layout = html.Div(
    children = [
        html.Div(
            children=[
                html.P(children="👻📈", className='header-emoji'),
        html.H1(
            children="Aavegotchi Baazaar Explorer",
            className='header-title',
            ),
        html.P(
            children="Analyse past sales on the baazaar"
            " including as Gotchis, wearables and tickets"
            " Future features include:",
            className='header-description',),
        html.P(
            children=
            "Finding best value gotchi,"
            " Market value of your gotchi,"
            " Good deals based on historical prices",),
            ],
            className='header',
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        figure={
                            'data': [
                                {
                                    "x": data['BRS'],
                                    "y": data['Price (GHST)'],
                                    "type": "scatter",
                                    'mode': 'markers',
                                }
                                    ],
                            'layout': {'title': 'Cost by Rarity'},
                            },
                    ),
                ),
            ],
            className="card",
        ),

        dcc.Graph(
            figure={
                'data': [
                    {
                        "x": data['Block Sold'],
                        "y": data['Value'],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Cost efficiency of Gotchis"},
            },
        ),
    ]
)

if __name__ == "__main__":

    app.run_server(debug=True)