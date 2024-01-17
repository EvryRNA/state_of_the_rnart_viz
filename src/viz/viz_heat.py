from typing import Any

from src.enums.enums_heatmap import (
    PAPER_METRICS,
    PAPER_SUP_METRICS,
    RNA_NAMES,
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
        self.positions = [
            (0.308, 0.77),
            (0.655, 0.77),
            (0.9999, 0.77),
            (0.308, 0.23),
            (0.655, 0.23),
            (0.9999, 0.23),
        ]
        self.metrics = PAPER_METRICS + PAPER_SUP_METRICS

    def plot_heatmaps(self):
        return self.plot_box_plot()

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
            nticks=len(RNA_NAMES),
            tickangle=0,
            tickfont=dict(size=20),
        )
        return fig

    def plot_box_plot(self, n_row=2, n_col=3, len_color=0.45, horizontal_spacing=0.04):
        # Create a subplot with three rows and three columns
        fig = sp.make_subplots(
            rows=n_row,
            cols=n_col,
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=0.09,
            subplot_titles=[x.replace("INF-ALL", "INF") for x in self.metrics],
        )  # Adjust width
        heatmaps = self._get_heat_maps(self.metrics)
        heatmaps = [x.T[RNA_NAMES] for x in heatmaps]  # To select RNA challenges order
        for row in range(n_row):
            for col in range(n_col):
                index = row * n_col + col
                data = heatmaps[index]
                position = self.positions[index]
                columns = [
                    f"{rna} ({RNA_CHALLENGES_LENGTH[rna]} nt)" for rna in data.columns
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
                    reversescale=self.metrics[index] not in ASC_METRICS,
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
        return fig

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
