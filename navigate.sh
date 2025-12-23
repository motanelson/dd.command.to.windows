printf "\033c\033[40;37m\ngive me the file image to open "
read i
mdir -i $i ::
while true;
do
    printf "\033[40;37m\ngive me the path  "
    read ii
    mdir -i $i ::/$ii
done