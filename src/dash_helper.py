from dash import Dash, dcc, html, Input, Output, callback, ctx
import dash
import dash_bootstrap_components as dbc
from src.viz.viz3d import Viz3D
from src.enums.enums import STYLE_TITLE, TEXT_FIRST_CASE, TEXT_SECOND_CASE, BUTTON_STYLE

from src.viz.viz_tables import VizTables
from src.viz.viz_heatmap import VizHeatmap
import flask


class DashHelper:
    def __init__(
        self,
        app,
        native_path: str,
        rna_dir: str,
        scores_dir: str,
        scores_dir_casp: str,
        casp_rna_native: str,
        casp_rna_dir: str,
    ):
        """
        :param native_path: path to native structures
        :param rna_dir: path to the aligned structures
        """
        self.app = app
        self.native_path = native_path
        self.rna_dir = rna_dir
        self.casp_rna_native = casp_rna_native
        self.casp_rna_dir = casp_rna_dir
        self.challenge = "rna_puzzles"
        self.viz3d = Viz3D(native_path, rna_dir, scores_dir, "rna_puzzles", self.app)
        self.viz_casp = Viz3D(casp_rna_native, casp_rna_dir, scores_dir_casp, "casp", self.app)
        self.viz_table_rna_puzzles = VizTables(scores_dir, "rna_puzzles", self.app)
        self.viz_table_casp = VizTables(scores_dir_casp, "casp", self.app)
        self.viz_table = self.get_viz_table()
        self.viz = self.get_viz()
        self.viz_heatmap = VizHeatmap(scores_dir)
        self.app.callback(
            dash.dependencies.Output(
                "3d_structures_shown", "children", allow_duplicate=True
            ),
            dash.dependencies.Output("title_challenge", "children"),
            dash.dependencies.Output("tables_shown", "children"),
            dash.dependencies.Output("heatmap", "children"),
            dash.dependencies.Output("boxplot", "children"),
            dash.dependencies.Input(
                "button-rna_puzzles",
                "n_clicks",
            ),
            dash.dependencies.Input("button-casp", "n_clicks"),
            prevent_initial_call=True,
            suppress_callback_exceptions=True,
        )(self.update_benchmark)

    def get_viz(self):
        if self.challenge == "rna_puzzles":
            viz = self.viz3d
        elif self.challenge == "casp":
            viz = self.viz_casp
        self.viz = viz
        return viz

    def get_viz_table(self):
        if self.challenge == "rna_puzzles":
            viz_table = self.viz_table_rna_puzzles
        elif self.challenge == "casp":
            viz_table = self.viz_table_casp
        return viz_table

    def get_first_page(self):
        content = html.Div(
            children=[
                html.Hr(style={"height": "15px"}),
                html.H1("State-of-the-RNArt", style=STYLE_TITLE),
                html.H3(
                    "Benchmarking current methods for RNA 3D structure prediction",
                    style={"color": "black"},
                ),
                html.Hr(style={"height": "15px"}),
            ],
        )
        return content

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
            html.Hr(style={"height": "2px"}),
        )

    def get_text_explanation(
        self, all_info, bg_color="#4682A9", color="white", button_color="black"
    ):
        content = html.Div(
            children=[
                html.Div(
                    style={
                        "background-image": all_info.get("IMAGE"),
                        "width": "50px",
                        "height": "50px",
                        "background-size": "cover",
                        "background-position": "center",
                        "margin": "0 auto",
                    }
                ),
                html.H2(
                    all_info.get("H2"),
                    style={
                        "color": color,
                        "fontSize": "30px",
                    },
                ),
                *self._get_separation(color=color),
                html.H3(
                    all_info.get("H3"),
                    style={
                        "color": color,
                        "width": "70%",
                        "text-align": "center",
                        "margin": "0 auto",
                        "fontSize": "15",
                        "height": "120px",
                    },
                ),
                *self._get_separation(color=color),
                html.Button(
                    html.A(
                        "More information",
                        href=all_info.get("LINK"),
                        style={
                            "color": "white" if color != "white" else "black",
                            "text-decoration": "none",
                        },
                    ),
                    style={
                        "color": "inherit",
                        "text-decoration": "none",
                        "background-color": button_color,
                        "border": "black",
                        "border-radius": "5px",
                        "padding": "10px",
                        "margin": "0 auto",
                        "display": "block",
                        "fontSize": "20px",
                    },
                ),
            ],
            style={
                "background-color": bg_color,
                "width": "100%",
                "margin": "0 auto",
                "padding": "20px",
                "text-align": "center",
                "height": "450px",
            },
        )
        return content

    def get_table_metrics(self):
        return self.viz_table.plot_csv_metrics("rp03")

    def get_first_cases(self):
        return dbc.Row(
            [
                dbc.Col(
                    self.get_text_explanation(TEXT_FIRST_CASE, button_color="#cedbe6"),
                    width=6,
                ),
                dbc.Col(
                    self.get_text_explanation(
                        TEXT_SECOND_CASE,
                        "#cedbe6",
                        color="black",
                        button_color="#4682A9",
                    ),
                    width=6,
                ),
            ]
        )

    def get_native_plot_dropdown(self):
        return html.Div(
            children=[
                html.Br(),
                self.get_button_choose_benchmark(),
                html.Div(
                    children=[
                        html.Br(style={"height": "10px"}),
                        *self.viz.get_native_plot(),
                        html.Br(),
                    ],
                ),
            ],
            style={
                "background-color": "#b5c9da",
                "width": "80%",
                "text-align": "center",
                "justify-content": "center",
                "margin": "0 auto",
                "border-radius": "5px",
                "padding": "20px",
            },
        )

    def get_layout_native(self):
        self.viz = self.get_viz()
        return html.Div(
            children=[
                html.Br(),
                self.get_native_plot_dropdown(),
                html.Br(),
                html.Div(
                    self.viz.get_all_plots_3d(),
                    style={
                        "width": "100%",
                        "text-align": "center",
                        "justify-content": "center",
                        "margin": "0 auto",
                    },
                ),
            ],
            id="3d_structures_shown",
        )

    def get_layout_native_casp(self):
        return [
            html.Div(
                children=[
                    html.Br(style={"height": "10px"}),
                    *self.viz_casp.get_native_plot(),
                    html.Br(),
                ],
                style={
                    "background-color": "#b5c9da",
                    "width": "100%",
                    "text-align": "center",
                    "justify-content": "center",
                    "margin": "0 auto",
                },
            ),
            html.Br(),
            html.Div(
                self.viz_casp.get_all_plots_3d(),
                style={
                    "width": "100%",
                    "text-align": "center",
                    "justify-content": "center",
                    "margin": "0 auto",
                },
            ),
        ]

    def get_layout_tables(self):
        self.viz_table = self.get_viz_table()
        return html.Div(
            children=[
                html.H2("Metrics", style={"color": "black", "fontSize": "40px"}),
                html.Div(
                    self.viz_table.plot_csv_metrics(),
                    style={
                        "width": "100%",
                        "text-align": "center",
                        "justify-content": "center",
                        "margin": "0 auto",
                    },
                ),
                html.H2(
                    "Scoring functions", style={"color": "black", "fontSize": "40px"}
                ),
                html.Div(
                    self.viz_table.plot_csv_energies(),
                    style={
                        "width": "100%",
                        "text-align": "center",
                        "justify-content": "center",
                        "margin": "0 auto",
                    },
                ),
            ],
            id="tables_shown",
        )

    def get_layout_dcc(self, fig, c_id):
        return html.Div(
            html.Div(
                dcc.Graph(
                    figure=fig,
                    responsive=True,
                    style={"width": "100%", "height": "100%"},
                ),
                style={
                    "width": "100%",
                    "height": "100%",
                },
            ),
            style={
                "width": "77%",
                "height": "800px",
                "display": "inline-block",
                "padding-top": "5px",
                "padding-left": "1px",
                "overflow": "hidden",
            },
            id=c_id,
        )

    def get_heatmap(self):
        fig = self.viz_heatmap.plot_heatmaps()
        return self.get_layout_dcc(fig, "heatmap")

    def get_boxplot(self):
        fig = self.viz_heatmap.plot_box_plot()
        return self.get_layout_dcc(fig, "boxplot")

    def get_button_choose_benchmark(self):
        return html.Div(
            [
                html.H2(
                    "Choose a benchmark:", style={"color": "black", "fontSize": "35px"}
                ),
                html.Div(
                    [
                        html.Button(
                            "RNA-Puzzles",
                            id="button-rna_puzzles",
                            n_clicks=0,
                            style={**BUTTON_STYLE, **{"color": "black"}},
                        ),
                        html.Button(
                            "CASP-RNA",
                            id="button-casp",
                            n_clicks=0,
                            style={
                                **BUTTON_STYLE,
                                **{"color": "white", "background-color": "#4682A9"},
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "align-items": "center",
                        "width": "30%",
                        "margin": "0 auto",
                        "padding": "20px",
                        "text-align": "center",
                    },
                ),
            ]
        )

    def update_benchmark(self, btn1, btn2):
        if "button-rna_puzzles" == ctx.triggered_id:
            self.challenge = "rna_puzzles"
            title = "RNA-Puzzles"
            heatmap, boxplot = self.get_heatmap(), self.get_boxplot()
        elif "button-casp" == ctx.triggered_id:
            self.challenge = "casp"
            title = "CASP-RNA"
            heatmap, boxplot = None, None
        layout_table = self.get_layout_tables()
        return (
            self.get_layout_native(),
            html.H2(
                f"{title} challenge",
                style={"color": "black", "fontSize": "30px"},
                id="title_challenge",
            ),
            layout_table,
            heatmap,
            boxplot,
        )

    def run(self):
        page_structure = [
            dbc.Row(self.get_first_page()),
            html.Br(),
            dbc.Row(self.get_first_cases()),
            html.Br(),
            self.get_layout_native(),
            html.Br(),
            self.get_layout_tables(),
            self.get_heatmap(),
            self.get_boxplot(),
        ]

        self.app.layout = dbc.Container(
            id="root",
            children=page_structure,
            fluid=True,
            style={
                "background-color": "white",
            },
        )
        return self.app


server = flask.Flask(__name__)  # define flask app.server

app = dash.Dash(
    external_stylesheets=[dbc.themes.MORPH],
    suppress_callback_exceptions=True,
    server=server,
)
params = {
    "app": app,
    "native_path": "data/rna_puzzles/native",
    "rna_dir": "data/rna_puzzles/aligned",
    "scores_dir": "data/rna_puzzles/scores",
    "scores_dir_casp": "data/casp_rna/scores",
    "casp_rna_native": "data/casp_rna/native",
    "casp_rna_dir": "data/casp_rna/aligned",
}
dash_helper = DashHelper(**params)
app = dash_helper.run()
if __name__ == "__main__":
    app.run_server(debug=True)
