from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    blood_closs_data = dm.pickle_load( "blood_closs_data.pickle" )
    horce_url = dm.pickle_load( "horce_url.pickle" )    
    horce_data = dm.pickle_load( "horce_data_storage.pickle" )

    for k in tqdm( horce_url.keys() ):
        horce_name = k.replace( " ", "" )
        
        try:
            all_data = horce_data[horce_name]
        except:
            continue

        for i in range( 0, len( all_data ) ):
            str_data = all_data[i]
            
            if len( str_data ) == 22:
                cd = lib.CurrentData( str_data )

                if cd.race_check():
                    race_time = cd.race_time()
                    key_dist = str( int( cd.dist() * 1000 ) )
                    key_race_kind = str( int( cd.race_kind() ) )

                    if not race_time == 0 \
                      and not key_dist == "0" \
                      and not key_race_kind == "0":
                        closs_data = blood_closs_data[k]

                        lib.dic_append( result, key_dist, {} )
                        lib.dic_append( result[key_dist], key_race_kind, {} )

                        for t in range( 0, len( closs_data ) ):
                            key_name = closs_data[t]["name"]
                            key_rate = str( int( closs_data[t]["rate"] * 100 ) )
                            lib.dic_append( result[key_dist][key_race_kind], key_name, {} )
                            lib.dic_append( result[key_dist][key_race_kind][key_name], key_rate, \
                                           { "rank": 0, "diff": 0, "time": 0, "up_time": 0, "count": 0 } )

                            result[key_dist][key_race_kind][key_name][key_rate]["count"] += 1
                            result[key_dist][key_race_kind][key_name][key_rate]["rank"] += cd.rank()
                            result[key_dist][key_race_kind][key_name][key_rate]["diff"] += cd.diff()
                            result[key_dist][key_race_kind][key_name][key_rate]["time"] += race_time
                            result[key_dist][key_race_kind][key_name][key_rate]["up_time"] += cd.up_time()
                            
                        
    for k in result.keys():
        for kk in result[k].keys():
            for kkk in result[k][kk].keys():
                for kkkk in result[k][kk][kkk].keys():
                    result[k][kk][kkk][kkkk]["rank"] /= result[k][kk][kkk][kkkk]["count"]
                    result[k][kk][kkk][kkkk]["diff"] /= result[k][kk][kkk][kkkk]["count"]
                    result[k][kk][kkk][kkkk]["time"] /= result[k][kk][kkk][kkkk]["count"]

                    if k == "2000" \
                      and kk == "1" \
                      and  result[k][kk][kkk][kkkk]["count"] > 30:
                        print( k, kk, kkk, kkkk, result[k][kk][kkk][kkkk]["diff"], result[k][kk][kkk][kkkk]["count"] )          


    dm.pickle_upload( "blood_closs_analyze_data.pickle", result )

main()
