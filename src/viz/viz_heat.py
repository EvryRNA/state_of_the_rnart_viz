import os
from typing import List, Any

from src.viz.enum import (
    PAPER_METRICS,
    PAPER_SUP_METRICS,
    ASC_METRICS,
    MODELS,
    METRICS,
    ORDER_MODELS,
    RNA_CHALLENGES_LENGTH,
)
from src.viz.viz_abstract import VizAbstract
import plotly.subplots as sp
import plotly.graph_objects as go


class VizHeat(VizAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_type = "heatmap"
        self.save_path_full = os.path.join(self.save_path_dir, self.plot_type)

    def plot_heatmaps(self):
        positions = [
            (0.308, 0.77),
            (0.655, 0.77),
            (0.9999, 0.77),
            (0.308, 0.23),
            (0.655, 0.23),
            (0.9999, 0.23),
        ]
        self.plot_heatmap_t_paper(
            PAPER_METRICS,
            positions,
            width=2000,
            height=700,
            n_row=2,
            n_col=3 if self.benchmark == "RNA_PUZZLES" else 2,
        )
        positions = [(0.475, 0.5), (0.999, 0.5)]
        self.plot_heatmap_t_paper(
            PAPER_SUP_METRICS,
            positions,
            is_supp=True,
            n_row=1,
            n_col=2,
            width=1400,
            height=350,
            len_color=1,
            horizontal_spacing=0.05,
        )

    def _update_axes_heatmap(self, fig: Any, row, col):
        fig.update_xaxes(
            row=row,
            col=col,
            showline=True,
            showticklabels=True,
            tickfont=dict(size=20),
            tickangle=90,
        )
        fig.update_yaxes(
            row=row,
            col=col,
            showline=True,
            showticklabels=True,
            nticks=len(self.rna_names),
            tickangle=0,
            tickfont=dict(size=20),
        )
        return fig

    def convert_heatmap(self, heatmaps: List):
        """
        Convert heatmap by translatin and select the RNAs sorted by sequence length
        :param heatmaps:
        :return:
        """
        new_heatmaps = []
        for heatmap in heatmaps:
            try:
                new_heatmaps.append(heatmap.T[self.rna_names])
            except KeyError:
                continue
        return new_heatmaps

    def plot_heatmap_t_paper(
        self,
        metrics: List,
        positions,
        is_supp: bool = False,
        n_row=2,
        n_col=3,
        len_color=0.45,
        width=1400,
        height=800,
        horizontal_spacing=0.04,
    ):
        # Create a subplot with three rows and three columns
        fig = sp.make_subplots(
            rows=n_row,
            cols=n_col,
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=0.09,
            subplot_titles=[x.replace("INF-ALL", "INF") for x in metrics],
        )  # Adjust width
        heatmaps = self._get_heat_maps(metrics)
        heatmaps = self.convert_heatmap(heatmaps)
        for row in range(n_row):
            for col in range(n_col):
                index = row * n_col + col
                data = heatmaps[index]
                position = positions[index]
                columns = [
                    f"{rna} ({self.rna_lengths[rna]} nt)" for rna in data.columns
                ]
                heatmap = go.Heatmap(
                    z=data,
                    y=data.index,
                    x=columns,
                    colorbar=dict(
                        y=position[1],
                        x=position[0],
                        thickness=20,
                        len=len_color,
                        tickfont=dict(size=16),
                    ),
                    colorscale="Viridis",
                    reversescale=metrics[index] not in ASC_METRICS,
                )
                fig.add_trace(
                    heatmap,
                    row=row + 1,
                    col=col + 1,
                )
                fig = self._update_axes_heatmap(fig, row + 1, col + 1)
                if col != 0:
                    fig.update_yaxes(showticklabels=False, row=row + 1, col=col + 1)
                if row != 1 and n_row != 1:
                    fig.update_xaxes(showticklabels=False, row=row + 1, col=col + 1)
        fig = self._clean_fig(fig)
        fig.update_annotations(font_size=24)
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
        )
        name = "supp_" if is_supp else ""
        save_path = os.path.join(
            self.save_path_full, f"{name}{self.benchmark}_heatmap.png"
        )
        fig.write_image(save_path, scale=4, width=width, height=height)

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
