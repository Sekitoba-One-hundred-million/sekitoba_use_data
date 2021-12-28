from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )

def main():
    result = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.race_check( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.current_data( current_data )
            pd = lib.past_data( past_data, current_data )
            
            if not cd.race_check():
                continue

            limb_math = lib.limb_search( pd )

            if limb_math == 0:
                continue

            try:
                first_horce_body = float( cd.passing_rank().split( "-" )[0] )
            except:
                continue

            key_limb = str( int( limb_math ) )
            lib.dic_append( result, key_limb, { "data": 0, "count": 0 } )
            result[key_limb]["data"] += first_horce_body / cd.all_horce_num()
            result[key_limb]["count"] += 1

    for i in range( 1, 9 ):
        k = str( i )
        result[k]["data"] /= result[k]["count"]
        print( "limb:{} horce_body:{}".format( k, str( result[k]["data"] ) ) )

    #dm.pickle_upload( "limb_passing_rank.pickle", result )

if __name__ == "__main__":
    main()

