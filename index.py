from pathlib import Path
import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from bjorli_games import *


page_container = html.Div(
    children=[
        # represents the URL bar, doesn't render anything
        dcc.Location(
            id='url',
            refresh=False,
        ),
        # content will be rendered in this element
        html.Div(id='page-content')
    ]
)

data_paths = get_bjorli_game_paths()
dcc_children = []
for path in data_paths:
    dcc_children.append(dcc.Link(children=path[1], href=f"/{path[0].name}"))
    dcc_children.append(html.Br())

### Index Page Layout ###
index_layout = html.Div(children=dcc_children)

### Set app layout to page container ###
app.layout = page_container### Assemble all layouts ###
validation_children = [page_container, index_layout]
for path in data_paths:
    validation_children.append(bg_layout(path[0].name))

app.validation_layout = html.Div(
    children = validation_children
)

### Update Page Container ###
@app.callback(
    Output(
        component_id='page-content',
        component_property='children',
        ),
    [Input(
        component_id='url',
        component_property='pathname',
        )]
)
def display_page(pathname):
    match pathname.split("/"):
        case ["", ""]:
            return index_layout
        case ["", date]:
            return bg_layout(date)
        case _:
            return "404"
