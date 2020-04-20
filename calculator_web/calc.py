import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, MATCH, State, ALL

import dash_defer_js_import as dji


import numpy as np
import pandas as pd
import joblib

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


app = dash.Dash(__name__, external_stylesheets = ["/static/style.css"])
server = app.server

df = pd.read_csv("../../joined_combined_filtered_mined_soil_water_df_td_17_4.csv")
fdf = df[(df["pool"] != True) & (df["secondfloor"] < 1) & (df["mhome"] < 1)  & (df["pers_prop_val"] < 1) & (df["parval"] < 1000000) & (df["parval"] > 10000) & (df["lot_area"] < 500)].copy()
fdf["add_g_size"] = fdf["addsize"] + fdf["gize"]

cdf = pd.read_csv("../CropWaterUsage.csv")

model = joblib.load('../regr.pkl') 

features = ["lot_area", "TotalWater", "water_dist", "castorieindex", "firstfloor", "city_dist"]
features_label = ["Lot Area (acre)", "Total Water Access (ft/year)", "Distance to Water Diversion (km)", "Soil Quality (Storie) Index", "Floor Area (sqft)", "Distance from City (km)"]
features_text = [
    dcc.Markdown("The parcel lot size, in acres, as defined in survey data.\n\nSource: Obtained via LandGrid Parcel Data extract.", style={'whiteSpace': 'pre-wrap'}), 
    dcc.Markdown("Total agricultural water estimate, in acre-ft/acre/year. This estimate was obtained from identification of crop type grown at each parcel and using a combination of irrigation data for each crop and evapotranspiration data obtained for Fresno. A fixed mean rainfall figure was used. \n\nSources: Crop data - California Natural Resources Agency (ESRI shapefiles), Evaporanspiration - ITRC, California Polytechnic, Irrigation - \"California Agricultural Production and Irrigated Water Use\", CRS.", style={'whiteSpace': 'pre-wrap'}), 
    dcc.Markdown("The mean distance to the 5 nearest bulk water diversion points, in kilometers. This is a proxy for irrigation water transportation/access difficulty.\n\nSource: Computed from CA Water Boards eWRIMS extract.", style={'whiteSpace': 'pre-wrap'}),  
    dcc.Markdown("Storie Index for soil quality, extracted from SSURGO database for predominant soil type in each parcel\n\nSource: US DoA NRCS Web Soil Survey.", style={'whiteSpace': 'pre-wrap'}),  
    dcc.Markdown("Floor Area for any single storey habitable buildings only.\n\nSource: Fresno County Assesor.", style={'whiteSpace': 'pre-wrap'}), 
    dcc.Markdown("Direct distance to centre of Fresno city area, per parcel.\n\nSource: Calculated from LandGrid Parcel Data extract.", style={'whiteSpace': 'pre-wrap'}), ]

sliders = [

    html.Div([html.Div(features_label[i], id = {'type': 'dynlabel', 'index': f + '--label'}, style = {'width': '225px', 'float' : 'left'}, n_clicks = 0),

    html.Div(dcc.Slider(
        id= {'type' : 'dynslider', 'index': f + '--slider'},
        min=round(fdf[f].quantile(0.25),1),
        max=round(fdf[f].quantile(0.75),1),
        value=fdf[f].mean(),
        marks={str(int(x)): str(int(x)) for x in np.linspace(int(fdf[f].quantile(0.10)), int(fdf[f].quantile(0.90)), 5)},
        included = False,
        step = 0.1,
        tooltip = {}
    ), style = {'width': '75%', 'display' : 'inline-block'})
    ], id = {'type' : 'dynsliderdiv', 'index': f + '--sliderdiv'}, n_clicks = 0)

    for i,f in enumerate(features)

]


