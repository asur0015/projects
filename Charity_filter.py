#Importing Libraries
from dash import Dash, dcc, html, Input, Output
from plotly.express import data
import pandas as pd
import re
from PIL import Image
import dash_bootstrap_components as dbc



#Reading Data File
data = pd.read_csv(r"data_charity.csv")
data["inside_vic"] = data["State"].apply(lambda x: "Only Victorian Charities" if x in ['Victoria', 'VIC','Vic', 'victoria', 'St Helena Victoria', 'VICTORIA', 'Benalla Victoria', 'vic' 'Victoria,', 'VIC ', 'Victora'] else "Charities that operate across Australia including Victoria")

#Header Image path
image_path = 'https://charity-project.s3.ap-southeast-2.amazonaws.com/image.png'


#Webpage HTML
app = Dash(__name__ , external_stylesheets=[dbc.themes.FLATLY])
server = app.server



app.layout = html.Div([
    html.Img(src=image_path, style={'height': '450px','width':'100%'}),
    html.Br(),
    
    html.Br(),
    html.H3('Select a Charity location Preference:'),
    html.P('Please note that all the charities given below operate in Victoria. There are some charities that are based on the other states of Australia, but all of them operate in Victoria remotely. All the charity details that you see operate in Victoria, Australia.'),
    
    html.Br(),
    html.H4('So, please enter your preferred charity:'),
    dcc.RadioItems(
        id='radio-filter',
        options=[{'label': i, 'value': i} for i in data['inside_vic'].unique()],
        value = data['inside_vic'].unique()[0],
        labelStyle={'display': 'inline-block', 'margin-right': '20px'},
        inputStyle={'margin-right': '10px'}
    ),
    
    html.Br(),
    html.H4('Select from the given Suburbs:'),
    dcc.Dropdown(
        id='dropdown-filtered',
        options=[],
        value=None,
        multi = True
    ),
    
    html.Br(),
    html.Div(id='output', style={'border': 'solid', 'border-width': '2px', 'border-collapse': 'separate', 'margin':'20px'}),
    html.Br(),
    html.Br()
])

@app.callback(
    Output('dropdown-filtered', 'options'),
    Input('radio-filter', 'value')
)

def update_dropdown(value):
    if(value == "Only Victorian Charities"):
        filtered_data = data[data['inside_vic'] == value]
    else:
        filtered_data = data
    list_of_suburbs = sorted([str(suburb) for suburb in filtered_data["Town_City"].unique()])
    options = [{'label': str(suburb), 'value': str(suburb)} for suburb in list_of_suburbs]
    return options

@app.callback(
    Output('output', 'children'),
    Input('dropdown-filtered', 'value')
)

def update_table(value):
    if value:
        filtered_df = data[data["Town_City"].isin(value)]
    else:
        filtered_df = data
    
    filtered_df = filtered_df[['Charity_Legal_Name','Charity_Website', 'Advancing_Education', 'Promoting_or_protecting_human_rights', 'Advancing_social_or_public_welfare', 'Children', 'Families', 'Females', 'Financially_Disadvantaged', 'Males', 'People_at_risk_of_homelessness']]
    final_df = pd.DataFrame(columns=["Name", "Website", "Type"])
    
    for index, row in filtered_df.iterrows():
        charity_type = [col for col, value in row.items() if str(value).strip() == "Y"]
        final_df = final_df.append({"Name": row['Charity_Legal_Name'], "Website": row['Charity_Website'], "Type": str(charity_type).replace("[", "").replace("]", "")}, ignore_index = True)

    table_data = [html.Tr([html.Th(col, style={'padding': '10px', 'border-bottom': '2px solid black'}) for col in final_df.columns])] + \
                 [html.Tr([html.Td(final_df.iloc[i][col], style={'padding': '10px'})  if col != "Website" else html.Td(html.A(final_df.iloc[i][col], href = final_df.iloc[i][col])) for col in final_df.columns])
                  for i in range(len(final_df))]
    return table_data


if __name__ == '__main__':
    app.run_server(debug=True)