import sekitoba_library as lib
import sekitoba_data_manage as dm

# 1:ミドル 一定型
# 2:ミドル 緩急型
# 3:ハイ 直線手前スロー型
# 4:ハイ 一本調子型
# 5:スロー 右肩上がり型
# 6:スロー ヨーイドン型

dm.dl.file_set( "race_data.pickle" )
dm.dl.file_set( "horce_data_storage.pickle" )
dm.dl.file_set( "wrap_data.pickle" )

def wrap_split( wrap_list, dist ):
    first_halon = int( len( wrap_list ) / 2 )
    before_last_halon = 4
    last_halon = 6

    if dist <= 1200:
        first_halon = 4
        last_halon = 4        
        before_last_halon = len( wrap_list ) - first_halon - last_halon

    if len( wrap_list ) < first_halon + before_last_halon + last_halon:
        first_halon = len( wrap_list ) - before_last_halon - last_halon

    count = 0
    first_wrap = round( ( sum( wrap_list[count:count+first_halon] ) / first_halon ) * 2, 2 )
    count += first_halon
    before_last_wrap = round( ( sum( wrap_list[count:count+before_last_halon] ) / before_last_halon ) * 2, 2 )
    count += before_last_halon
    last_wrap = round( ( sum( wrap_list[count:count+last_halon] ) / last_halon ) * 2, 2 )

    return first_wrap, before_last_wrap, last_wrap

# 1:右肩上がり型
# 2:ヨーイドン型
def slow_check( wrap_list, dist ):
    first_wrap, before_last_wrap, last_wrap = wrap_split( wrap_list, dist )
    
    if before_last_wrap < last_wrap:
        return 1

    if first_wrap < before_last_wrap:
        return 2

    diff_wrap_first = first_wrap - before_last_wrap
    diff_wrap_last = before_last_wrap - last_wrap

    if diff_wrap_first * 3 <= diff_wrap_last:
        return 2

    return 1

# 1:直線手前スロー型
# 2:一本調子型

def high_check( wrap_list, dist ):
    first_wrap, before_last_wrap, last_wrap = wrap_split( wrap_list, dist )

    if last_wrap - before_last_wrap < 0.2:
        return 1

    return 2

# 1:一定型
# 2:緩急型

def middle_check( wrap_list ):
    min_wrap = min( wrap_list )
    max_wrap = max( wrap_list )
    
    if abs( min_wrap - max_wrap ) < 0.8:
        return 1

    return 2

def pace_create( wrap_data ):
    wrap_list = []

    if len( wrap_data ) == 0:
        return -1

    for dk in wrap_data.keys():
        if dk == "100":
            wrap_list.append( wrap_data[dk] )
        else:
            wrap_list.append( wrap_data[dk] / 2 )
            wrap_list.append( wrap_data[dk] / 2 )
            
    n = len( wrap_list )
    p1 = int( n / 2 )
    p2 = p1 + ( n % 2 )
    pace = ( sum( wrap_list[0:p1] ) - sum( wrap_list[p2:n] ) )
    dist = int( list( wrap_data.keys() )[-1] )
    score = 0

    if pace < -1:
        score = 2
        high_score = high_check( wrap_list, dist )
        score += high_score
    elif 1 < pace:
        score = 4
        slow_score = slow_check( wrap_list, dist )
        score += slow_score
    else:
        score = 0
        middle_score = middle_check( wrap_list )
        score += middle_score
        
    return score

def main():
    race_data = dm.dl.data_get( "race_data.pickle" )
    wrap_data = dm.dl.data_get( "wrap_data.pickle" )
    horce_data = dm.dl.data_get( "horce_data_storage.pickle" )
    check = {}

    for k in race_data.keys():
        race_id = lib.id_get( k )

        try:
            current_wrap = wrap_data[race_id]
        except:
            continue

        pace = lib.pace_create( current_wrap )

        if pace == -1:
            continue

        key_pace = str( int( pace ) )
        lib.dic_append( check, key_pace, 0 )
        check[key_pace] += 1

    for k in check.keys():
        print( k, check[k] )

if __name__ == "__main__":
    main()
