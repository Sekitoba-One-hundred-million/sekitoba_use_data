import glob
import codecs
import pandas as pd

import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}

    for d in range( 1, 11 ):
        place_num = str( d )
        file_list = glob.glob( "/Users/kansei/Desktop/wind_data/" + place_num + "/*.csv" )

        for i in range( 0, len( file_list ) ):
            with codecs.open( file_list[i], "r", "Shift-JIS", "ignore") as file:
                str_data = file.readlines()

                for r in range( 6, len( str_data ) ):
                    data = str_data[r].replace( "\n", "" ).split( "," )
                    key = data[0].split( " " )[0] + ":" + data[0].split( " " )[1].split( ":" )[0]

                    lib.dic_append( result, place_num, {} )
                    lib.dic_append( result[place_num], key, { "wind": 0, "direction": "" } )
                    result[place_num][key]["direction"] = data[3]
                
                    try:
                        result[place_num][key]["wind"] = float( data[1] )
                    except:
                        result[place_num][key]["wind"] = 0
                    

    dm.pickle_upload( "wind_direction.pickle", result )

main()
        
    
