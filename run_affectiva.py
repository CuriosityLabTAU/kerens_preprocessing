from path_names import *
from load_files import *
from datetime import datetime
import numpy as np

def get_time(t_str):
    try:
        return datetime.strptime(t_str, '%Y_%m_%d_%H_%M_%S')
    except:
        return datetime.strptime(t_str, '%Y_%m_%d_%H_%M_%S_%f')

def get_stats(aff_list):
    stats = {}
    for f in aff_list[0].keys():
        stats[f] = {'n':0, 'mean': 0.0, 'std': 0.0, 'max': 0.0, 'data': []}
    for l in aff_list:
        for k, v in l.items():
            if k != 'time':
                stats[k]['data'].append(float(v))
    for k, v in stats.items():
        try:
            v['n'] = len(v['data'])
            v['mean'] = np.mean(np.array(v['data']))
            v['std'] = np.std(np.array(v['data']))
            v['max'] = np.max(np.array(v['data']))
            stats[k].pop('data')
        except:
            print(v['data'])
    return stats

def game_stats(aff_list, stat_type):
    result = {}
    for k, v in aff_list[0].items():
        if k != 'time':
            aff_temp = []
            for a in aff_list:
                aff_temp.append(float(a[k]))
            if stat_type == 'max':
                result[k] = np.max(np.array(aff_temp))
        else:
            result[k] = v
    print(result)
    return result


the_dates = [['2016', '05', '25'], ['2016', '02', '05'], ['2017', '02', '03'],['2017','05','24']]

# print('--- Affectiva ---')
aff_data = load_affectiva(the_path, the_dates)

print('Tablet, number of data points')
for t, data in aff_data.items():
    print(t, len(data))
    # for d in data:
    #     print(t, d['time'], d['smile'])

print('--- game ---')
game_data = load_game(the_path, the_dates)
print('Tablet, number of data points')
for t, data in game_data.items():
    print(t, len(data))


print('--- sync ---')
aff_results = {}
sub_results = {}
sub_stats = {}
for tab, data in game_data.items():
    aff_results[tab] = {}
    sub_results[tab] = {}
    sub_stats[tab] = {}
    print(tab)
    # try:
    i_game = 0
    i_aff = 0
    if len(aff_data[tab]) == 0:
        print('done')
    else:
        # find first match
        t_aff = get_time(aff_data[tab][i_aff]['time'])
        t_game = get_time(game_data[tab][i_game]['time'])
        while t_game < t_aff:
            i_game += 1
            t_game = get_time(game_data[tab][i_game]['time'])

        for j_game in range(0,len(game_data[tab])-1):
            # get all the data between this game and the next
            t_game = get_time(game_data[tab][j_game]['time'])
            t_game_next = get_time(game_data[tab][j_game + 1]['time'])
            game_data[tab][j_game]['aff'] = []
            while t_game_next > t_aff and i_aff < len(aff_data[tab])-1:
                i_aff += 1
                t_aff = get_time(aff_data[tab][i_aff]['time'])
                game_data[tab][j_game]['aff'].append(aff_data[tab][i_aff])

            if len(game_data[tab][j_game]['aff']) > 0 and game_data[tab][j_game]['action'] == 'play':
                # print(len(game_data[tab][i_game]['aff']), t_aff, t_game, t_game_next)
                # print(game_data[tab][i_game]['action'], game_data[tab][i_game]['comment'], game_data[tab][i_game]['subject'])
                local_results = get_stats(game_data[tab][j_game]['aff'])
                game_results= game_stats(game_data[tab][j_game]['aff'], 'max')
                try:
                    sub_results[tab][game_data[tab][j_game]['subject']].append(game_results)
                except:
                    sub_results[tab][game_data[tab][j_game]['subject']] = [game_results]
                if local_results is not None:
                    local_results['play'] = game_data[tab][j_game]['comment']
                    try:
                        aff_results[tab][game_data[tab][j_game]['subject']].append(local_results)
                    except:
                        aff_results[tab][game_data[tab][j_game]['subject']] = [local_results]
        # except:
        #     print(tab, 'end of data')

        # for kr, vr in aff_results[tab].items():
        #     print(kr, len(vr))
        for kr, vr in sub_results[tab].items():
            stats = get_stats(vr)
            print(kr, len(vr), stats)
            sub_stats[tab][kr] = stats

results_file = open(analysis_path + 'affectiva_results.json', 'w+')
json.dump(aff_results, results_file)
results_file = open(analysis_path + 'affectiva_subject_stats.json', 'w+')
json.dump(sub_stats, results_file)