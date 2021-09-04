local slugline = {}

function get_slugline_data (meta)
  local date
  local location
  local sequence_start
  for k,v in pairs(meta) do
    if k == "date" then
      date = pandoc.utils.stringify(v)
    end
    if k == "location" then
      location = pandoc.utils.stringify(v)
    end
    if k == 'sequence_start' then
      sequence_start = pandoc.utils.stringify(v)
    end
  end
  slugline = pandoc.Span('Slugline', {date=date, location=location, sequence_start=sequence_start})
end

function insert_slugline (el)
  if slugline ~= nil then
    table.insert(el.content, 1, slugline)
  end
  return el
end

return {{Meta = get_slugline_data}, {Para = insert_slugline}}
