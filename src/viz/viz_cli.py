import os
from typing import List

from src.viz.viz_box import VizBox
from src.viz.viz_heat import VizHeat
from src.viz.viz_polar import VizPolar


class VizCLI:
    def __init__(self, csv_folder: str):
        self.csv_folder = csv_folder
        self.benchmark = os.path.basename(csv_folder)

    def run(self):
        pass
        # viz_box = VizBox(self.csv_folder, self.benchmark)
        # viz_box.box_plot_by_method()
        viz_heat = VizHeat(self.csv_folder, self.benchmark)
        # viz_heat.plot_heatmaps()
        viz_heat.summary_all_table()

    @staticmethod
    def run_benchmark(benchmark: str):
        csv_folder = os.path.join("docker_data", "output", benchmark)
        viz_cli = VizCLI(csv_folder)
        viz_cli.run()

    @staticmethod
    def run_all_benchmark(benchmarks: List):
        in_paths = {
            name: os.path.join("docker_data", "output", name) for name in benchmarks
        }
        viz_polar = VizPolar(in_paths)
        viz_polar.viz()


if __name__ == "__main__":
    benchmarks = ["CASP_RNA", "RNA_PUZZLES", "RNASOLO"]
    for benchmark in benchmarks:
        VizCLI.run_benchmark(benchmark)
    # VizCLI.run_all_benchmark(benchmarks)
