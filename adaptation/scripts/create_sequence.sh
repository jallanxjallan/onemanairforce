#!/usr/bin/env bash

sequence=$1 
output_filename=$(echo $sequence | sed 's/ /_/g' | sed -e 's/\(.*\)/\L\1/')
output_filepath=sequences/$output_filename".md"

if test -f $output_filepath; then
  echo "$filepath already exists"
else
  
  output_indexed_documents.py screenplay.ctd --base_node "$sequence" --label "Document" \
  | xargs pandoc --template=sequence -M title="$sequence" -o $output_filepath 
  echo $output_filepath | tr -d '\n' | xclip -sel clip

fi
