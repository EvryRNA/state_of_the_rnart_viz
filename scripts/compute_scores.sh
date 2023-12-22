#!/bin/bash

INPUT_DIR="docker_data/input";
OUTPUT_DIR="docker_data/output"
PREDS="PREDS";
NATIVE="NATIVE";

function compute_scores_from_rna_scoring(){
  pdb_names=$(ls "${INPUT_DIR}/$1/${PREDS}/");
  for name in ${pdb_names}; do
    path_to_native=${INPUT_DIR}/$1/${NATIVE}/${name}.pdb;
    path_to_pred=${INPUT_DIR}/$1/PREDS/${name};
    path_to_output=${OUTPUT_DIR}/$1/${name}.csv;
    echo "$path_to_native $path_to_pred $path_to_output";
    mkdir -p ${OUTPUT_DIR}/$1;
    docker run -it -v ${PWD}/docker_data/:/app/docker_data -v ${PWD}/tmp:/tmp rna_scores --native_path=$path_to_native --pred_path=$path_to_pred --result_path=$path_to_output --all_scores=ALL
  done

}

compute_scores_from_rna_scoring "RNA_PUZZLES";
#compute_scores_from_rna_scoring "CASP_RNA";
