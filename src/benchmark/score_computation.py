import os

DOCKER_COMMAND = (
    "docker run -it -v ${PWD}/docker_data/:/app/docker_data "
    "-v ${PWD}/tmp:/tmp rnadvisor --pred_path $PRED_PATH "
    "--native_path $NATIVE_PATH --result_path $OUTPUT_PATH "
    "--log_path $LOG_PATH --time_path $TIME_PATH "
    "--all_scores=ALL"
)


class ScoreComputation:
    def __init__(self, native_paths: str, preds_paths: str, output_path: str):
        self.native_paths = native_paths
        self.preds_paths = preds_paths
        self.output_path = output_path
        self.log_path = os.path.join("docker_data", "logs")
        self.time_path = os.path.join("docker_data", "time")

    def run_benchmark(self):
        """
        Compute scores for all the predictions.
        """
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.time_path, exist_ok=True)
        for challenge in os.listdir(self.native_paths):
            pred_path = os.path.join(self.preds_paths, challenge.replace(".pdb", ""))
            if os.path.isdir(pred_path):
                native_path = os.path.join(self.native_paths, challenge)
                output_path = os.path.join(
                    self.output_path, challenge.replace(".pdb", ".csv")
                )
                log_path = os.path.join(
                    self.log_path, challenge.replace(".pdb", ".log")
                )
                time_path = os.path.join(
                    self.time_path, challenge.replace(".pdb", "_time.csv")
                )
                self.compute_challenge(
                    native_path, pred_path, output_path, log_path, time_path
                )

    def compute_challenge(
        self,
        native_path: str,
        pred_path: str,
        output_path: str,
        log_path: str,
        time_path: str,
    ):
        """
        Run the docker command to compute all the metrics
        :return:
        """
        command = (
            DOCKER_COMMAND.replace("$PRED_PATH", pred_path)
            .replace("$NATIVE_PATH", native_path)
            .replace("$OUTPUT_PATH", output_path)
            .replace("$LOG_PATH", log_path)
            .replace("$TIME_PATH", time_path)
        )
        os.system(command)


if __name__ == "__main__":
    # To compute challenge for all the benchmarks
    prefix = os.path.join("docker_data", "input")
    for dataset in ["RNA_PUZZLES", "RNASOLO", "CASP_RNA"]:
        NATIVE_PATHS = os.path.join(prefix, dataset, "NATIVE")
        PREDS_PATHS = os.path.join(prefix, dataset, "PREDS")
        OUTPUT_PATH = os.path.join(prefix.replace("input", "output"), "RNA_PUZZLES")
        score_computation = ScoreComputation(NATIVE_PATHS, PREDS_PATHS, OUTPUT_PATH)
        score_computation.run_benchmark()
