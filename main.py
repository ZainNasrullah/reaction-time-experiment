from reaction_time.reaction_time import ReactionTime

if __name__ == '__main__':
    reaction = ReactionTime()

    if reaction.plot_mode == "True":
        reaction.print_results(f'logs/{reaction.log_name}.csv')
    else:
        reaction.run()
