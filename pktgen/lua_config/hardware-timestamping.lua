--- Demonstrates and tests hardware timestamping capabilities

local mg     = require "moongen"
local device = require "device"
local memory = require "memory"
local ts     = require "timestamping"
local hist   = require "histogram"
local timer  = require "timer"
local log    = require "log"
local stats	 = require "stats"
local pcap	 = require "pcap"

local PKT_SIZE = 192

function configure(parser)
	parser:description("Demonstrate and test hardware timestamping capabilities.\n")
	parser:argument("txPort", "Device use for tx."):args(1):convert(tonumber)
	parser:argument("rxPort", "Device use for rx."):args(1):convert(tonumber)
	parser:option("-f --file", "File to replay."):default(nil):convert(tostring):target('file')
	parser:option("-r --rate", "Sending rate"):default(1000):convert(tonumber):target("rate")
	parser:option("-t --time", "Set running duration"):default(30):convert(tonumber):target("time")
	parser:option("-n --number", "Number of headers"):default(2):convert(tonumber):target("number")
	parser:option("-s --size", "Header size"):default(8):convert(tonumber):target("size")
	local args = parser:parse()
	return args
end

function master(args)
	local txDev = device.config{port = args.txPort, txQueues = 2}
	local rxDev = device.config{port = args.rxPort, rxQueues = 2}
	device.waitForLinks()
	local txQueue0 = txDev:getTxQueue(0)
	local txQueue1 = txDev:getTxQueue(0)
	local rxQueue0 = rxDev:getRxQueue(1)
	local rxQueue1 = rxDev:getRxQueue(1)

	txQueue0:setRate(args.rate)

	if args.file then
		mg.startTask("loadSlave", txQueue0, rxDev, args.file, args.time)
	else
		mg.startTask("timestamper", txQueue1, rxQueue1, args.time, args.number, args.size)
	end

	mg.waitForTasks()
end

function timestamper(txQueue, rxQueue, test_time, number, size)
    local filter = rxQueue.qid ~= 0
    log:info("Testing timestamping %s %s rx filtering for %d seconds.",
        "L2 PTP packets",
        filter and "with" or "without",
        test_time
    )
    local runtime = timer:new(test_time)
    local hist = hist:new()
    local timestamper = ts:newTimestamper(txQueue, rxQueue)
    while mg.running() and runtime:running() do
        local lat = timestamper:measureLatency(PKT_SIZE, function(buf)
            local eth = buf:getEthPacket()
            local ptp = buf:getPtpPacket()
            -- mark reserved field for padding
            eth.payload.uint8[5] = 1
            for i = 0, 0 + number-1 do
                ptp.payload.uint8[i*size + 10] = i + 1
            end
        end)
        hist:update(lat)
    end
    hist:print()
    if hist.numSamples == 0 then
        log:error("Received no packets.")
    end
    print()
end
