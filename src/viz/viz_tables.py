from typing import List, Optional
import os
import pandas as pd
from dash import dash_table
from src.enums.enums import NAMES_CLEAN, REPLACE_METRICS_AND_SCORES, METRICS, ENERGIES
from dash import Dash, dcc, html, Input, Output, callback
import dash


class VizTables:
    def __init__(self, csv_folder: str, puzzle: str, app):
        self.csv_folder = csv_folder
        self.counter = 0
        self.current_value = None
        self.puzzle = puzzle
        app.callback(
            dash.dependencies.Output(
                f"data_table_Metrics_{self.puzzle}", "children", allow_duplicate=True
            ),
            dash.dependencies.Output(
                f"data_table_Scoring functions_{self.puzzle}",
                "children",
                allow_duplicate=True,
            ),
            dash.dependencies.Input(f"dropdown_challenges_{puzzle}", "value"),
            prevent_initial_call=True,
            suppress_callback_exceptions=True,
        )(self.update_table)

    def clean_df(self, df):
        """
        Add Model name, clean the names, change the metrics names
        """
        df["Model name"] = df.index
        new_order = ["Model name"] + [x for x in df.columns if x != "Model name"]
        df = df[new_order]
        df["Model name"] = df["Model name"].apply(self.clean_name)
        df.rename(columns=REPLACE_METRICS_AND_SCORES, inplace=True)
        df = df[df["Model name"].notnull()]
        df = df.round(2)
        return df

    def clean_name(self, name):
        name = name.replace("normalized_", "")
        split_name = name.split("_")
        new_name = NAMES_CLEAN[split_name[0]]
        if len(split_name) <= 2 or split_name[0] == "ifoldrna":
            return new_name
        else:
            return new_name + f" (Prediction {split_name[-1].replace('.pdb', '')})"

    def _plot_csv(self, rna_challenge: str, scores: List, name: str):
        df = pd.read_csv(
            os.path.join(self.csv_folder, f"{rna_challenge}.csv"), index_col=0
        )
        df = self.clean_df(df)
        df = df[["Model name"] + scores]
        output = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            style_header={"backgroundColor": "#4782a9", "color": "white"},
            style_cell={
                "backgroundColor": "#b5c9da",
                "color": "black",
                "textAlign": "center",
            },
            style_data={"border": "1px solid white"},
        )
        output = html.Div(
            children=[
                html.Div(output, id=f"data_table_{name}_{self.puzzle}"),
            ],
            style={
                "margin": "0 auto",
                "width": "100%",
            },
        )
        return output

    def plot_csv_metrics(self, rna_challenge: Optional[str] = None):
        if rna_challenge is None:
            rna_challenge = "rp03" if self.puzzle == "rna_puzzles" else "R1108"
        if self.puzzle == "casp":
            metrics = [
                metric for metric in METRICS if metric not in ["CAD", "εRMSD", "lDDT"]
            ]
        else:
            metrics = METRICS
        return self._plot_csv(rna_challenge, metrics, "Metrics")

    def plot_csv_energies(self, rna_challenge: Optional[str] = None):
        if self.puzzle == "casp":
            return html.Div()
        if rna_challenge is None:
            rna_challenge = "rp03" if self.puzzle == "rna_puzzles" else "R1108"
        return self._plot_csv(rna_challenge, ENERGIES, "Scoring functions")

    def update_table(self, value):
        if self.counter > 1 and value == "rp03":
            new_value = self.current_value
        else:
            self.current_value = value
            new_value = self.current_value
        self.counter += 1
        return self.plot_csv_metrics(new_value), self.plot_csv_energies(new_value)
