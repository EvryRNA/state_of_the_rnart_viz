import os

from src.viz.viz_box import VizBox
from src.viz.viz_heat import VizHeat


class VizCLI:
    def __init__(self, csv_folder: str):
        self.csv_folder = csv_folder
        self.benchmark = os.path.basename(csv_folder)

    def run(self):
        viz_box = VizBox(self.csv_folder, self.benchmark)
        viz_box.box_plot_by_method()
        viz_heat = VizHeat(self.csv_folder, self.benchmark)
        viz_heat.plot_heatmaps()
        viz_heat.summary_table()


if __name__ == "__main__":
    csv_folder = os.path.join("docker_data", "output", "RNA_PUZZLES")
    viz_cli = VizCLI(csv_folder)
    viz_cli.run()
