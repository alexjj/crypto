import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

data = pd.read_csv('gotchi.csv')
data['Value'] = data['BRS'] / data['Price (GHST)']

app = dash.Dash(__name__)

app.layout = html.Div(
    children = [
        html.H1(children="Aavegotchi Baazaar Explorer",),
        html.P(
            children="Analyse past sales on the baazaar"
            " including as Gotchis, wearables and tickets"
            " Future features include:"
            " * Finding best value gotchi"
            " * Market value of your gotchi"
            " * Good deals based on historical prices",
        ),
        dcc.Graph(
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