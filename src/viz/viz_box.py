import os
from typing import List, Any

import pandas as pd
import plotly.express as px

from src.viz.enum import (
    PAPER_METRICS,
    COLORS,
    ORDER_MODELS,
    METRICS,
    SUB_METRICS,
    MODELS,
)
from src.viz.viz_abstract import VizAbstract


class VizBox(VizAbstract):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_type = "boxplot"
        self.save_path_full = os.path.join(self.save_path_dir, self.plot_type)

    def box_plot_by_method(self):
        self._box_plot_by_method(width=1200, height=600)

    def _box_plot_by_method(
        self,
        width: int = 1200,
        height: int = 800,
        legend_coordinates=(0.43, -0.25),
    ):
        metrics = PAPER_METRICS
        df = self._get_df_box_plot_ready(metrics=metrics)
        df = df.rename(columns={"Category": "Method"}).replace({"INF-ALL": "INF"})
        if "casp" in self.benchmark.lower():
            df = df[df["Model"] != "MC-Sym"]
        fig = px.box(
            df,
            x="Model",
            y="Metric",
            color="Method",
            facet_col="Metric_name",
            facet_col_wrap=3,
            facet_row_spacing=0.06,
            facet_col_spacing=0.05,
            color_discrete_map=COLORS,
            category_orders={
                "Model": ORDER_MODELS,
                "Metric_name": [x.replace("INF-ALL", "INF") for x in metrics],
            },
        )
        fig = self._update_fig_box_plot(
            fig, is_complete=False, legend_coordinates=legend_coordinates
        )
        fig.update_xaxes(showticklabels=True)
        fig.update_traces(width=0.3)
        for data in fig.data:
            data["marker"] = dict(color="#000000", opacity=1, size=8)
        for cat, color in COLORS.items():
            fig.update_traces(fillcolor=color, selector=dict(name=cat))
        for col in range(1, 4):
            fig.update_xaxes(showticklabels=False, row=3, col=col)
            fig.update_xaxes(showticklabels=False, row=4, col=col)
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        save_path = os.path.join(self.save_path_full, f"{self.benchmark}_box.png")
        fig.write_image(save_path, scale=2, width=width, height=height)

    def _get_df_box_plot_ready(self, metrics: List = SUB_METRICS) -> pd.DataFrame:
        """Return the df used for box plots"""
        df = self.scores_df[self.scores_df["Metric_name"].isin(metrics)]
        # Take only the best model for each RNA
        df = df[df["Model"].isin(MODELS)]
        return df

    def _update_fig_box_plot(
        self, fig: Any, is_complete: bool = True, legend_coordinates=(0.43, -0.25)
    ) -> Any:
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
                    yanchor="top",
                    xanchor="right",
                    x=legend_coordinates[0],
                    y=legend_coordinates[1],
                    orientation="h",
                ),
            )
        return fig
