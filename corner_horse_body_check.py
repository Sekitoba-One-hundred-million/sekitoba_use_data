import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    check = {}
    corner_horce_body = dm.pickle_load( "corner_horce_body.pickle" )

    for k in corner_horce_body.keys():
        print( k )
        try:
            hb = corner_horce_body[k]["1"]
        except:
            hb = corner_horce_body[k]["3"]

        for kk in hb.keys():
            key = str( hb[kk] )
            lib.dic_append( check, key, 0 )
            check[key] += 1

main()
