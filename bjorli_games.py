import math
import time
import datetime
from typing import Tuple, List, Dict
from dash import Dash, dash_table, dcc, html, ctx
from dash.dependencies import Input, Output, State
from pathlib import Path


app = Dash(__name__)


def file_to_table(filename: Path) -> List[Dict[str, any]]:
    """Reads csv file on the form
        Deltager,sp1,sp2,sp3,sp4
        m,1,2,3,4
        r,9,8,7,6
        a,5,4,3,2

    first row are the the game names, except first column which are row names
    first column in each subsequent row are the contestants name
    the rest of the columns are corresponding score for the contestant
    in the respective game

    Returns:
        headers:

    """

    with open(filename, "r") as table_file:
        headers = table_file.readline().strip().split(",") + ["Total"]
        table = []
        for line in table_file.readlines():
            row = line.strip().split(",")
            row[1:] = list(map(int, row[1:]))
            row.append(math.prod(row[1:]))
            table.append({})
            print(headers)
            print(row)
            for head, score in zip(headers, row, strict=True):
                table[-1][head] = score
    table = sorted(table, key=lambda d: d["Total"])
    return table


def table_to_file(filename: Path, table: List[Dict[str, any]]):
    out_string = ",".join(list(table[0].keys())[:-1]) + "\n"
    for line in table[1:-1]:
        out_string += ",".join(map(str, list(line.values())[:-1])) + "\n"
    out_string += ",".join(map(str, list(table[-1].values())[:-1]))
    print(filename)
    filename.touch()    
    filename.write_text(out_string)


def update_table_new_column(
    columns: Dict[str, any], rows: List[Dict[str, any]]
) -> List[Dict[str, any]]:
    for col_name in [c["name"] for c in columns]:
        for row in rows:
            if col_name not in row:
                row[col_name] = 1

    return rows


def calculate_new_total(rows: List[Dict[str, any]]) -> List[Dict[str, any]]:
    for row in rows:
        total = 1
        for column, value in row.items():
            if not column in ["Deltager", "Total"]:
                total *= int(value)
        row["Total"] = total
    return rows


def create_score_table(table: List[Dict[str, any]]):
    columns = []
    for col in table[0].keys():
        match col:
            case "Deltager" | "Total":
                columns.append({"name": col, "id": col})
            case _:
                columns.append({"name": col, "id": col, "renamable": True, "deletable": True})



    score_table = dash_table.DataTable(
        id="score-board",
        style_table={"overflowX": "auto"},
        style_cell={
            "whiteSpace": "normal",
            "height": "auto",
            "minWidth": "30px",
            "width": "30px",
            "maxWidth": "30px",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "rgb(220, 220, 220)",
            }
        ],
        data=table,
        columns=columns,
        editable=True,
    )
    return score_table


def read_rules(filename: Path):
    markdown = dcc.Markdown(filename.read_text())
    return html.Div([markdown],)


def bg_layout(date: str):
    date_verbose = datetime.datetime.strptime(date, "%Y%m").strftime("%B %Y") 
    data_path = Path("data")/date
    top_header = html.H1(children=f"Bjorli games {date_verbose}", style={"text-align": "center"})
    newest_file = [d for d in sorted(data_path.iterdir()) if d.name != "regler.md"][-1]
    table_from_file = file_to_table(newest_file)
    score_table = create_score_table(table_from_file)
    column_add_button = html.Button("Add Column", id="adding-column-button", n_clicks=0)
    column_add_div = html.Div(
        [
            dcc.Input(
                id="add-column-div",
                placeholder="Nytt spillnavn",
                value="",
            ),
            column_add_button,
        ]
    )
    save_button = html.Div([html.Button('Submit', id='submit-table', n_clicks=0, className=f"{date}"),
                            html.P(id='submit-table-hidden')])
    rules_markdown = read_rules(data_path/"regler.md")

    lo = html.Div(
        style={
            "width": "50%",
            "margin": "auto;",
            "display": "inline",
            "justify-content": "center",
            "align-items": "center",
        },
        children=[
            top_header,
            column_add_div,
            score_table,
            save_button,
            rules_markdown,
        ],
    )
    return lo


@app.callback(
    [Output("score-board", "columns"), Output("score-board", "data")],
    [Input("adding-column-button", "n_clicks"), Input("score-board", "data_timestamp")],
    [
        State("add-column-div", "value"),
        State("score-board", "columns"),
        State("score-board", "data"),
    ],
)
def new_column(n_clicks, timestamp, value, existing_columns, current_data):
    match ctx.triggered[0]["prop_id"]:
        case "adding-column-button.n_clicks":
            existing_columns.insert(
                -1, {"id": value, "name": value, "renamable": True, "deletable": True}
            )
            new_data = update_table_new_column(existing_columns, current_data)
            return [existing_columns, new_data]
        case "score-board.data_timestamp":
            new_data = calculate_new_total(current_data)
            return [existing_columns, new_data]
        case _:
            return [existing_columns, current_data]


@app.callback(
    Output('submit-table-hidden', 'children'),
    [Input('submit-table', 'n_clicks'),
     Input('submit-table', 'className')],
    [State("score-board", "data")])
def clicks(n_clicks, date, data):
    if n_clicks > 0:
        filename = Path("data")/date/f"{int(time.time())}.csv"
        table_to_file(filename, data)


if __name__ == "__main__":
    lo = bg_layout(date="102022")
    app.layout = lo
    app.run_server(debug=True)
