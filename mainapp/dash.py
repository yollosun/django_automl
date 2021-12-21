import dash
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DjangoDash

app = DjangoDash('SimpleExample')   # replaces dash.Dash

app.layout = html.Div([
    dcc.RadioItems(
        id='dropdown-color',
        options=[{'label': c, 'value': c.lower()} for c in ['Red', 'Green', 'Blue']],
        value='red'
    ),
    html.Div(id='output-color'),
    dcc.RadioItems(
        id='dropdown-size',
        options=[{'label': i,
                  'value': j} for i, j in [('L','large'), ('M','medium'), ('S','small')]],
        value='medium'
    ),
    html.Div(id='output-size')

])

@app.callback(
    dash.dependencies.Output('output-color', 'children'),
    [dash.dependencies.Input('dropdown-color', 'value')])
def callback_color(dropdown_value):
    return "The selected color is %s." % dropdown_value

@app.callback(
    dash.dependencies.Output('output-size', 'children'),
    [dash.dependencies.Input('dropdown-color', 'value'),
     dash.dependencies.Input('dropdown-size', 'value')])
def callback_size(dropdown_color, dropdown_size):
    return "The chosen T-shirt is a %s %s one." %(dropdown_size,
                                                  dropdown_color)









# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.express as px
# import pandas as pd
#
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })
#
# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
#
#
#
# def dashi(df, x, y, typeOfGraph, list=0):
#     app = dash.Dash(__name__)
#     if typeOfGraph == "scatter":
#         fig = px.scatter(df, x=x, y=y)
#     elif typeOfGraph == "bar":
#         fig = px.bar(df, x=x, y=y)
#     elif typeOfGraph == "line":
#         fig = px.line(df, x=x, y=y)
#     elif typeOfGraph == "area":
#         fig = px.area(df, x=x, y=y)
#     elif typeOfGraph == "funnel":
#         fig = px.funnel(df, x=x, y=y)
#     elif typeOfGraph == "histogram":
#         fig = px.histogram(df, x=x, y=y)
#     elif typeOfGraph == "density_heatmap":
#         fig = px.density_heatmap(df, x=x, y=y)
#     fig = px.bar(df, x=x, y=y, barmode="group")
#     app.layout = html.Div(children=[
#         html.H1(children='Hello Dash'),
#
#         dcc.Graph(
#             id='example-graph',
#             figure=fig
#         )
#     ])
#     return app
#     # app.run_server(debug=True)
#
#
#
#
# # assume you have a "long-form" data frame
# # see https://plotly.com/python/px-arguments/ for more options
# # df = pd.DataFrame({
# #     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
# #     "Amount": [4, 1, 2, 2, 4, 5],
# #     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# # })
#
# # fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
# #
# #
# #
# # if __name__ == '__main__':
# #