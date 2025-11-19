#!/usr/bin/env python3

import os
from time import perf_counter
import logging
import yaml
import metcalcpy.util.read_env_vars_in_config as readconfig
from metplotpy.plots.wind_rose import wind_rose

def main():

    # Read the input files
    yaml_files_str = os.environ['WIND_ROSE_YAML_CONFIG_FILE_LIST'].split(',')
    yaml_files = [yf.lstrip() for yf in yaml_files_str]
    yaml_file_dir = os.environ['WIND_ROSE_YAML_CONFIG_DIR']
    plot_input_dir = os.environ['WIND_ROSE_STAT_INPUT_DIR']
    plot_input_files_list_str = os.environ['WIND_ROSE_STAT_INPUT_FILES'].split(',')
    plot_input_files_list = [pi.lstrip() for pi in plot_input_files_list_str]
    plot_output_dir = os.environ['WIND_ROSE_OUTPUT_DIR']
    plot_output_file_labels_str = os.environ['WIND_ROSE_OUTPUT_LABELS'].split(',')
    plot_output_file_labels = [ol.lstrip() for ol in plot_output_file_labels_str]

    # Check to see that the two lists have the same number of elements
    # If they dont', error out
    if len(plot_input_files_list) != len(plot_output_file_labels):
        raise RuntimeError('The number of files in WIND_ROSE_STAT_INPUT_FILES must be equal to the number of labels in WIND_ROSE_OUTPUT_LABELS')


    # Loop through data
    for f,l in zip(plot_input_files_list,plot_output_file_labels):
        os.environ['WIND_ROSE_STAT_INPUT'] = os.path.join(plot_input_dir,f)

        os.environ['WIND_ROSE_OUTPUT_LABEL'] = l

        for i in yaml_files:

            os.environ['WIND_ROSE_YAML_CONFIG_NAME'] = os.path.join(yaml_file_dir,i)

            # Read in the YAML configuration file.  Environment variables in
            # the configuration file are supported.
            try:
                input_config_file = os.getenv("WIND_ROSE_YAML_CONFIG_NAME", "custom_wind_rose.yaml")
                settings = readconfig.parse_config(input_config_file)
                logging.info(settings)
            except yaml.YAMLError as exc:
                logging.error(exc)

            #try:
            start = perf_counter()
            plot = wind_rose.WindRosePlot(settings)
            plot.save_to_file()
            plot.write_output_file()
            end = perf_counter()
            execution_time = end - start
            plot.logger.info(f"Finished creating wind rose plot, execution time: {execution_time} seconds")
            #except ValueError as val_er:
            #    print(val_er)

if __name__ == "__main__":
  main()
