import SekitobaLibrary as lib
import SekitobaDataManage as dm
from SekitobaDataCreate.race_type import RaceType

import copy
import datetime
import trueskill
from tqdm import tqdm

def main():
    horce_rating_data = {}
    jockey_rating_data = {}
    trainer_rating_data = {}
    use_jockey_rateing = {}
    use_trainer_rateing = {}
    env = trueskill.TrueSkill( draw_probability = 0, beta = 12 )
    race_data = dm.pickle_load( "race_data.pickle" )
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )
    race_day = dm.pickle_load( "race_day.pickle" )
    race_jockey_id_data = dm.pickle_load( "race_jockey_id_data.pickle" )
    race_trainer_id_data = dm.pickle_load( "race_trainer_id_data.pickle" )
    foot_used_data = dm.pickle_load( "foot_used.pickle" )
    race_type = RaceType()    
    sort_time_data = []

    for k in race_data.keys():
        race_id = lib.idGet( k )
        day = race_day[race_id]
        check_day = datetime.datetime( day["year"], day["month"], day["day"] )
        race_num = int( race_id[-2:] )
        timestamp = int( datetime.datetime.timestamp( check_day ) + race_num )
        sort_time_data.append( { "k": k, "time": timestamp } )

    line_timestamp = 60 * 60 * 24 * 2 - 100 # 2day race_numがあるので -100
    sort_time_data = sorted( sort_time_data, key=lambda x: x["time"] )
    dev_result = { "horce": {}, "jockey": {}, "trainer": {} }
    
    for i, std in enumerate( sort_time_data ):
        k = std["k"]
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        dev_result["horce"][race_id] = {}
        dev_result["jockey"][race_id] = {}
        dev_result["trainer"][race_id] = {}
        jockey_id_list = race_jockey_id_data[race_id]
        trainer_id_list = race_trainer_id_data[race_id]
        rank_list = []
        rating_list = []
        use_jockey_id_list = []
        use_trainer_id_list = []
        use_horce_id_list = []

        if not i == 0:
            current_timestamp = std["time"]
            before_timestamp = sort_time_data[i-1]["time"]
            diff_timestamp = int( current_timestamp - before_timestamp )

            if line_timestamp < diff_timestamp:
                use_jockey_rateing = copy.deepcopy( jockey_rating_data )
                use_trainer_rateing = copy.deepcopy( trainer_rating_data )

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )

            if not cd.raceCheck():
                continue

            if not horce_id in jockey_id_list or not horce_id in trainer_id_list:
                continue

            jockey_id = jockey_id_list[horce_id]
            trainer_id = trainer_id_list[horce_id]
            my_foot_used = race_type.best_foot_used( cd, pd )
            currnt_foot_used = 0

            if race_id in foot_used_data:
                currnt_foot_used = foot_used_data[race_id]

            if not horce_id in horce_rating_data:
                horce_rating_data[horce_id] = env.create_rating()

            if not jockey_id in jockey_rating_data:
                jockey_rating_data[jockey_id] = env.create_rating()
                use_jockey_rateing[jockey_id] = env.create_rating()
                
            if not trainer_id in trainer_rating_data:
                trainer_rating_data[trainer_id] = env.create_rating()
                use_trainer_rateing[trainer_id] = env.create_rating()

            horce_current_rating = horce_rating_data[horce_id]
            jockey_current_rating = jockey_rating_data[jockey_id]
            trainer_current_rating = trainer_rating_data[trainer_id]
            
            use_jockey_current_rateing = use_jockey_rateing[jockey_id]
            use_trainer_current_rateing = use_trainer_rateing[trainer_id]
            rank = cd.rank()

            if rank == 0:
                continue

            diff = 3
            if my_foot_used == currnt_foot_used:
                rank += diff
            elif not my_foot_used == 0:
                rank -= diff

            rank_list.append( max( int( rank ), 0 ) )
            use_horce_id_list.append( horce_id )
            use_jockey_id_list.append( jockey_id )
            use_trainer_id_list.append( trainer_id )
            dev_result["horce"][race_id][horce_id] = horce_current_rating.mu
            dev_result["jockey"][race_id][jockey_id] = use_jockey_current_rateing.mu
            dev_result["trainer"][race_id][trainer_id] = use_trainer_current_rateing.mu
            rating_list.append( ( copy.deepcopy( horce_current_rating ), copy.deepcopy( jockey_current_rating ), copy.deepcopy( trainer_current_rating ) ) )

        if len( use_horce_id_list ) < 2:
            continue

        next_rating_list = env.rate( rating_list, ranks=rank_list )

        for i in range( 0, len( next_rating_list ) ):
            horce_rating_data[use_horce_id_list[i]] = copy.deepcopy( next_rating_list[i][0] )
            jockey_rating_data[use_jockey_id_list[i]] = copy.deepcopy( next_rating_list[i][1] )
            trainer_rating_data[use_trainer_id_list[i]] = copy.deepcopy( next_rating_list[i][2] )

    prod_result = { "horce": {}, "jockey": {}, "trainer": {} }

    for horce_id in horce_rating_data.keys():
        prod_result["horce"][horce_id] = horce_rating_data[horce_id].mu

    for jockey_id in jockey_rating_data.keys():
        prod_result["jockey"][jockey_id] = jockey_rating_data[jockey_id].mu

    for jockey_id in jockey_rating_data.keys():
        prod_result["trainer"][jockey_id] = jockey_rating_data[jockey_id].mu

    #dm.pickle_upload( "foot_used_true_skill_data.pickle", prod_result, prod = True )
    #dm.pickle_upload( "horce_jockey_true_skill_data.pickle", dev_result )
    dm.pickle_upload( "foot_used_true_skill_data.pickle", dev_result )

if __name__ == "__main__":
    main()
