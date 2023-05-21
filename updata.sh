
while read line
do
    data=($line)
    file_name=${data[${#data[@]}-1]}
    echo "finish ${file_name}"
    python $file_name
done < use_pickle.txt

exit 0
