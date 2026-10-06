import random
from collections import defaultdict

ideal_response = {'R': 'P', 'P': 'S', 'S': 'R'}


def player(prev_play, opponent_history=[], my_history=[], memory={}):

    if prev_play == "":
        opponent_history.clear()
        my_history.clear()
        memory.clear()
        memory['freq1'] = defaultdict(lambda: defaultdict(int))
        memory['freq2'] = defaultdict(lambda: defaultdict(int))
        memory['freq3'] = defaultdict(lambda: defaultdict(int))
        memory['combo'] = defaultdict(lambda: defaultdict(int))
        memory['scores'] = defaultdict(int)
        memory['last_predictions'] = {}
        memory['opp_counts'] = defaultdict(int)

    if prev_play != "":
        opponent_history.append(prev_play)
        memory['opp_counts'][prev_play] += 1

        for strat, pred in memory['last_predictions'].items():
            if pred == prev_play:
                memory['scores'][strat] += 1
            else:
                memory['scores'][strat] -= 1

        if len(opponent_history) >= 2:
            key1 = opponent_history[-2]
            memory['freq1'][key1][prev_play] += 1
        if len(opponent_history) >= 3:
            key2 = "".join(opponent_history[-3:-1])
            memory['freq2'][key2][prev_play] += 1
        if len(opponent_history) >= 4:
            key3 = "".join(opponent_history[-4:-1])
            memory['freq3'][key3][prev_play] += 1
        if len(my_history) >= 1 and len(opponent_history) >= 2:
            combo_key = my_history[-1] + opponent_history[-2]
            memory['combo'][combo_key][prev_play] += 1

    predictions = {}

    # Detector de ciclo fijo (para bots tipo Quincy, que repiten una secuencia exacta)
    cycle_prediction = None
    for cycle_len in range(1, 11):
        needed = cycle_len * 3
        if len(opponent_history) >= needed:
            recent = opponent_history[-needed:]
            is_cycle = all(
                recent[i] == recent[i % cycle_len] for i in range(needed)
            )
            if is_cycle:
                cycle_prediction = opponent_history[-cycle_len]
                break
    if cycle_prediction:
        predictions['cycle'] = cycle_prediction
        memory['scores']['cycle'] = 9999  # máxima prioridad, es un patrón determinista

    if len(opponent_history) >= 1:
        key1 = opponent_history[-1]
        if memory['freq1'][key1]:
            predictions['freq1'] = max(memory['freq1'][key1], key=memory['freq1'][key1].get)

    if len(opponent_history) >= 2:
        key2 = "".join(opponent_history[-2:])
        if memory['freq2'][key2]:
            predictions['freq2'] = max(memory['freq2'][key2], key=memory['freq2'][key2].get)

    if len(opponent_history) >= 3:
        key3 = "".join(opponent_history[-3:])
        if memory['freq3'][key3]:
            predictions['freq3'] = max(memory['freq3'][key3], key=memory['freq3'][key3].get)

    if len(my_history) >= 1 and len(opponent_history) >= 1:
        combo_key = my_history[-1] + opponent_history[-1]
        if memory['combo'][combo_key]:
            predictions['combo'] = max(memory['combo'][combo_key], key=memory['combo'][combo_key].get)

    if memory['opp_counts']:
        predictions['most_common'] = max(memory['opp_counts'], key=memory['opp_counts'].get)

    memory['last_predictions'] = predictions

    if predictions:
        best_strategy = max(predictions.keys(), key=lambda s: memory['scores'][s])
        prediction = predictions[best_strategy]
    else:
        prediction = random.choice(["R", "P", "S"])

    guess = ideal_response[prediction]
    my_history.append(guess)
    return guess