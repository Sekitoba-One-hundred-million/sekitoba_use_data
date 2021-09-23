from tqdm import tqdm
import sys

sys.path.append( "../" )

import library as lib
import data_manage as dm

def race_id_create( year_day, place_data, race_num ):
    place_num = str( lib.place_num( place_data[1:3] ) )
    year = year_day.split( "/")[0]

    if int( year ) < 2009 \
       or int( year ) > 2020:
        return ""
    
    if place_num == "0":
        return ""

    first = True
    count = ""
    day = ""
    
    for i in range( 0, len( place_data ) ):
        if str.isdecimal( place_data[i] ):
            if first:
                count += place_data[i]
            else:
                day += place_data[i]
        else:
            first =  False

    if len( place_num ) == 1:
        place_num = "0" + place_num
        
    if len( count ) == 1:
        count = "0" + count

    if len( day ) == 1:
        day = "0" + day

    if len( race_num ) == 1:
        race_num = "0" + race_num
        
    race_id = year + place_num + count + day + race_num

    return race_id

def baba_index_check( baba_index_data ):
    result = {}

    for k in baba_index_data.keys():
        for kk in baba_index_data[k].keys():
            result[kk] = baba_index_data[k][kk]

    return result
    
def main():
    result = {}
    jockey_full_data = dm.pickle_load( "jockey_full_data.pickle" )
    money_data = dm.pickle_load( "race_money_data.pickle" )
    race_rank_data = dm.pickle_load( "race_rank_data_average.pickle" )
    baba_index_data = dm.pickle_load( "baba_index_data.pickle" )
    baba_index_data = baba_index_check( baba_index_data )
    standard_time_data = dm.pickle_load( "standard_time.pickle" )
    dist_index = dm.dist_index_get()
    base_loaf_weight = 55
    
    for k in tqdm( jockey_full_data.keys() ):
        result[k] = {}
        for kk in jockey_full_data[k].keys():
            year = kk.split( "/" )[0]
            race_id = race_id_create( kk, jockey_full_data[k][kk]["place"], jockey_full_data[k][kk]["race_num"] )

            if len( race_id ) == 0:
                continue

            key_popular = jockey_full_data[k][kk]["popular"]
            baba_index = baba_index_data[kk]
            burden_weight = float( jockey_full_data[k][kk]["weight"] )
            baba_index = baba_index_data[kk]
            burden_weight = float( jockey_full_data[k][kk]["weight"] )
            place = jockey_full_data[k][kk]["place"][1:3]
            kind_dist = jockey_full_data[k][kk]["dist"]

            if kind_dist[0] == "障":
                continue
            
            standard_time = standard_time_data[place][kind_dist]

            try:
                money_class = str( lib.money_class_get( money_data[race_id] ) )
            except:
                print( race_id, jockey_full_data[k][kk]["place"] )
            
            try:
                average_speed_index = race_rank_data["speed_index"][money_class][key_popular]["data"]
                average_diff = race_rank_data["diff"][money_class][key_popular]["data"]
                diff = float( jockey_full_data[k][kk]["diff"] )
                race_time = lib.race_time( jockey_full_data[k][kk]["time"] )
            except:
                continue

            key_dist = ""

            for i in range( 0, len( kind_dist ) ):
                if str.isdecimal( kind_dist[i] ):
                    key_dist += kind_dist[i]
            
            speed_index = ( standard_time - race_time ) * dist_index[key_dist] + \
                ( burden_weight - base_loaf_weight ) + baba_index + 80

            lib.dic_append( result[k], year, { "diff": 0, "speed_index": 0, "all": 0 } )
            result[k][year]["speed_index"] += ( speed_index - average_speed_index )
            result[k][year]["diff"] += ( diff - average_diff )
            result[k][year]["all"] += 1

    for k in result.keys():
        for kk in result[k].keys():
            result[k][kk]["speed_index"] /= result[k][kk]["all"]
            result[k][kk]["diff"] /= result[k][kk]["all"]
            #print( k, kk , result[k][kk] )
            
main()
