import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

from src.enums.enums_heatmap import (
    ASC_METRICS,
    COLORS,
    METRICS,
    MODELS,
    MODELS_TO_GROUP,
    OLD_TO_NEW,
    ORDER_MODELS,
    PAPER_METRICS,
    RNA_NAMES,
    SUB_METRICS,
    PAPER_SUP_METRICS,
)


class VizHeatmap:
    def __init__(self, csv_folder: str):
        self.csv_folder = csv_folder
        self.scores_df = self._get_df_clean(csv_folder)

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
        scores_df: Dict = {"RNA_name": [], "Metric": [], "Metric_name": [], "Model": []}
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

    def _update_fig_box_plot(self, fig: Any, is_complete: bool = True) -> Any:
        fig.update_yaxes(matches=None, showticklabels=True)
        params_axes = dict(
            showgrid=True,
            gridcolor="#d6d6d6",
            linecolor="black",
            zeroline=False,
            linewidth=1,
            showline=True,
            mirror=True,
            gridwidth=1,
            griddash="dot",
            title=None,
        )
        fig.update_xaxes(**params_axes)
        fig.update_yaxes(**params_axes)
        fig.update_xaxes(
            tickangle=45,
        )
        fig.update_layout(dict(plot_bgcolor="white"), margin=dict(l=0, r=5, b=0, t=20))
        param_marker = dict(
            opacity=1, line=dict(width=0.5, color="DarkSlateGrey"), size=6
        )
        fig.update_traces(marker=param_marker, selector=dict(mode="markers"))
        for annotation in fig["layout"]["annotations"]:
            annotation["text"] = annotation["text"].replace("Metric_name=", "")
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=18,  # Set the font size here
            )
        )
        fig.update_layout(
            legend=dict(
                orientation="v",
                bgcolor="#f3f3f3",
                bordercolor="Black",
                borderwidth=1,
            ),
        )
        fig.update_xaxes(visible=True, showticklabels=False)
        if not is_complete:
            fig.update_layout(
                legend=dict(
                    yanchor="top", xanchor="right", x=0.41, y=-0.18, orientation="h"
                ),
            )
        return fig

    def _box_plot_by_method(self, metrics: List[str], name: str):
        df = self._get_df_box_plot_ready(metrics=metrics)
        df = df.rename(columns={"Category": "Method"})
        fig = px.box(
            df,
            x="Model",
            y="Metric",
            color="Method",
            facet_col="Metric_name",
            facet_col_wrap=4,
            facet_row_spacing=0.19,
            facet_col_spacing=0.05,
            color_discrete_map=COLORS,
            category_orders={
                "Model": ORDER_MODELS,
                "Metric_name": [x for x in METRICS if x in metrics],
            },
        )
        fig = self._update_fig_box_plot(fig, is_complete=False)
        fig.update_xaxes(showticklabels=True)
        fig.update_traces(width=0.6)
        for data in fig.data:
            data["marker"] = dict(color="#000000", opacity=1, size=8)
        for cat, color in COLORS.items():
            fig.update_traces(fillcolor=color, selector=dict(name=cat))
        fig.update_layout(
            width=1400,
            height=900,
        )
        return fig

    def plot_box_plot(self):
        return self._box_plot_by_method(PAPER_METRICS + PAPER_SUP_METRICS, name="all")

    def _get_df_box_plot_ready(self, metrics: List = SUB_METRICS) -> pd.DataFrame:
        """Return the df used for box plots"""
        df = self.scores_df[self.scores_df["Metric_name"].isin(metrics)]
        # Take only the best model for each RNA
        df = df[df["Model"].isin(MODELS)]
        return df

    def normalize_metric(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise the different metrics
        :param df:
        :return:
        """
        normalized_metrics = []
        for metric in df["Metric_name"].unique():
            col = df[df["Metric_name"] == metric]["Metric"]
            normalized_metrics.extend((col - col.min()) / (col.max() - col.min()))
        df["Normalized_Metric"] = normalized_metrics
        return df

    def convert_to_heatmap(self, df: pd.DataFrame) -> np.ndarray:
        all_dfs = []
        for i_model, model in enumerate(MODELS):
            df_model = df[df["Model"] == model]
            pivot_df = df_model.pivot(
                index="RNA_name", columns="Metric_name", values="Normalized_Metric"
            )
            c_df = np.nan * np.ones((len(RNA_NAMES), len(METRICS)))
            for i_name, rna_name in enumerate(RNA_NAMES):
                try:
                    c_df[i_name, :] = pivot_df[pivot_df.index == rna_name].values[0]
                except IndexError:
                    continue
            all_dfs.append(c_df)
        output = np.array(all_dfs)
        return output

    def _get_heat_maps(self, metrics):
        heatmaps = []
        for metric in metrics:
            heatmaps.append(self._get_heat_map(metric))
        return heatmaps

    def _get_heat_map(self, metric: str):
        df = self.scores_df[self.scores_df["Metric_name"].isin(METRICS)]
        # Take only the best model for each RNA
        df = df[df["Model"].isin(MODELS)]
        df = df[df["Metric_name"].isin(METRICS)]
        df = df[df["Metric_name"] == metric]
        pivot_df = df.pivot(index="RNA_name", columns="Model", values="Metric")
        pivot_df = pivot_df.reindex(columns=ORDER_MODELS)
        return pivot_df

    def _heat_map(self, metric: str):
        df = self.scores_df[self.scores_df["Metric_name"].isin(METRICS)]
        # Take only the best model for each RNA
        df = df[df["Model"].isin(MODELS)]
        df = df[df["Metric_name"].isin(METRICS)]
        df = df[df["Metric_name"] == metric]
        pivot_df = df.pivot(index="RNA_name", columns="Model", values="Metric")
        fig = px.imshow(
            pivot_df,
        )
        params_axes = dict(
            showgrid=True,
            gridcolor="#d6d6d6",
            linecolor="black",
            zeroline=False,
            linewidth=1,
            showline=True,
            mirror=True,
            gridwidth=1,
            griddash="dot",
            title=None,
        )
        fig.update_xaxes(**params_axes)
        fig.update_yaxes(**params_axes)
        fig.update_layout(dict(plot_bgcolor="white"), margin=dict(l=0, r=5, b=0, t=20))
        param_marker = dict(
            opacity=1, line=dict(width=0.5, color="DarkSlateGrey"), size=6
        )
        fig.update_traces(marker=param_marker, selector=dict(mode="markers"))
        fig.update_layout(coloraxis_colorbar_x=0.58)
        save_path = os.path.join("data", "plots", "heatmap", f"heatmap_{metric}.png")
        fig.write_image(save_path, scale=2)

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

    def plot_heatmaps(self):
        return self.plot_heatmap_t_paper(PAPER_METRICS + PAPER_SUP_METRICS)

    def _plot_heatmap_update_xaxes(self, fig, row, col):
        fig.update_xaxes(
            row=row,
            col=col,
            showline=True,
            showticklabels=True,
            tickfont=dict(size=12),
            tickangle=45,
        )
        return fig

    def _plot_heatmap_update_yaxes(self, fig, row, col):
        fig.update_yaxes(
            row=row,
            col=col,
            showline=True,
            showticklabels=True,
            nticks=len(RNA_NAMES),
            tickangle=0,
            tickfont=dict(size=12),
        )
        return fig

    def update_colorbar_position(self, fig):
        pos_x = [0.425, 0.999]
        pos_y = [0.905, 0.635, 0.365, 0.09]
        positions = [
            (pos_x[0], pos_y[0]),
            (pos_x[1], pos_y[0]),
            (pos_x[0], pos_y[1]),
            (pos_x[1], pos_y[1]),
            (pos_x[0], pos_y[2]),
            (pos_x[1], pos_y[2]),
            (pos_x[0], pos_y[3]),
            (pos_x[1], pos_y[3]),
        ]
        color_all_axis = {
            f"coloraxis{i}": dict(
                colorbar_x=positions[i - 1][0],
                colorbar_y=positions[i - 1][1],
                colorbar_thickness=15,
                colorbar_len=0.2,
            )
            for i in range(1, 9)
        }
        fig.update_layout(width=900, height=900, **color_all_axis)
        return fig

    def plot_heatmap_t_paper(self, metrics: List, is_supp: bool = False):
        # Create a subplot with three rows and three columns
        n_rows, n_cols = 4, 2
        fig = sp.make_subplots(
            rows=n_rows,
            cols=n_cols,
            horizontal_spacing=0.15,
            vertical_spacing=0.08,
            subplot_titles=metrics,
        )
        heatmaps = self._get_heat_maps(metrics)
        heatmaps = [x.T for x in heatmaps]
        for row in range(n_rows):
            for col in range(n_cols):
                index = row * n_cols + col
                data = heatmaps[index]
                heatmap = go.Heatmap(
                    z=data,
                    y=data.index,
                    x=data.columns,
                    colorbar=dict(thickness=50, len=4),
                    reversescale=metrics[index] not in ASC_METRICS,
                    coloraxis=f"coloraxis{row * 2 + col + 1}",
                )
                fig.add_trace(heatmap, row=row + 1, col=col + 1)
                fig = self._plot_heatmap_update_xaxes(fig, row + 1, col + 1)
                fig = self._plot_heatmap_update_yaxes(fig, row + 1, col + 1)
                fig.update_coloraxes(colorscale="viridis", row=row + 1, col=col + 1)
        fig = self._clean_fig(fig)
        fig = self.update_colorbar_position(fig)
        fig.update_annotations(font_size=16)
        return fig

    def plot_heatmap_t(self, metrics: List, name: str):
        # Create a subplot with three rows and three columns
        metrics = [x for x in metrics if x not in PAPER_METRICS]
        fig = sp.make_subplots(
            rows=1,
            cols=2,
            horizontal_spacing=0.11,
            vertical_spacing=0.13,
            subplot_titles=metrics,
        )  # Adjust width
        len_color = 0.4
        positions = [(i, j) for j in [0.77, 0.22] for i in [0.44, 0.999]]
        heatmaps = self._get_heat_maps(metrics)
        heatmaps = [x.T for x in heatmaps]
        colorscale = "Viridis" if name == "ascending_metrics" else "thermal"
        for i, (data, position) in enumerate(zip(heatmaps, positions)):
            heatmap = go.Heatmap(
                z=data,
                y=data.index,
                x=data.columns,
                colorbar=dict(
                    y=position[1], x=position[0], thickness=10, len=len_color
                ),
                colorscale=colorscale,
            )
            row, col = i // 2 + 1, i % 2 + 1
            fig.add_trace(heatmap, row=row, col=col)
            fig.update_xaxes(
                row=row,
                col=col,
                showline=True,
                showticklabels=True,
                tickfont=dict(size=12),
                tickangle=45,
            )
            fig.update_yaxes(
                row=row,
                col=col,
                showline=True,
                showticklabels=True,
                nticks=len(RNA_NAMES),
                tickangle=0,
                tickfont=dict(size=12),
            )
        fig = self._clean_fig(fig)
        fig.update_annotations(font_size=16)
        return fig
