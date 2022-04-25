#!/usr/bin/env bash

filename=$(echo $1 | sed 's/ /_/g' | sed -e 's/\(.*\)/\L\1/')
filepath=sequences/$filename".md"

if test -f $filepath; then
  echo "$filepath already exists"
else
    /home/jeremy/Library/scripts/output_document_filepaths.py \
    screenplay.ctd \
    --base_node="$1" \
    --label=Treatment \
    | /home/jeremy/Library/scripts/output_pandoc_args.py \
    | xargs -l1 pandoc -d synopsis  \
    | xargs pandoc -M name="$1" -d sequence -o $filepath 
    echo file://$(pwd)/$filepath
fi
