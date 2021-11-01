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

perform_check_file() {
  if check_file $1
  then
    :
  else
    echo "$1 file missing"
    exit 1

fi

}

perform_check_dir() {
  if check_dir $1
  then
    :
  else
    echo "$1 folder missing"
    exit 1

fi

}

perform_rmd_checks() {
  export md_file=$1
  export md_file_2=$2
  if check_file $md_file
  then
    :
  else
    if check_file $md_file_2
    then
      export md_file=$md_file_2
    else
        echo $md_file 'file missing'
        exit 1
    fi
fi

}

perform_rmd_checks $base_pth/lab4.rmd $base_pth/lab4.Rmd

#export md_file=$base_pth/lab1.rmd
#export md_file_2=$base_pth/lab1.Rmd
#
#if check_file $md_file
#  then
#    :
#  else
#    if check_file $md_file_2
#    then
#      export md_file=$md_file_2
#    else
#        echo $md_file 'file missing'
#        exit 1
#    fi
#fi

perform_check_file $base_pth/lab4.pdf


export complie_file=$base_pth/rmd_compile.pdf
Rscript -e "rmarkdown::render('$md_file', output_file ='$complie_file')" --verbose False &> $base_pth/md_log.txt
if [ $? -eq 0 ]; then
    rm $base_pth/md_log.txt
    rm $complie_file
else
    echo "Markdown file" $md_file "does not compile, check $base_pth/md_log.txt"
    exit 1
fi

echo "You passed the test - great work!"
