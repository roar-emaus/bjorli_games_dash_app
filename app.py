import dash
import logging


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        )
