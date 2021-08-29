#!/bin/bash
export base_pth=$1


check_file () {
  if [ -e $1 ]
  then
    return 0
  else
    return 1
fi
}

check_dir () {
  if [ -d $1 ]
  then
    return 0
  else
    return 1
fi
}

export md_file=$base_pth/lab0.rmd
export md_file_2=$base_pth/lab0.Rmd

if check_file $md_file || check_file $md_file_2
  then
    :
  else
    echo 'lab0 markdown file missing'
fi
export complie_file=$base_pth/rmd_compile.pdf
Rscript -e "rmarkdown::render('$md_file', output_file ='$complie_file')" --verbose False &> $base_pth/tmp.txt
if [ $? -eq 0 ]; then
    rm $base_pth/tmp.txt
    rm $complie_file
else
    echo "Markdown file $md_file does not compile, check $base_pth/md_log.txt"
fi


if check_file $base_pth/lab0.pdf
  then
    :
  else
    echo "lab 0 pdf file missing"

fi
