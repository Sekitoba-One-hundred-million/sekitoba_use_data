import math
from tqdm import tqdm

import SekitobaLibrary as lib
import SekitobaDataManage as dm

def main():
    result = {}
    corner_rank = dm.pickle_load( "corner_rank_data.pickle" )

    for race_id in tqdm( corner_rank.keys() ):
        if len( corner_rank[race_id] ) == 0:
            continue

        key_list = sorted( list( corner_rank[race_id].keys() ) )
        corner = ""#min( corner_rank[race_id].keys() )

        for k in key_list:
            if not len( corner_rank[race_id][k] ) == 0:
                corner = k
                break
        
        if len( corner ) == 0:
            continue

        lib.dic_append( result, race_id, {} )
        result[race_id] = {}
        rank = 1
        skip = False
        cr = corner_rank[race_id][corner]
        str_horce_num = ""
        
        for i in range( 0, len( cr ) ):
            word = cr[i]

            if str.isdigit( word ):
                str_horce_num += word
            elif not len( str_horce_num ) == 0:
                result[race_id][str_horce_num] = rank
                str_horce_num = ""
                rank += 1

        if not len( str_horce_num ) == 0:
            result[race_id][str_horce_num] = rank

    dm.pickle_upload( "first_corner_rank.pickle", result )
                    
main()        
            

