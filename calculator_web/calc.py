import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, MATCH, State

import numpy as np
import pandas as pd
import joblib

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

app = dash.Dash(__name__)
server = app.server

df = pd.read_csv("../../joined_combined_filtered_mined_soil_water_df_td_17_4.csv")
fdf = df[(df["pool"] != True) & (df["secondfloor"] < 1) & (df["mhome"] < 1)  & (df["pers_prop_val"] < 1) & (df["parval"] < 1000000) & (df["parval"] > 10000) & (df["lot_area"] < 500)].copy()
fdf["add_g_size"] = fdf["addsize"] + fdf["gize"]

model = joblib.load('../regr.pkl') 

features = ["lot_area", "TotalWater", "water_dist", "castorieindex", "firstfloor", "city_dist"]
features_label = ["Lot Area (acre)", "Total Water Access (ft/year)", "Distance to Water Diversion (km)", "Soil Quality (Storie) Index", "Floor Area (sqft)", "Distance from City (km)"]

sliders = [

    html.Div([html.Div(features_label[i], style = {'width': '225px', 'float' : 'left'}),

    html.Div(dcc.Slider(
        id= {'type' : 'dynslider', 'index': f + '--slider'},
        min=round(fdf[f].quantile(0.25),1),
        max=round(fdf[f].quantile(0.75),1),
        value=fdf[f].mean(),
        marks={str(int(x)): str(int(x)) for x in np.linspace(int(fdf[f].quantile(0.25)), int(fdf[f].quantile(0.75)), 5)},
        included = False,
        step = 0.1,
        tooltip = {}
    ), style = {'width': '48%', 'display' : 'inline-block'})
    ])

    for i,f in enumerate(features)

]


structure = list([

    dcc.Graph(id='indicator-graphic'),

    html.Div(
        [
        html.Div("Independent to Plot: ", style={'float' : 'left', 'width': '225px', 'padding-top': '8px'}),
        html.Div(
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': fl, 'value': features[i]} for i,fl in enumerate(features_label)],
                value='TotalWater'
            ), style = {'width': '15%', 'display' : 'inline-block', 'padding-left': '24px'})
        ], style = {'margin-bottom': '20px', 'margin-top': '20px'})

    ])

structure.extend(sliders)

#print(structure)

app.layout = html.Div(structure)


slider_inputs = [Input({'type': 'dynslider', 'index': f + '--slider'}, 'value') for f in features]
inputs = [Input('xaxis-column', 'value')]
inputs.extend(slider_inputs)



@app.callback(
    Output('indicator-graphic', 'figure'),
    inputs)
def update_graph(x_col, *values):
    
    values = list(values)

    x = np.linspace(df[x_col].quantile(0.25),df[x_col].quantile(0.75),50)

    f_index = features.index(x_col)

    pred_args = [values[0:f_index] + [w] + values[f_index + 1:] for w in x]

    y = [model.predict([arg])[0] for arg in pred_args]

    dff = pd.DataFrame({'x': x, 'pred': y})

    return {
        'data': [dict(
            x=dff['x'],
            y=dff['pred'],
            mode='line',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': features_label[f_index],
                'type': 'linear' 
            },
            yaxis={
                'title': "Parcel Value $USD",
                'type': 'linear'
            },
            margin={'l': 50, 'b': 40, 't': 10, 'r': 20},
            hovermode='closest'
        )
    }


@app.callback(
    Output({'type': 'dynslider', "index": MATCH}, "disabled"),
    inputs,
    [State({'type': 'dynslider', 'index': MATCH}, 'id')]
)
def disable_slider(x_col, *values):
    if(x_col in values[-1]['index']): 
        return True
    return False

if __name__ == '__main__':
    app.run_server(debug=True)
