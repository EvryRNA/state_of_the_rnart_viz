import os
from typing import List, Any

from src.viz.enum import (
    ASC_METRICS,
    MODELS,
    METRICS,
    ORDER_MODELS,
    PAPER_METRICS,
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
        """
        Plot the heatmap visualiation
        :param name: Name of the benchmark
        :return:
        """
        positions = [
            (0.315, 0.9),
            (0.66, 0.9),
            (0.9999, 0.9),
            (0.315, 0.635),
            (0.66, 0.635),
            (0.9999, 0.635),
            (0.315, 0.365),
            (0.66, 0.365),
            (0.9999, 0.365),
            (0.315, 0.1),
        ]
        self.plot_heatmap_t_paper(positions, width=2600, height=2000)

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
            nticks=len(self.rna_lengths),
            tickangle=0,
            tickfont=dict(size=20),
        )
        return fig

    def plot_heatmap_t_paper(
        self,
        positions,
        n_row=4,
        n_col=3,
        len_color=0.2,
        width=3000,
        height=800,
        horizontal_spacing=0.03,
    ):
        metrics = PAPER_METRICS
        fig = sp.make_subplots(
            rows=n_row,
            cols=n_col,
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=0.07,
            subplot_titles=[x.replace("INF-ALL", "INF") for x in metrics],
        )
        heatmaps = self._get_heat_maps(metrics)
        heatmaps = [
            x.T[self.rna_names] for x in heatmaps
        ]  # To select RNA challenges order
        for row in range(n_row):
            for col in range(n_col):
                index = row * n_col + col
                if index >= len(heatmaps):
                    break
                data = heatmaps[index]
                position = positions[index]
                if "casp" in self.benchmark.lower():
                    data = data.drop("MC-Sym", axis=0)
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
                if row != n_row - 1:
                    fig.update_xaxes(showticklabels=False, row=row + 1, col=col + 1)
                if col != 0 and row == n_row - 2:
                    fig.update_xaxes(showticklabels=True, row=row + 1, col=col + 1)

        fig = self._clean_fig(fig)
        fig.update_annotations(font_size=24)
        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
        )
        save_path = os.path.join(
            "docker_data", "plots", "heatmap", f"{self.benchmark}_heatmap.png"
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
