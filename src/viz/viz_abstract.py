import os
from typing import Dict

import numpy as np
import pandas as pd

from src.viz.enum import (
    MODELS,
    MODELS_TO_GROUP,
    OLD_TO_NEW,
    PAPER_SUP_METRICS, RNA_NAMES, CASP_RNA_NAMES, RNA_CHALLENGES_LENGTH_SORTED,
    CASP_RNA_CHALLENGES_LENGTH_SORTED,
)


class VizAbstract:
    def __init__(self, csv_folder: str, benchmark: str):
        """

        :param csv_folder: folder to the csv files with the different metrics
        :param benchmark: either "RNA_PUZZLES" or "CASP_RNA"
        """
        self.csv_folder = csv_folder
        self.benchmark = benchmark
        self.scores_df = self._get_df_clean(csv_folder)
        self.save_path_dir = os.path.join("docker_data", "plots")
        self.plot_type = None # To be completed by the subclasses
        self.rna_names = RNA_NAMES if benchmark == "RNA_PUZZLES" else CASP_RNA_NAMES
        self.rna_lengths = RNA_CHALLENGES_LENGTH_SORTED  if benchmark == "RNA_PUZZLES" else CASP_RNA_CHALLENGES_LENGTH_SORTED

    def add_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a column with the category of the model
        """
        df["Category"] = df["Model"].apply(lambda x: MODELS_TO_GROUP.get(x, "Other"))
        return df

    def _get_df_clean(self, csv_folder: str):
        """
        Prepare dataframe to plotly format. It adds a column with the model name and RNA name.
        :param csv_folder:
        :return:
        """
        scores_df: Dict = {
            "RNA_name": [],
            "Metric": [],
            "Metric_name": [],
            "Model": [],
            "Full_path": [],
        }
        print(f"Csv folder: {csv_folder}")
        for csv_file in os.listdir(csv_folder):
            if csv_file.endswith(".csv"):
                df = pd.read_csv(os.path.join(csv_folder, csv_file), index_col=[0])
                df = self._get_model_name(df)
                rna_name = csv_file.replace(".csv", "")
                for metric in df.columns:
                    if metric != "Model":
                        scores_df["RNA_name"].extend(len(df) * [rna_name])
                        scores_df["Metric"].extend(df[metric].values)
                        scores_df["Metric_name"].extend(len(df) * [metric])  # type: ignore
                        scores_df["Model"].extend(df["Model"].values)
                        scores_df["Full_path"].extend(df.index)
        scores_df = pd.DataFrame(scores_df)
        scores_df = self._change_name(scores_df)
        scores_df = self.add_category(scores_df)
        mask = (
            (scores_df["Metric_name"] == "INF-ALL") | (scores_df["Metric_name"] == "DI")
        ) & (scores_df["Model"] == "epRNA")
        # Use the boolean mask to drop the rows
        scores_df.loc[mask, "Metric"] = np.nan  # type: ignore
        return scores_df

    def _change_name(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Change the name of the models and some metrics
        :param df:
        :return:
        """
        for old_value, new_value in OLD_TO_NEW.items():
            df = df.replace(old_value, new_value)
        return df

    def _get_model_name(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get the model names and keep only the one row per model, the one with the best RMSD score
        It adds a column with the model name
        :param df:
        :return:
        """
        names = df.index.values
        model_names = {name: name.split("_")[1] for name in names}
        new_names, new_model_names = [], []
        for name, model_name in model_names.items():
            if model_name not in new_model_names:
                new_names.append(name)
                new_model_names.append(model_name)
        df = df.loc[new_names]
        df["Model"] = new_model_names
        return df

    def summary_table(self):
        scores_df = self.scores_df[self.scores_df["Model"].isin(MODELS)]
        df = (
            scores_df[["Metric", "Metric_name", "Model"]]
            .groupby(["Metric_name", "Model"], as_index=False)
            .mean()
        )
        df = df.pivot(index="Metric_name", columns="Model", values="Metric").T
        df_supp, df_paper = (
            df[PAPER_SUP_METRICS],
            df[
                [
                    "RMSD",
                    "εRMSD",
                    "DI",
                    "P-VALUE",
                    "TM-score",
                    "GDT-TS",
                    "INF-ALL",
                    "lDDT",
                ]
            ],
        )
        path_to_supp = os.path.join(self.save_path_dir, "table", f"{self.benchmark}_supplementary_results.csv")
        path_to_save_paper = path_to_supp.replace("supplementary_results", "results_paper")
        df_supp.to_csv(path_to_supp)
        df_paper.to_csv(path_to_save_paper)

    def _clean_fig(self, fig):
        fig.update_annotations(font_size=10)
        params_axes = dict(
            showgrid=True,
            gridcolor="grey",
            linecolor="black",
            zeroline=False,
            linewidth=1,
            showline=True,
            mirror=True,
            gridwidth=1,
            griddash="dot",
            tickson="boundaries",
        )
        fig.update_yaxes(**params_axes)
        fig.update_xaxes(**params_axes)
        fig.update_layout(
            dict(plot_bgcolor="white"), margin=dict(l=10, r=5, b=10, t=20)
        )
        param_marker = dict(
            opacity=1, line=dict(width=0.5, color="DarkSlateGrey"), size=6
        )
        fig.update_traces(marker=param_marker, selector=dict(mode="markers"))
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=10,  # Set the font size here
            )
        )
        return fig
