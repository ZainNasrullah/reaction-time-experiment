from reaction_time.reaction_time import ReactionTime
from reaction_time.reaction_time_gui import ReactionTimeGUI

if __name__ == '__main__':
    reaction = ReactionTimeGUI()

    if reaction.plot_mode == "True":
        reaction.print_results(f'logs/{reaction.log_name}.csv')
    else:
        reaction.run()
