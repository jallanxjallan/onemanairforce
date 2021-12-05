--!/usr/local/bin/lua

local sredis = require 'sredis'

function Pandoc(doc)
  local rkey = doc.meta['slugline_data_key']

  for k,v in pairs(doc.meta) do
    sredis.query({'hset', rkey, k, pandoc.utils.stringify(v)})
  end
  local slugline = pandoc.Span('SLUGLINE', {slugline_data_key=rkey})
  table.insert (doc.blocks[1].content, 1, slugline)
  return pandoc.Pandoc(doc.blocks)
end
