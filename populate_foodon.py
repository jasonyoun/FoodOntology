"""
Authors:
    Jason Youn - jyoun@ucdavis.edu
    Simon Kit Sang, Chu - kschu@ucdavis.edu

Description:
    Preprocess the FDC data.

To-do:
"""
# standard imports
import argparse
import logging as log

# local imports
from managers.parse_foodon import ParseFoodOn
from managers.scoring import ScoringManager
from utils.config_parser import ConfigParser
from utils.set_logging import set_logging

# global variables
DEFAULT_CONFIG_FILE = './config/populate_foodon.ini'


def parse_argument():
    """
    Parse input arguments.

    Returns:
        - parsed arguments
    """
    parser = argparse.ArgumentParser(description='Populate FoodON.')

    parser.add_argument(
        '--config_file',
        default=DEFAULT_CONFIG_FILE,
        help='Path to the .ini configuration file.')

    return parser.parse_args()


def grid_search(classes_dict_skeleton, candidate_entities, configparser):
    log.info('Performing grid search.')

    # get list of hyper-parameters to use for running grid search
    alpha_list = [float(alpha) for alpha in configparser.get_str_list('alpha')]
    N_list = [int(N) for N in configparser.get_str_list('num_mapping_per_iteration')]

    iteration = 1
    total_iterations = len(alpha_list) * len(N_list)

    for alpha in alpha_list:
        for num_mapping in N_list:
            log.info('Running grid search %d/%d: (alpha: %f, N: %d)',
                     iteration, total_iterations, alpha, num_mapping)

            # overwrite scoring config for grid search
            scoring_config = ConfigParser(configparser.getstr('scoring_config'))

            scoring_config.overwrite('alpha', str(alpha))
            scoring_config.overwrite('num_mapping_per_iteration', str(num_mapping))

            siblings_scores = scoring_config.getstr('initial_siblings_scores')
            parents_scores = scoring_config.getstr('initial_parents_scores')
            scoring_config.overwrite('initial_siblings_scores', siblings_scores)
            scoring_config.overwrite('initial_parents_scores', parents_scores)

            pairs_filepath = scoring_config.getstr('pairs_filepath')
            populated_filepath = scoring_config.getstr('populated_filepath')
            pairs_filepath = pairs_filepath.replace(
                '.pkl', '_alpha{}_N{}.pkl'.format(alpha, num_mapping))
            populated_filepath = populated_filepath.replace(
                '.pkl', '_alpha{}_N{}.pkl'.format(alpha, num_mapping))
            scoring_config.overwrite('pairs_filepath', pairs_filepath)
            scoring_config.overwrite('populated_filepath', populated_filepath)

            # run population
            scoring_manager = ScoringManager(
                classes_dict_skeleton,
                candidate_entities,
                configparser.getstr('preprocess_config'),
                scoring_config)

            scoring_manager.run_iteration()

            iteration += 1


def main():
    """
    Main function.
    """
    # set log, parse args, and read configuration
    args = parse_argument()
    configparser = ConfigParser(args.config_file)
    set_logging(configparser.getstr('logfile'))

    # parse FoodOn
    parse_foodon = ParseFoodOn(configparser.getstr('foodon_parse_config'))
    classes_dict = parse_foodon.get_candidate_classes()
    classes_dict_skeleton, candidate_entities = parse_foodon.get_seeded_skeleton(classes_dict)

    # run
    if configparser.getbool('grid_search'):
        grid_search(classes_dict_skeleton, candidate_entities, configparser)
    else:
        scoring_manager = ScoringManager(
            classes_dict_skeleton,
            candidate_entities,
            configparser.getstr('preprocess_config'),
            configparser.getstr('scoring_config'))

        scoring_manager.run_iteration()


if __name__ == '__main__':
    main()