structure = list([

    html.Div([dcc.Graph(id='indicator-graphic', style={'flex':'47.5%'}, responsive = 'auto'),    dcc.Graph(id='hist-graphic', style={'flex':'20%'}, responsive = 'auto')], style={'display':'flex', 'width' : '80%'}),

    html.Div(
        [
        html.Div("Independent to Plot", style={'float' : 'left', 'width': '225px', 'paddingTop': '8px'}),
        html.Div(
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': fl, 'value': features[i]} for i,fl in enumerate(features_label)],
                value='TotalWater', clearable = False, searchable = False,
            ), style = {'width': '15%', 'display' : 'inline-block', 'paddingLeft': '24px'})
        ], style = {'marginBottom': '20px', 'marginTop': '20px'})

    ])

info_section = list([ html.Div([

    html.Div(sliders, style = {'flex': '50%'}),

    html.Div(
        [html.Div("", id = "glossary_sel", style = {'fontStyle': 'italic', 'fontSize': '14pt', 'padding': '5px 5px 0px 5px'}), html.Div("", id = "glossary_txt", style = {'padding': '5px'})
        , html.Div(dcc.Markdown("Random forest regression fitted on 12273 parcel samples, R<sup>2</sup> = 0.54 on 2166 test samples. Target variable source Fresno County Assesor via LandGrid.", dangerously_allow_html=True), style = {'padding': '5px', 'fontSize': '11px', 'fontStyle': 'italic'})]
        , style = {'flex': '20%', 'border': 'solid 1px gray'})], style = {'display': 'flex', 'width' : '80%'}  )



])

structure.extend(info_section)

#print(structure)

app.layout = html.Div(structure + [html.Article(dji.Import(src="/static/script.js"))])

slider_inputs = [Input({'type': 'dynslider', 'index': f + '--slider'}, 'value') for f in features]
inputs = [Input('xaxis-column', 'value')]
inputs.extend(slider_inputs)



@app.callback(
    Output('indicator-graphic', 'figure'),
    inputs)
def update_graph(x_col, *values):
    
    values = list(values)

    x = np.linspace(fdf[x_col].quantile(0),fdf[x_col].quantile(0.90),50)

    f_index = features.index(x_col)

    pred_args = [values[0:f_index] + [w] + values[f_index + 1:] for w in x]
    y = [model.predict([arg])[0] for arg in pred_args]

    dff = pd.DataFrame({'x': x, 'pred': y})

    if(x_col == 'TotalWater'):

        u = cdf[cdf["TotalWater"] < fdf[x_col].quantile(0.90)]["TotalWater"].values
        t = cdf[cdf["TotalWater"] < fdf[x_col].quantile(0.90)]["Crop2016"].values
        

        pred_args = [values[0:f_index] + [w] + values[f_index + 1:] for w in u]
        v = [model.predict([arg])[0] for arg in pred_args]

        cdff = pd.DataFrame({'x': u, 'pred': v, 'text': t})


    data = [dict(
            name="Prediction",
            x=dff['x'],
            y=dff['pred'],
            mode='line',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
    )]

    if(x_col == 'TotalWater'):
        data.append(dict(
            name="Crop",
            x=cdff['x'],
            y=cdff['pred'],
            text=cdff['text'],
            mode='markers',
            marker={
                'color': 'green',
                'size': 10,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ))        

    return {
        'data': data,
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
    Output('hist-graphic', 'figure'),
    inputs)
def update_graph(x_col, *values):
    
    f_index = features.index(x_col)

    ffdf = fdf[(fdf[x_col] >= fdf[x_col].quantile(0)) & (fdf[x_col] < fdf[x_col].quantile(0.90))]

    return {
        'data': [dict(
            x=ffdf[x_col],
            type='histogram',
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
                'title': "Count",
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


nclicks_old = np.zeros(len(features))

@app.callback(
    [Output('glossary_sel', "children"), Output('glossary_txt', "children")],
    [Input({'type': 'dynlabel', "index": ALL}, 'n_clicks'), Input({'type': 'dynsliderdiv', "index": ALL}, 'n_clicks')],
)
def update_text(a, b):
  
    global nclicks_old

    nclicks = np.array(a) + np.array(b)
    diff = nclicks - nclicks_old
    i = np.argmax(diff)
    nclicks_old = nclicks

    return features_label[i], features_text[i]




if __name__ == '__main__':
    app.run_server(debug=True)
