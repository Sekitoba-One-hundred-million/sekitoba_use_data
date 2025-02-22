import numpy as np

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    wrap_data = dm.pickle_load( "wrap_data.pickle" )
    time200_data = dm.pickle_load( "time200_data.pickle" )

    if time200_data == None:
        time200_data = {}
        
        for k in wrap_data.keys():        
            time200 = 0

            try:
                time200 = wrap_data[k]["200"]
            except:
                try:
                    time200 = ( wrap_data[k]["100"] + wrap_data[k]["300"] ) / 3 * 2
                except:
                    continue

            time200_data[k] = time200

    dm.pickle_upload( "time200_data.pickle", time200_data )
    race_data = dm.pickle_load( "race_data.pickle" )
    race_info = dm.pickle_load( "race_info_data.pickle" )

    all_time = 0
    max_time = -1
    min_time = 1000
    all_count = 0
    first_analyze_data = {}
    
    for k in race_data.keys():
        race_id = lib.id_get( k )
        
        try:
            time200 = time200_data[race_id]
        except:
            continue

        key_kind = str( race_info[race_id]["kind"] )
        key_dist = str( race_info[race_id]["dist"] )
        key_baba = str( race_info[race_id]["baba"] )
        key_place = str( race_info[race_id]["place"] )

        all_time += time200
        all_count += 1
        max_time = max( max_time, time200 )
        min_time = min( min_time, time200 )
        lib.dic_append( first_analyze_data, key_place, {} )
        lib.dic_append( first_analyze_data[key_place], key_dist, {} )
        lib.dic_append( first_analyze_data[key_place], "list", [] )
        lib.dic_append( first_analyze_data[key_place][key_dist], key_kind, {} )
        lib.dic_append( first_analyze_data[key_place][key_dist], "list", [] )
        lib.dic_append( first_analyze_data[key_place][key_dist][key_kind], key_baba, {} )
        lib.dic_append( first_analyze_data[key_place][key_dist][key_kind], "list", [] )
        lib.dic_append( first_analyze_data[key_place][key_dist][key_kind][key_baba], "list", [] )

        first_analyze_data[key_place]["list"].append( time200 )
        first_analyze_data[key_place][key_dist]["list"].append( time200 )
        first_analyze_data[key_place][key_dist][key_kind]["list"].append( time200 )
        first_analyze_data[key_place][key_dist][key_kind][key_baba]["list"].append( time200 )

    result = {}

    print( all_time / all_count )
    print( max_time )
    print( min_time )
    
    for k in first_analyze_data.keys():#place        
        lib.dic_append( result, k, {} )
        result[k]["mean"] = np.mean( first_analyze_data[k]["list"] )
        result[k]["std"] = np.std( first_analyze_data[k]["list"] )

        for kk in first_analyze_data[k].keys():#dist
            if kk == "list":
                continue
            
            lib.dic_append( result[k], kk, {} )
            result[k][kk]["mean"] = np.mean( first_analyze_data[k][kk]["list"] )
            result[k][kk]["std"] = np.std( first_analyze_data[k][kk]["list"] )

            for kkk in first_analyze_data[k][kk].keys():#kind
                if kkk == "list":
                    continue
                
                lib.dic_append( result[k][kk], kkk, {} )
                result[k][kk][kkk]["mean"] = np.mean( first_analyze_data[k][kk][kkk]["list"] )
                result[k][kk][kkk]["std"] = np.std( first_analyze_data[k][kk][kkk]["list"] )

                for kkkk in first_analyze_data[k][kk][kkk].keys():#baba
                    if kkkk == "list":
                        continue
                    
                    lib.dic_append( result[k][kk][kkk], kkkk, {} )
                    result[k][kk][kkk][kkkk]["mean"] = np.mean( first_analyze_data[k][kk][kkk][kkkk]["list"] )
                    result[k][kk][kkk][kkkk]["std"] = np.std( first_analyze_data[k][kk][kkk][kkkk]["list"] )

    dm.pickle_upload( "first_pace_analyze_data.pickle", result )
    
    
    
main()

