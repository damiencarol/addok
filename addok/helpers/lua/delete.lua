-- Delete all keys matching pattern
-- args:
--    - pattern to match keys. Eg: d|*
local keys = redis.call('keys', ARGV[1])
if unpack(keys) ~= nil then
    return redis.call('del', unpack(keys))
else
    -- no keys to delete
    return 0
end
