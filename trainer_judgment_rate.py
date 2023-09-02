import sekitoba_library as lib
import sekitoba_data_manage as dm

import copy
import datetime
import trueskill
from tqdm import tqdm

def main():
    trainer_judgment = {}
    use_trainer_judgment = {}
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    race_day = dm.pickle_load( "race_day.pickle" )
    race_trainer_id_data = dm.pickle_load( "race_trainer_id_data.pickle" )
    sort_time_data = []
    param_list = [ "limb", "popular", "flame_num", "dist", "kind", "baba", "place" ]

    for k in race_data.keys():
        race_id = lib.id_get( k )
        day = race_day[race_id]
        check_day = datetime.datetime( day["year"], day["month"], day["day"] )
        race_num = int( race_id[-2:] )
        timestamp = int( datetime.datetime.timestamp( check_day ) + race_num )
        sort_time_data.append( { "k": k, "time": timestamp } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( sort_time_data, key=lambda x: x["time"] )
    dev_result = {}
    
    for i, std in enumerate( sort_time_data ):
        k = std["k"]
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        dev_result[race_id] = {}
        trainer_id_list = race_trainer_id_data[race_id]
        rank_list = []
        rating_list = []
        use_trainer_id_list = []
        use_horce_id_list = []

        if not i == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[i-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                use_trainer_judgment = copy.deepcopy( trainer_judgment )

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )

            if not cd.race_check():
                continue

            if not horce_id in trainer_id_list:
                continue

            first_passing_rank = -1

            try:
                first_passing_rank = int( cd.passing_rank().split( "-" )[0] )
            except:
                continue

            before_rank = -1
            before_cd = pd.before_cd()

            if not before_cd == None:
                before_rank = before_cd.rank()

            first_passing_class = min( int( first_passing_rank / int( cd.all_horce_num() / 3 ) ), 2 )
            key_first_passing_class = str( first_passing_class )
            trainer_id = trainer_id_list[horce_id]
            limb_math = lib.limb_search( pd )

            key_data = {}
            key_data["limb"] = str( int( limb_math ) )
            key_data["popular"] = str( int( cd.popular() ) )
            key_data["flame_num"] = str( int( cd.flame_number() ) )
            key_data["dist"] = str( int( cd.dist_kind() ) )
            key_data["kind"] = str( int( cd.race_kind() ) )
            key_data["baba"] = str( int( cd.baba_status() ) )
            key_data["place"] = str( int( cd.place()) )

            if not trainer_id in trainer_judgment:
                trainer_judgment[trainer_id] = {}

            dev_result[race_id][horce_id] = {}
            
            for param in param_list:
                lib.dic_append( trainer_judgment[trainer_id], param, {} )                
                lib.dic_append( trainer_judgment[trainer_id][param], key_data[param], { "0": 0, "1": 0, "2": 0, "count": 0 } )
                trainer_judgment[trainer_id][param][key_data[param]][key_first_passing_class] += 1
                trainer_judgment[trainer_id][param][key_data[param]]["count"] += 1
                
                score_data = {}

                if trainer_id in use_trainer_judgment and \
                param in use_trainer_judgment[trainer_id] and \
                key_data[param] in use_trainer_judgment[trainer_id][param] and \
                not use_trainer_judgment[trainer_id][param][key_data[param]]["count"] == 0:
                    for r in [ "0", "1", "2" ]:
                        score_data[r] = use_trainer_judgment[trainer_id][param][key_data[param]][r] / use_trainer_judgment[trainer_id][param][key_data[param]]["count"]
                    
                dev_result[race_id][horce_id][param] = score_data

                trainer_judgment[trainer_id][param][key_data[param]]["count"] += 1
                trainer_judgment[trainer_id][param][key_data[param]][key_first_passing_class] += 1

    for trainer_id in trainer_judgment.keys():
        for param in trainer_judgment[trainer_id].keys():
            for data in trainer_judgment[trainer_id][param].keys():
                count = trainer_judgment[trainer_id][param][data]["count"]
                for key in trainer_judgment[trainer_id][param][data].keys():
                    trainer_judgment[trainer_id][param][data][key] = trainer_judgment[trainer_id][param][data][key] / count

    dm.pickle_upload( "trainer_judgment_rate_data.pickle", dev_result )
    dm.pickle_upload( "trainer_judgment_rate_prod_data.pickle", trainer_judgment )

if __name__ == "__main__":
    main()
