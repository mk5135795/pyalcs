import argparse
import logging

import gym
import gym_maze

import matplotlib.pyplot as plt
import numpy as np

from examples.acs2.maze.utils import maze_knowledge
from lcs.agents.acs2 import ACS2, Configuration
from lcs.agents.acs2.plot import Plots as pl

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def maze_metrics(population, environment):
    return {
        'population': len(population),
        'knowledge': maze_knowledge(population, environment)
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--environment", default="Maze4-v0")
    parser.add_argument("--epsilon", default=1.0, type=float)
    parser.add_argument("--ga", action="store_true")
    parser.add_argument("--explore-trials", default=50, type=int)
    parser.add_argument("--exploit-trials", default=10, type=int)
    args = parser.parse_args()

    maze = gym.make(args.environment)

    freq = 10
    plot = pl.Plots('conf.txt', freq)
    cfg = Configuration(8, 8,
                        epsilon=args.epsilon,
                        do_ga=args.ga,
                        user_metrics_collector_fcn=plot.get_logger(),
                        metrics_trial_frequency=freq)

    agent = ACS2(cfg)
    for i in range(3):
        population, m = agent.explore(maze, 200, decay=False)
        plot.add_data("mix", f'explore {i+1}', m)
        population, m = agent.exploit(maze, 200)
        plot.add_data("mix", f'exploit {i+1}', m)
    plot.add_data("mix_no_div", '')
    plot.draw()
    plot.save_datasets('test.csv')


