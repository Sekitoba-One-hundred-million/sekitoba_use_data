import sekitoba_library as lib
import sekitoba_data_manage as dm

def main():
    result = {}
    first_time_data = dm.pickle_load( "first_time.pickle" )

    for k in first_time_data.keys():
        race_id = lib.id_get( k )
        year = race_id[0:4]
        race_place_num = race_id[4:6]
        day = race_id[9]
        num = race_id[7]

        for i in range( 0, len( first_time_data[k] ) ):
            if not len( first_time_data[k][i]["time"] ) == 0:
                try:
                    file_name = "../database/" +  first_time_data[k][i]["name"] + ".txt"
                    current_data, _ = lib.race_check( file_name, year, day, num, race_place_num )#今回と過去のデータに分ける
                    cd = lib.current_data( current_data )
                    lib.dic_append( result, str( int( cd.rank() ) ), { "time": 0, "count": 0 } )
                    ave =  sum( first_time_data[k][i]["time"] ) / len( first_time_data[k][i]["time"] )
                    result[str( int( cd.rank() ) )]["count"] += 1
                    result[str( int( cd.rank() ) )]["time"] += ave
                except:
                    continue


    for i in range( 1, 18 ):
        result[str(i)]["time"] /= result[str(i)]["count"]
        print( i, result[str(i)]["time"] )
        
main()
