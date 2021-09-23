import math
from tqdm import tqdm
import matplotlib.pyplot as plt

import sekitoba_library as lib
import sekitoba_data_manage as dm

year = "2020"

def train_check( train_data ):
    analyze_data = {}
    
    for k in train_data.keys():
        for kk in train_data[k].keys():
            year = k[0:4]

            if year == "2020":
                continue

            t_time = 0
            tr_time = 0
            for i in range( 0, len( train_data[k][kk]["time"] ) - 1 ):
                if not train_data[k][kk]["time"][i] == 0:
                    t_time = float( train_data[k][kk]["time"][i] )
                    tr_time = float( train_data[k][kk]["time"][i+1] )
                    break

            if not t_time == 0 \
               and not tr_time == 0 \
               and  tr_time < t_time:
                cource = train_data[k][kk]["cource"]
                foot = train_data[k][kk]["foot"]
                baba = train_data[k][kk]["baba"]

                if cource not in analyze_data.keys():
                    analyze_data[cource] = { "time": 0, "wrap_time": 0, "count": 0, "time_all": [], "wrap_time_all": [], "foot": [], "baba": [] }

                if foot not in analyze_data[cource].keys():
                    analyze_data[cource][foot] = { "time": 0, "wrap_time": 0, "count": 0 }

                if baba not in analyze_data[cource].keys():
                    analyze_data[cource][baba] = { "time": 0, "wrap_time": 0, "count": 0 }

                analyze_data[cource]["time"] += t_time
                analyze_data[cource]["wrap_time"] += tr_time
                analyze_data[cource]["count"] += 1
                analyze_data[cource]["time_all"].append( t_time )
                analyze_data[cource]["wrap_time_all"].append( tr_time )
                analyze_data[cource]["foot"].append( foot )
                analyze_data[cource]["baba"].append( baba )

                analyze_data[cource][foot]["time"] += t_time
                analyze_data[cource][foot]["wrap_time"] += tr_time
                analyze_data[cource][foot]["count"] += 1

                analyze_data[cource][baba]["time"] += t_time
                analyze_data[cource][baba]["wrap_time"] += tr_time
                analyze_data[cource][baba]["count"] += 1

    for k in analyze_data.keys():
        analyze_data[k]["time"] /= analyze_data[k]["count"]
        analyze_data[k]["wrap_time"] /= analyze_data[k]["count"]
        for kk in analyze_data[k].keys():
            if not kk == "time" \
               and not kk == "count" \
               and not kk == "wrap_time" \
               and not kk == "time_all" \
               and not kk == "wrap_time_all" \
               and not kk == "foot" \
               and not kk == "baba":
                analyze_data[k][kk]["time"] /= analyze_data[k][kk]["count"]
                analyze_data[k][kk]["wrap_time"] /= analyze_data[k][kk]["count"]
                analyze_data[k][kk]["time"] = analyze_data[k]["time"] / analyze_data[k][kk]["time"]
                analyze_data[k][kk]["wrap_time"] = analyze_data[k]["wrap_time"] / analyze_data[k][kk]["wrap_time"]

    result = {}

    for k in analyze_data.keys():
        result[k] = {}
        result[k]["time_sd"] = 0
        result[k]["wrap_time_sd"] = 0
        result[k]["time"] = analyze_data[k]["time"]
        result[k]["wrap_time"] = analyze_data[k]["wrap_time"]
        
        for kk in analyze_data[k].keys():
            if not kk == "time" \
               and not kk == "count" \
               and not kk == "wrap_time" \
               and not kk == "time_all" \
               and not kk == "wrap_time_all" \
               and not kk == "foot" \
               and not kk == "baba":
                result[k][kk] = {}
                result[k][kk]["time"] = analyze_data[k][kk]["time"]
                result[k][kk]["wrap_time"] = analyze_data[k][kk]["wrap_time"]

        for i in range( 0, len( analyze_data[k]["time_all"] ) ):
            result[k]["time_sd"] += math.pow( result[k]["time"] - analyze_data[k]["time_all"][i], 2 )
            result[k]["wrap_time_sd"] += math.pow( result[k]["wrap_time"] - analyze_data[k]["wrap_time_all"][i], 2 )

            
        result[k]["time_sd"] /= len( analyze_data[k]["time_all"] )
        result[k]["wrap_time_sd"] /= len( analyze_data[k]["wrap_time_all"] )
        result[k]["time_sd"] = math.sqrt( result[k]["time_sd"] )
        result[k]["wrap_time_sd"] = math.sqrt( result[k]["wrap_time_sd"] )
        #print( k, result[k]["wrap_time_sd"] )

    dm.pickle_upload( "analyze_train_data.pickle", result)
    return result
                
