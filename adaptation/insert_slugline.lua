--!/usr/local/bin/lua

function Pandoc(doc)
  local date = 'None'
  local category = 'None'
  for k,v in pairs(doc.meta) do
    if k == "date" then
      date =  pandoc.utils.stringify(v)
    elseif k == 'category' then
      category = pandoc.utils.stringify(v) 
    elseif k == 'sequence_start' then 
      sequence_start = pandoc.utils.stringify(v) 
    end
  end
  local content = pandoc.Str('SLUGLINE')
  local attrs = pandoc.Attr("", {}, {{"date", date}, {"category", category}, {"sequence_start", sequence_start }})
  table.insert (doc.blocks[1].content, 1, pandoc.Span(content, attrs))
  return pandoc.Pandoc(doc.blocks)
end
