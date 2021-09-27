from tqdm import tqdm

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}
    corner_rank = dm.pickle_load( "corner_rank_data.pickle" )

    for k in tqdm( corner_rank.keys() ):
        race_id = k
        
        for corner in corner_rank[race_id].keys():
            if len( corner_rank[race_id][corner] ) == 0:
                continue

            lib.dic_append( result, race_id, {} )
            result[race_id][corner] = {}
            hb = 0
            box = False
            skip = False
            cr = corner_rank[race_id][corner]

            for i in range( 0, len( cr ) ):
                if skip:
                    skip = False
                    continue
                
                if cr[i] == "(":
                    box = True
                    
                    if not i == 0:
                        hb += 1
                    
                elif cr[i] == ")":
                    box = False
                    hb += 1
                elif not box and cr[i] == ",":
                    hb += 1.5
                elif cr[i] == "-":
                    hb += 3.5
                elif cr[i] == "=":
                    hb += 6

                if str.isdecimal( cr[i] ):
                    c = cr[i]

                    if not i == len( cr ) - 1 and str.isdecimal( cr[i+1] ):
                        c += cr[i+1]
                        skip = True
                        
                    result[race_id][corner][c] = hb

    dm.pickle_upload( "corner_horce_body.pickle", result )
                    
main()        
            

