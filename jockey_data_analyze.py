import copy
from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm

def time_create( time_data ):
    result = 0
    time_data = time_data.split( ":" )
    result += float( time_data[0] ) * 60
    result += float( time_data[1] )

    return result

def rank_add( data, rank, a ):
    if rank == 1:
        data["one"] += a
        data["two"] += a
        data["three"] += a
    elif rank == 2:
        data["two"] += a
        data["three"] += a
    elif rank == 3:
        data["three"] += a    

def main():
    result = {}
    jockey_full_data = dm.pickle_load( "jockey_full_data.pickle" )
    
    c = 0
    for jockey_id in tqdm( jockey_full_data.keys() ):
        c += 1
        past_data = []
        result[jockey_id] = {}
        key_list = jockey_full_data[jockey_id]["key_list"]
        day_num = jockey_full_data[jockey_id]["key_num"]
        instance = { "count": 0, "rank": 0, "one": 0, "two": 0, "three": 0, "time": 0, "up": 0, "fhb": 0 }
        instance100 = { "count": 0, "rank": 0, "one": 0, "two": 0, "three": 0, "time": 0, "up": 0, "fhb": 0 }

        for i in range( len( key_list ) - 1, -1, -1 ):
            key = key_list[i]
            result[jockey_id][key] = {}            
            result[jockey_id][key]["all"] = copy.copy( instance )
            result[jockey_id][key]["100"] = copy.copy( instance100 )

            if not result[jockey_id][key]["all"]["count"] == 0:
                count = result[jockey_id][key]["all"]["count"]                
                result[jockey_id][key]["all"]["rank"] /= count
                result[jockey_id][key]["all"]["one"] /= count
                result[jockey_id][key]["all"]["two"] /= count
                result[jockey_id][key]["all"]["three"] /= count
                result[jockey_id][key]["all"]["time"] /= count
                result[jockey_id][key]["all"]["fhb"] /= count

                count100 = min( result[jockey_id][key]["100"]["count"], 100 )
                result[jockey_id][key]["100"]["rank"] /= count100
                result[jockey_id][key]["100"]["one"] /= count100
                result[jockey_id][key]["100"]["two"] /= count100
                result[jockey_id][key]["100"]["three"] /= count100
                result[jockey_id][key]["100"]["time"] /= count100
                result[jockey_id][key]["100"]["up"] /= count100
                result[jockey_id][key]["100"]["fhb"] /= count100

            try:
                rank = float( jockey_full_data[jockey_id][key]["rank"] )
                time = time_create( jockey_full_data[jockey_id][key]["time"] )
                up = float( jockey_full_data[jockey_id][key]["up"] )
                dist = float( jockey_full_data[jockey_id][key]["dist"][1:5] ) /1000
                first_horce_body = float( jockey_full_data[jockey_id][key]["passing"].split( "-" )[0] )
                past_data.append( { "time": time / dist, "rank": rank, "up": up, "fhb": first_horce_body } )   
            except:
                continue                

            instance["count"] += 1
            instance["rank"] += rank
            instance["time"] += time / dist
            instance["up"] += up
            rank_add( instance, rank, 1 )
        
            if instance100["count"] >= 100:
                p = instance100["count"] - 100
                instance100["time"] -= past_data[p]["time"]
                instance100["up"] -= past_data[p]["up"]
                instance100["rank"] -= past_data[p]["rank"]
                rank_add( instance100, past_data[p]["rank"], -1 )

            instance100["count"] += 1
            instance100["rank"] += rank
            instance100["time"] += time / dist
            instance100["up"] += up
            rank_add( instance100, rank, 1 )                

    dm.pickle_upload( "jockey_anlyze_data.pickle", result )           

if __name__ == "__main__":
    main()
