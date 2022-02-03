--!/usr/local/bin/lua
function Pandoc(doc)
  local synopsis
  local date
  local category

  for k,v in pairs(doc.meta) do
    if k == 'synopsis' then
      synopsis = pandoc.utils.stringify(v)
    elseif k == 'date' then
      date = pandoc.utils.stringify(v)
    elseif k == 'category' then
      category = pandoc.utils.stringify(v)
    end
  end
  local new_blocks = {}
  if synopsis == nil then
    table.insert(new_blocks, doc.blocks[1])
  else
    table.insert(new_blocks, pandoc.Para(pandoc.Str(synopsis)))
  end
  local slugline = pandoc.Span('SLUGLINE', {date=date, category=category})
  table.insert(new_blocks[1].content, 1, slugline)
  return pandoc.Pandoc(new_blocks)
end
