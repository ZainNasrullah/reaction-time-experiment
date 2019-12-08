# built-in
import os
import platform
import datetime
import time
import configparser
from collections import Counter

# analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# non-standard library
import readchar
import pygame
import pygame.gfxdraw

# local imports
from reaction_time.utils import calculate_time_delta_ms, avg_time_scores_by
from reaction_time.gui_classes import GameConfig, Circle


class ReactionTimeGUI:
    def __init__(self, config_path="config.cfg"):
        """ Initialize the ReactionTimeGUI Object

        Parameters
        ----------
        config_path : str
            Path to the configuration file

        """

        # read the config file
        print(
            "Please provide the file path to your configuration file"
            " (blank for default: ./config.cfg):\n"
        )
        user_config_path = input()
        if user_config_path != "":
            config_path = user_config_path

        config = configparser.ConfigParser()
        assert os.path.isfile(config_path), f"Config file not found at {config_path}"
        print("Loading configuration.")
        config.read(config_path)

        print("Initializing ReactionTime.")
        KEY_MAPPING = config.items("KEY_MAPPING")
        KEY_SCORES = config.items("KEY_SCORES")

        key_mapping_list, mapped_keys = zip(*KEY_MAPPING)
        self.key_list, key_scores = zip(*KEY_SCORES)

        self.plot_mode = config["MODE"]["PLOT_MODE"]
        self.log_name = config["MODE"]["LOG_NAME"]

        assert (
            key_mapping_list == self.key_list
        ), "KEY_MAPPING and KEY_SCORES don't have the same keys"

        key_scores = np.array([int(score) for score in key_scores])
        self.key_probabilities = key_scores / key_scores.sum()

        low_speed = float(config["GENERAL"]["LOW_SPEED"])
        high_speed = float(config["GENERAL"]["HIGH_SPEED"])
        self.speed = lambda: np.random.uniform(low_speed, high_speed)

        self.sequence_length = int(config["GENERAL"]["SEQUENCE_LENGTH"])
        self.key_dict = {key: button for key, button in KEY_MAPPING}

        self.platform = platform.system()

    def run(self):
        """ Run the main reaction time loop

        Algorithm
        -----
        - Randomly selects a key
        - Prints it to the screen and waits for user input
        - Reads the user input, measures time taken and checks correctness
        - Waits until next iteration

        Returns
        -------
        None

        """

        print("Running Reaction Time.\n\n")
        history = list()
        count_history = Counter()
        previous_key = None

        print(f"Click one of the following: {self.key_dict.keys()}\n")
        print(
            "Note: The first and last iterations are not tracked. "
            "Exit by typing 'x' at any prompt."
        )

        game = GameConfig()
        selected_key = np.random.choice(self.key_list, p=self.key_probabilities)
        circles = [Circle(game, radius=20, key=self.key_dict[selected_key])]

        while game.run:

            time_taken, user_key, correct_flag = game.event_handler(
                circles[-1], selected_key=self.key_dict[selected_key]
            )

            if correct_flag == -1:
                break

            if correct_flag is not None:
                selected_key = np.random.choice(self.key_list, p=self.key_probabilities)
                new_circle = Circle(game, radius=20, key=self.key_dict[selected_key])
                circles.append(new_circle)

                # track number of iterations since last selected
                iters_last_selected = self._update_count_history(
                    count_history, selected_key
                )

            # exclude first iteration (prevents skewing distribution)
            # previous key ~ prior iteration random key
            if game.n_iter != 0:
                result = (
                    previous_key,
                    selected_key,
                    user_key,
                    time_taken,
                    correct_flag,
                    iters_last_selected,
                )
                history.append(result)

            # update values for subsequent iterations
            if time_taken is not None:
                previous_key = selected_key
                game.n_iter += 1

            game.fill_background()

            i = 0
            while i < len(circles):
                circles[i].render_self_with_text(self.key_dict[selected_key])
                if circles[i].alpha == 0:
                    circles.pop(i)
                else:
                    i += 1

            game.print_score()
            pygame.display.update()
            game.clock.tick(60)

        game.quit()
        metrics_df = self._create_save_metrics_df(history)
        self.print_results(metrics_df)

    @staticmethod
    def print_results(metrics_df):
        """ Print average statistics and create plots to summarize the run

        Parameters
        ----------
        metrics_df: pd.DataFrame or str
            Output metrics from ReactionTime.run()

        Returns
        -------
        None

        """

        # if string passed, read in dataframe
        if isinstance(metrics_df, str):
            metrics_df = pd.read_csv(metrics_df)

        # print out some summary statistics
        try:
            key_performance = avg_time_scores_by(metrics_df, "key")
            previous_key_performance = avg_time_scores_by(metrics_df, "previous_key")
            transition_performance = avg_time_scores_by(
                metrics_df, ["previous_key", "key"]
            )
        except pd.core.base.DataError:
            raise ValueError("Not enough sample data to generate metrics.")

        print(f"Average time for key\n: {key_performance}")
        print(f"Average time given previous key\n: {previous_key_performance}")
        print(f"Average time given transition\n: {transition_performance}")

        fig, ax = plt.subplots(2, 1, sharex=True)
        palette = {0: "#ff4500", 1: "#00ff00"}
        sns.boxplot(data=metrics_df, x="key", y="time_ms", ax=ax[0])
        sns.swarmplot(
            data=metrics_df,
            x="key",
            y="time_ms",
            hue="correct",
            palette=palette,
            alpha=0.5,
            ax=ax[0],
        )
        ax[0].title.set_text("Time (ms) Distribution for Key")
        ax[0].set_xlabel("")

        sns.boxplot(data=metrics_df, x="previous_key", y="time_ms", ax=ax[1])
        sns.swarmplot(
            data=metrics_df,
            x="previous_key",
            y="time_ms",
            hue="correct",
            palette=palette,
            alpha=0.5,
            ax=ax[1],
        )
        ax[1].title.set_text("Time (ms) Distribution Given Previous Key")
        ax[1].set_xlabel("")

        # Set the formatting the same for both subplots
        ax[0].tick_params(axis="both", which="both", labelsize=7, labelbottom=True)
        ax[1].tick_params(axis="both", which="both", labelsize=7, labelbottom=True)

        plt.tight_layout()
        plt.show()

        sns.scatterplot(
            data=metrics_df,
            x="time_ms",
            y="iters_last_selected",
            hue="correct",
            palette=palette,
            alpha=0.5,
        )
        plt.title("Time Taken vs Iterations Since Last Selected")
        plt.show()

        transition_matrix = pd.pivot_table(
            data=metrics_df,
            index="previous_key",
            columns="key",
            values="time_ms",
            aggfunc="mean"
        )
        transition_count = pd.pivot_table(
            data=metrics_df,
            index="previous_key",
            columns="key",
            values="time_ms",
            aggfunc="count",
        )
        sns.heatmap(data=transition_matrix, annot=transition_count, cmap="coolwarm")
        plt.title("Transition Matrix (Color - Avg Time Taken (ms), Annotation - Count)")
        plt.show()

    def _update_count_history(self, count_history, selected_key):

        iters_last_selected = None
        for key in self.key_list:
            if key != selected_key:
                # only increment keys that have been seen
                if key in count_history:
                    count_history[key] += 1
            else:
                # if not defined, count_history[key] returns 0
                iters_last_selected = count_history[key]
                count_history[key] = 0

        return iters_last_selected

    def _create_save_metrics_df(self, history):
        data_columns = [
            "previous_key",
            "key",
            "user_key",
            "time_ms",
            "correct",
            "iters_last_selected",
        ]

        metrics_df = pd.DataFrame(history, columns=data_columns)
        os.makedirs("logs", exist_ok=True)
        metrics_df.to_csv(f"logs/{self.log_name}.csv", index=False)
        return metrics_df
