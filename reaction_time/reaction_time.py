# built-in
import os
import datetime
import time
import configparser

# analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# non-standard library
import readchar

# local imports
from reaction_time.utils import calculate_time_delta_ms, avg_time_scores_by


class ReactionTime:
    def __init__(self, config_path="config.cfg"):
        """ Initialize the ReactionTime Object

        Parameters
        ----------
        config_path : str
            Path to the configuration file

        """

        # read the config file
        config = configparser.ConfigParser()
        assert os.path.isfile(config_path), "No configuration file found."
        config.read(config_path)

        KEY_MAPPING = config.items("KEY_MAPPING")
        KEY_SCORES = config.items("KEY_SCORES")

        self.key_list, key_scores = zip(*KEY_SCORES)
        key_scores = np.array([int(score) for score in key_scores])
        self.key_probabilities = key_scores / key_scores.sum()
        self.min_speed = float(config["GENERAL"]["MIN_SPEED"])

        low_speed = float(config["GENERAL"]["LOW_SPEED"])
        high_speed = float(config["GENERAL"]["HIGH_SPEED"])
        self.speed = lambda: np.random.uniform(low_speed, high_speed)

        self.sequence_length = int(config["GENERAL"]["SEQUENCE_LENGTH"])
        self.key_dict = {key: button for key, button in KEY_MAPPING}

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

        history = list()
        previous_key = None
        n_iter = 0

        print(f"Click one of the following: {self.key_dict.keys()}\n")
        print(
            "Note: The first and last iterations are not tracked. "
            "Exit by typing 'x' at any prompt."
        )

        while True:

            selected_key = np.random.choice(self.key_list, p=self.key_probabilities)
            print(selected_key)

            time_taken, user_key = self._read_user_input()
            correct_flag = self._validate_user_key(selected_key, time_taken, user_key)

            if correct_flag == -1:
                break

            # exclude first iteration (prevents skewing distribution)
            # previous key ~ prior iteration random key
            if n_iter != 0:
                result = (
                    previous_key,
                    selected_key,
                    user_key,
                    time_taken,
                    correct_flag,
                )
                history.append(result)

            # update values for subsequent iterations
            previous_key = selected_key
            n_iter += 1
            speed = self.speed()

            speed = max(self.min_speed, speed)
            time.sleep(speed)

        self._print_results(history)

    def _validate_user_key(self, random_key, time_taken, user_key):

        # user pressed the right key
        if user_key == self.key_dict[random_key]:
            print(f"Correct ({time_taken:0.2f}ms)\n")
            correct_flag = 1

        # user breaks the execution
        elif user_key == "x":
            correct_flag = -1

        # user pressed the wrong key
        else:
            print(f"Wrong ({time_taken:0.2f}ms)\n")
            correct_flag = 0

        return correct_flag

    def _read_user_input(self):

        # input mechanism via readchar
        user_press = b""
        start_dt = datetime.datetime.now()
        for _ in range(self.sequence_length):
            user_press += readchar.readchar()
        stop_dt = datetime.datetime.now()

        # convert byte string to utf-8 encoded string
        user_press = str(user_press, encoding="utf-8")
        time_taken = calculate_time_delta_ms(start_dt, stop_dt)

        return time_taken, user_press

    @staticmethod
    def _print_results(history):

        metrics_df = pd.DataFrame(
            history, columns=["previous_key", "key", "user_key", "time_ms", "correct"]
        )

        # print out some summary statistics
        key_performance = avg_time_scores_by(metrics_df, "key")
        previous_key_performance = avg_time_scores_by(metrics_df, "previous_key")
        transition_performance = avg_time_scores_by(metrics_df, ["previous_key", "key"])

        print(f"Average time for key\n: {key_performance}")
        print(f"Average time given previous key\n: {previous_key_performance}")
        print(f"Average time given transition\n: {transition_performance}")

        fig, ax = plt.subplots(2, 1, sharex=True)

        sns.boxplot(data=metrics_df, x="key", y="time_ms", ax=ax[0])
        ax[0].title.set_text("Time (ms) Distribution for Ability")
        ax[0].set_xlabel("")

        sns.boxplot(data=metrics_df, x="previous_key", y="time_ms", ax=ax[1])
        ax[1].title.set_text("Time (ms) Distribution for Previous Ability")
        ax[1].set_xlabel("")

        # Set the formatting the same for both subplots
        ax[0].tick_params(axis="both", which="both", labelsize=7, labelbottom=True)
        ax[1].tick_params(axis="both", which="both", labelsize=7)

        plt.tight_layout()
        plt.show()

        transition_matrix = pd.pivot_table(
            data=transition_performance,
            index="previous_key",
            columns="key",
            values="time_ms",
        )
        transition_count = pd.pivot_table(
            data=metrics_df,
            index="previous_key",
            columns="key",
            values="time_ms",
            aggfunc="count",
        )

        sns.heatmap(data=transition_matrix, annot=transition_count, cmap="coolwarm")
        plt.title("Transition Matrix (Color - Mean Time Taken (ms), Annotation - Count")
        plt.show()
