from tqdm import tqdm
from sklearn.cluster import KMeans

import SekitobaLibrary as lib
import SekitobaDataManage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "corner_horce_body.pickle" )

def main():
    result = {}
    race_data = dm.dl.data_get( "race_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    corner_horce_body = dm.dl.data_get( "corner_horce_body.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.idGet( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        instance = []
        key_horce_num_list = []

        for kk in race_data[k].keys():
            horce_id = kk
            current_data, past_data = lib.raceCheck( horce_data[horce_id],
                                                     year, day, num, race_place_num )#今回と過去のデータに分ける
            cd = lib.CurrentData( current_data )
            pd = lib.PastData( past_data, current_data )
            
            if not cd.raceCheck():
                continue

            limb_math = lib.limbSearch( pd )

            if limb_math == 0:
                continue
            
            key_horce_num = str( int( cd.horceNumber() ) )

            try:
                key = min( corner_horce_body[race_id] )
                first_horce_body = corner_horce_body[race_id][key][key_horce_num]
            except:
                continue

            instance.append( [ first_horce_body ] )
            key_horce_num_list.append( key_horce_num )

        if len( instance ) < 4:
            continue
        
        instance = KMeans( n_clusters = 3 ).fit_predict( instance )
        lib.dicAppend( result, race_id, {} )

        for i in range( 0, len( instance ) ):
            result[race_id][key_horce_num] = instance[i]

    dm.pickle_upload( "first_horce_body_split_class.pickle", result )

if __name__ == "__main__":
    main()

