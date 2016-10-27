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


function configure(parser)
	parser:description("Demonstrate and test hardware timestamping capabilities.\n")
	parser:argument("txPort", "Device use for tx."):args(1):convert(tonumber)
	parser:argument("rxPort", "Device use for rx."):args(1):convert(tonumber)
	parser:option("-f --file", "File to replay."):default(nil):convert(tostring):target('file')
	parser:option("-r --rate", "Sending rate"):default(1000):convert(tonumber):target("rate")
	parser:option("-t --time", "Set running duration"):default(30):convert(tonumber):target("time")
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
		mg.startTask("timestamper", txQueue1, rxQueue1, 319, args.time)
	end

	mg.waitForTasks()
end


function timestamper(txQueue, rxQueue, udp, run_time, randomSrc, vlan)
	local filter = rxQueue.qid ~= 0
	log:info("Testing timestamping %s %s rx filtering for %d seconds.",
		udp and "UDP packets to port " .. udp or "L2 PTP packets",
		filter and "with" or "without",
		run_time
	)
	if randomSrc then
		log:info("Using multiple flows, this can be slower on some NICs.")
	end
	if vlan then
		log:info("Adding VLAN tag, this is not supported on some NICs.")
	end
	local runtime = timer:new(run_time)
	local timestamper
	if udp then
		timestamper = ts:newUdpTimestamper(txQueue, rxQueue)
	else
		timestamper = ts:newTimestamper(txQueue, rxQueue)
	end
	local hist = hist:new()
	mg.sleepMillis(1000) -- ensure that the load task is running
	while mg.running() and runtime:running() do
		local lat = timestamper:measureLatency(function(buf)
			if udp then
				if randomSrc then
					buf:getUdpPacket().udp:setSrcPort(math.random(1, 1000))
				end
                local pkt = buf:getUdpPacket()
                pkt:fill {
                        DstPort = udp,
                        ethSrc = txQueue,
                        ethDst = rxQueue
                }
            end
			if vlan then
				buf:setVlan(1234)
			end
		end)
		hist:update(lat)
	end
	hist:print()
	if hist.numSamples == 0 then
		log:error("Received no packets.")
	end
	print()
	hist:save("histogram.csv")
end

function loadSlave(queue, rxDev, file, run_time)
	local mempool = memory:createMemPool()
	local bufs = mempool:bufArray()
	local pcapFile = pcap:newReader(file)
	local txCtr = stats:newDevTxCounter(queue, "plain")
	local rxCtr = stats:newDevRxCounter(rxDev, "plain")
	local runtime = timer:new(run_time)
	while runtime:running() and mg.running() do
		local n = pcapFile:read(bufs)
		if n == 0 then
			pcapFile:reset()
		end
		queue:sendN(bufs, n)
		txCtr:update()
		rxCtr:update()
	end
	mg.sleepMillis(1000)
	txCtr:finalize()
	rxCtr:finalize()
	mg.stop()
end

