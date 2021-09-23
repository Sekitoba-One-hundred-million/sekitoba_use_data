import glob
import codecs
import pandas as pd

import sekitoba_data_manage as dm

def file_analyze( file_name ):
    result = {}

    with codecs.open( file_name, "r", "Shift-JIS", "ignore") as file:
        str_data = file.readlines()

        for i in range( 5, len( str_data ) ):
            split_data = str_data[i].replace( "\n", "" ).split( "," )
            year = split_data[0]
            result[year] = {}
            result[year]["temperature"] = float( split_data[1] )
            result[year]["wind"] = float( split_data[4] )

    return result
    
def main():
    result = {}
    files = glob.glob( "../../weather_data/*")

    for file_name in files:        
        file_analyze( file_name )
        key = file_name.split( "/" )[3].split( "." )[0]
        print( key )
        result[key] = file_analyze( file_name )


    dm.pickle_upload( "weather_data.pickle", result )

main()
