#!/bin/bash
export base_pth=$1


check_file () {
  if [ -e $1 ]
then
    :
else
    echo "Error - $1 not found"
fi
}

check_dir () {
  if [ -d $1 ]
then
    :
else
    echo "Error - $1 not found"
fi
}

export md_file=$base_pth/lab0.rmd

check_file $md_file

Rscript -e "rmarkdown::render('$md_file')" --verbose False &> $base_pth/tmp.txt
if [ $? -eq 0 ]; then
    rm $base_pth/tmp.txt
else
    echo "Markdown file $md_file does not compile, check $base_pth/md_log.txt"
fi


check_file $base_pth/lab0.pdf
