from tqdm import tqdm
import matplotlib.pyplot as plt

import sekitoba_library as lib
import sekitoba_data_manage as dm

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "corner_horce_body.pickle" )
dm.dl.data_get( "first_up3_halon.pickle" )
dm.dl.file_set( "race_cource_info.pickle" )
dm.dl.file_set( "race_info_data.pickle" )

def main():
    result = {}
    x_data = []
    y_data = []
    race_data = dm.dl.data_get( "race_data.pickle" )
    race_info = dm.dl.data_get( "race_info_data.pickle" )    
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    corner_horce_body = dm.dl.data_get( "corner_horce_body.pickle" )    
    first_up3_halon = dm.dl.data_get( "first_up3_halon.pickle" )
    race_cource_info = dm.dl.data_get( "race_cource_info.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]
        up3_instance = []
        fhb_instance = []        

        key_place = str( race_info[race_id]["place"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_kind = str( race_info[race_id]["kind"] )        
        key_baba = str( race_info[race_id]["baba"] )
        info_key_dist = key_dist
        
        if race_info[race_id]["out_side"]:
            info_key_dist += "外"

        try:
            rci_dist = race_cource_info[key_place][key_kind][info_key_dist]["dist"]
            rci_info = race_cource_info[key_place][key_kind][info_key_dist]["info"]
        except:
            continue

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
            
            key_horce_num = str( int( cd.horce_number() ) )

            try:
                key = min( corner_horce_body[race_id] )
                first_horce_body = corner_horce_body[race_id][key][key_horce_num]
            except:
                continue

            key_limb = str( int( limb_math ) )

            try:
                up3 = sum( first_up3_halon[race_id][key_horce_num] ) / len( first_up3_halon[race_id][key_horce_num] )
            except:
                up3 = 0

            up3_instance.append( up3 )
            fhb_instance.append( first_horce_body )                

        if len( up3_instance ) == 0:
            continue
        
        up3 = sum( up3_instance ) / len( up3_instance )

        for i in range( 0, len( up3_instance ) ):
            score = ( up3_instance[i] - up3 ) * rci_dist[0]
            x_data.append( score )
            y_data.append( fhb_instance[i] )

    plt.scatter( x_data, y_data )
    plt.show()

if __name__ == "__main__":
    main()

