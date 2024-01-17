from typing import List, Dict, Any

import numpy as np
from dash import Dash, dcc, html, Input, Output, callback
import os

from src.enums.enums_heatmap import PAPER_METRICS, OLD_TO_NEW
from src.utils.utils import get_name_from_path
from src.enums.enums import NAMES_CLEAN, STYLE_H, STYLE_SCORE
from dash_bio.utils import PdbParser, create_mol3d_style
import dash_bio
import pandas as pd

import dash


class Viz3D:
    def __init__(self, native_path: str, rna_dir: str, scores_dir: str, puzzle: str, app: Dash):
        """
        :param native_path: path to native structures
        :param rna_dir: path to the aligned structures
        :param scores_dir: path to the scores
        :param puzzle: name of the puzzle (casp or rna-puzzles)
        """
        self.native_path = native_path
        self.rna_dir = rna_dir
        self.scores_dir = scores_dir
        self.all_challenges = sorted(os.listdir(self.rna_dir))
        # Drop R1117 for the moment
        if "R1117" in self.all_challenges:
            self.all_challenges.remove("R1117")
        self.dir_names = {
            rna: os.path.join(self.rna_dir, rna) for rna in self.all_challenges
        }
        self.names_to_path = {
            rna: {
                get_name_from_path(name): name
                for name in os.listdir(self.dir_names[rna])
                if name.endswith(".pdb")
            }
            for rna in self.all_challenges
        }

        self.all_methods = [
            x for x in list(NAMES_CLEAN.keys()) if x not in ["simrna", "eprna"]
        ]
        self.counter = 0  # Counter for the ID of non-predicted plots
        self.puzzle = puzzle
        self.current_challenge = self.all_challenges[0]
        app.callback(
            dash.dependencies.Output(
                f"all_challenges_methods_{puzzle}", "children", allow_duplicate=True
            ),
            dash.dependencies.Output(
                f"native_structure_{puzzle}", "children", allow_duplicate=True
            ),
            dash.dependencies.Input(f"dropdown_challenges_{puzzle}", "value"),
            prevent_initial_call=True,
            suppress_callback_exceptions=True,
        )(self.update_challenge)

    def get_native_plot(self):
        return [
            html.Div(
                id=f"native_molecule_{self.puzzle}",
                children=[self.get_native_structure(self.current_challenge)],
            ),
        ]

    def get_all_plots_3d(self):
        return [
            html.Div(
                id=f"all_challenges_methods_{self.puzzle}",
                children=[self.get_challenges_all_methods(self.current_challenge)],
            )
        ]

    def get_challenges_all_methods(self, rna_challenge: str):
        all_models = self.get_all_models(rna_challenge)
        return html.Div(
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "flexDirection": "row",
                "gap": 3,
                "justifyContent": "center",
                "marginBottom": 10,
            },
            children=[
                self.get_method_viz(method, rna_challenge, all_models)
                for method in all_models
            ],
            id=f"flex_container_{self.puzzle}",
        )

    def get_method_viz(self, method_name, rna_challenge, all_models):
        return self.get_viz_3d(method_name, rna_challenge, all_models)

    def get_viz_3d(self, method_name: str, rna_challenge: str, all_models: Dict):
        if len(all_models[method_name]) == 0:
            in_path = os.path.join(self.native_path, f"{rna_challenge}.pdb")
            is_native = True
        else:
            model_name = (
                method_name
                + "_"
                + all_models[method_name][0].replace("Prediction ", "")
                if len(all_models[method_name]) != 1
                else method_name
            )
            in_path = os.path.join(
                self.dir_names[rna_challenge],
                self.names_to_path[rna_challenge][model_name],
            )
            is_native = False
        try:
            scores_df = pd.read_csv(os.path.join(self.scores_dir, f"{rna_challenge}.csv"), index_col=0)
            scores_df = scores_df.rename(OLD_TO_NEW, axis = 1)
            scores = self.get_name_scores(in_path, scores_df, is_native)
        except FileNotFoundError:
            scores = {}
        output = self.get_data_styles(
            in_path, NAMES_CLEAN[method_name], scores, is_native=is_native
        )
        return output

    def get_name_scores(self, in_path: str, scores_df: pd.DataFrame, is_native: bool = False):
        """
        Finds the name from the scoring dataframe
        """
        if is_native:
            return None
        basename = os.path.basename(in_path)
        name = basename.split("_")[:-2]
        original_name = "normalized_" + "_".join(name) + ".pdb"
        try:
            scores = scores_df[scores_df.index == original_name][PAPER_METRICS ].to_dict()
        except KeyError:
            metrics = PAPER_METRICS.copy()
            metrics.remove("εRMSD")
            metrics.remove("lDDT")
            scores = scores_df[scores_df.index == original_name][metrics ].to_dict()
        new_scores = {key : scores[key][original_name] for key in scores}
        return new_scores

    def get_data_styles(self, in_path: str, method_name: str, scores: Dict, is_native: bool = False):
        content = self.get_viz_3d_data(in_path, is_native=is_native)
        if is_native:
            metrics = html.H3("No prediction", style=STYLE_SCORE),
            self.counter += 1
        else:
            scores = [f"{key}:{value:.2f}" for key, value in scores.items() if not np.isnan(value)]
            scores = " | ".join(scores)
            metrics = html.H3(scores, style={**STYLE_SCORE,
                                             **{"fontSize": "15px", "width": "70%", "margin": "0 auto",
                                                }})
        children = [
            html.H3(method_name, style={**STYLE_H, "margin": "0 auto", "width": "70%"}),
            metrics
        ]
        children.append(content)
        div_id = (
            self.puzzle + "_" + in_path + str(self.counter) if is_native else in_path
        )
        div = html.Div(id=div_id, children=children, style={"margin": "0 auto"})
        return div

    def get_title_from_path(self, in_path: str):
        """
        Get all the titles from the input paths with TM-score and RMSD
        """
        scores = {}
        name_split = in_path.split("_")
        method = get_name_from_path(os.path.basename(in_path))
        scores[method] = {"TM-score": float(name_split[-1].replace(".pdb", ""))}
        return scores

    def get_all_models(self, rna_challenge: str):
        """
        Return the different models for this challenge
        """
        all_models = list(self.names_to_path[rna_challenge].keys())
        all_models = self.get_name_and_decoys(all_models)
        all_models = {key: value for key, value in sorted(all_models.items())}
        all_models = {key: all_models.get(key, []) for key in self.all_methods}
        return all_models

    def get_name_and_decoys(self, in_paths: List):
        """
        Return the name and the decoys as values of dictionary
        """
        output = {}
        for in_path in in_paths:
            if "simrna" in in_path or "eprna" in in_path:
                continue
            name_split = in_path.split("_")
            method = name_split[0]
            if len(name_split) == 2:
                suffix = name_split[1]
                output[method] = output.get(method, []) + [f"Prediction {suffix}"]
                if method in output[method]:
                    output[method].remove(method)
            else:
                output[method] = [method]
        return output

    def get_native_structure(self, rna_challenge: str):
        native_path = os.path.join(self.native_path, f"{rna_challenge}.pdb")
        content = self.get_viz_3d_data(
            native_path, width=900, height=600, is_native=True
        )
        title = "RNA-Puzzles" if self.puzzle == "rna_puzzles" else "CASP-RNA"
        children = [
            html.Div(
                style={
                    "background-image": "url('assets/img/rna_icon.png')",
                    "background-size": "cover",
                    "background-position": "center",
                    "margin": "0 auto",
                    "width": "50px",
                    "height": "50px",
                }
            ),
            html.H2(
                f"{title} challenge",
                style={"color": "black", "fontSize": "30px"},
                id="title_challenge",
            ),
            *self._get_separation(color="black"),
            html.Div(
                dcc.Dropdown(
                    self.all_challenges,
                    value=self.all_challenges[0],
                    id=f"dropdown_challenges_{self.puzzle}",
                    style={"background-color": "#6DB9EF", "border-radius": "15px"},
                ),
                style={
                    "width": "20%",
                    "margin": "0 auto",
                    "height": "50px",
                    "border-radius": "15px",
                    "fontSize": "30px",
                    "color": "black",
                },
            ),
            html.Br(),
            html.H3(f"Native {rna_challenge}", style=STYLE_H),
            content,
        ]
        div = html.Div(
            id=f"native_structure_{self.puzzle}",
            children=children,
            style={"width": "100%"},
        )
        return div


    def get_viz_3d_data(
        self, in_path: str, width=450, height=450, is_native: bool = False
    ):
        parser = PdbParser(in_path)
        data = parser.mol3d_data()
        style = create_mol3d_style(
            data["atoms"],
            visualization_type="cartoon",
            color_element="chain",
            color_scheme=self.get_color_scheme(data, is_native),
        )
        content = dash_bio.Molecule3dViewer(
            modelData=data,
            styles=style,
            backgroundColor="#9BB8CD",
            backgroundOpacity=0.4,
            width=width,
            height=height,
            style={
                "width": width,
                "height": height,
                "textAlign": "center",
                "margin": "0 auto",
                "marginBottom": "20px"
            },
            zoom={"factor": 1.3}
        )
        return content

    def get_color_scheme(self, data: Any, is_native: bool):
        chains = list(set([atom.get("chain", 65) for atom in data.get("atoms", {})]))
        orders = [ord(id) for id in chains]
        max_order = max(orders)
        index_max = max_order + 1 if is_native else max_order
        if is_native:
            color_scheme = {
                chr(chain_id).upper(): "red" for chain_id in range(65, index_max)
            }
        else:
            color_scheme = {
                chr(chain_id).upper(): "blue" for chain_id in range(65, index_max)
            }
            color_scheme[chr(max_order).upper()] = "red"
        if "1" in chains and "A" in chains:
            color_scheme["1"] = "red"
            color_scheme["A"] = "blue"
        color_scheme["0"] = "red"
        return color_scheme

    def update_challenge(self, value):
        if value is None:
            return None
        self.current_challenge = value
        output = [self.get_challenges_all_methods(value)]
        native_struct = self.get_native_structure(value)
        return output, native_struct

    def _get_separation(self, color="white"):
        return (
            html.Hr(style={"height": "5px"}),
            html.Hr(
                style={
                    "width": "100px",
                    "background-color": color,
                    "height": "2px",
                    "margin": "0 auto",
                }
            ),
            html.Hr(style={"height": "5px"}),
        )