def test( train_data, analyze_train_data ):
    time_x_data = []
    wrap_x_data = []
    y_data = []
    rank_check = {}

    for i in range( 1, 19 ):
        rank_check[str(i)] = { "t":0, "tr": 0, "count": 0 }
        
    race_data = dm.pickle_load( "race_data.pickle" )

    for k in tqdm( race_data.keys() ):
        race_id = lib.id_get( k )
        year = k.split( lib.split_key )[1][0:4]
        race_place_num = k.split( lib.split_key )[1][4:6]
        day = k.split( lib.split_key )[1][9]
        num = k.split( lib.split_key )[1][7]

        if year == "2020":
            continue

        for kk in race_data[k].keys():
            horce_name = kk.replace( " ", "" )
            file_name = "../database/" + horce_name + ".txt"
            current_data, _ = lib.race_check( file_name, year, day, num, race_place_num )#今回と過去のデータに分ける

            try:
                current_train = train_data[race_id][horce_name]                
            except:
                continue

            if len( current_data ) == 22:
                cd = lib.current_data( current_data )
                d = int( cd.dist() * 1000 )

                if d == 2000:
                    wrap_list = []
                    t_time = 0
                    tr_time = 0
                    t = 0

                    for i in range( 0, len( current_train["time"] ) ):
                        if not current_train["time"][i] == 0:
                            t_time = current_train["time"][i]
                            tr_time = current_train["time"][i+1]
                            t = ( i + 1 ) % 2
                            break
     
                    if not t_time == 0 \
                       and not tr_time == 0 \
                       and tr_time < t_time :
                    
                        for i in range( 0, len( current_train["time"] ) ):
                            if i % 2 == t:
                                wrap_list.append( current_train["time"][i] )
                    
                        cource = current_train["cource"]
                        foot = current_train["foot"]
                        baba = current_train["baba"]
                        t_time *= analyze_train_data[cource][foot]["time"]
                        t_time *= analyze_train_data[cource][baba]["time"]
                        #tr_time *= analyze_train_data[cource][foot]["wrap_time"]
                        #tr_time *= analyze_train_data[cource][baba]["wrap_time"]
    
                        t_time = ( analyze_train_data[cource]["time"] - t_time )
                        t_time /= analyze_train_data[cource]["time_sd"]
                        tr_time = regression_line( wrap_list )

                        #tr_time = ( analyze_train_data[cource]["wrap_time"] - tr_time )
                        #tr_time /= analyze_train_data[cource]["wrap_time_sd"]
                        rank_key = str( int( cd.rank() ) )
                        
                        if not cd.rank() == 0:
                            rank_check[rank_key]["count"] += 1
                            rank_check[rank_key]["t"] += t_time
                            rank_check[rank_key]["tr"] += tr_time

                        if not cd.race_time() == 0:
                            time_x_data.append( t_time )
                            wrap_x_data.append( tr_time )
                            y_data.append( cd.race_time() )                                                                                   
                            

    for i in range( 1, 19 ):
        rank_check[str(i)]["t"] /= rank_check[str(i)]["count"]
        rank_check[str(i)]["tr"] /= rank_check[str(i)]["count"]
        print( i, rank_check[str(i)]["t"], rank_check[str(i)]["tr"] )
        
    #plt.scatter( time_x_data, y_data )
    #plt.show()
    #plt.close()

    #plt.scatter( wrap_x_data, y_data )
    #plt.show()
    #plt.close()

def regression_line( data ):
    a = 0
    #b = 0
    y_ave = 0
    x_ave = 0

    for i in range( 0, len( data ) ):
        y_ave += data[i]
        x_ave += i + 1

    y_ave /= len( data )
    x_ave /= len( data )

    a1 = 0
    a2 = 0

    for i in range( 0, len( data ) ):
        a1 += ( i + 1 - x_ave ) * ( data[i] - y_ave )
        a2 += math.pow( i + 1 - x_ave, 2 )

    a = a1 / a2
    b = y_ave - a * x_ave

    return a, b
    
def main():
    train_data = dm.pickle_load( "train_time_data.pickle" )
    analyze_train_data = dm.pickle_load( "analyze_train_data.pickle" )
    #analyze_train_data = train_check( train_data )

    test( train_data, analyze_train_data )
    
main()
