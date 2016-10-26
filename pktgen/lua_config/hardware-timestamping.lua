--- Demonstrates and tests hardware timestamping capabilities

local lm     = require "libmoon"
local device = require "device"
local memory = require "memory"
local ts     = require "timestamping"
local hist   = require "histogram"
local timer  = require "timer"
local log    = require "log"

local RUN_TIME = 30

function configure(parser)
	parser:description("Demonstrate and test hardware timestamping capabilities.\n")
	parser:argument("txPort", "Device use for tx."):args(1):convert(tonumber)
	parser:argument("rxPort", "Device use for rx."):args(1):convert(tonumber)
	-- parser:argument("file", "File to replay."):args(1)
	parser:option("-l --load", "replay as fast as possible"):default(1000):convert(tonumber):target("load")
	local args = parser:parse()
	return args
end

function master(args)
	local txDev = device.config{port = args.txPort, txQueues = 2}
	local rxDev = device.config{port = args.rxPort, rxQueues = 2}
	device.waitForLinks()
	local txQueue0 = txDev:getTxQueue(0)
	local txQueue1 = txDev:getTxQueue(1)
	local rxQueue0 = rxDev:getRxQueue(0)
	local rxQueue1 = rxDev:getRxQueue(1)
	-- lm.startTask("timestamper", txQueue0, rxQueue0):wait()
	-- lm.startTask("timestamper", txQueue0, rxQueue1):wait()
	lm.startTask("timestamper", txQueue0, rxQueue0, 319):wait()
	-- lm.startTask("timestamper", txQueue0, rxQueue0, 1234):wait()
	-- lm.startTask("timestamper", txQueue0, rxQueue1, 319):wait()
	-- lm.startTask("timestamper", txQueue0, rxQueue1, 319)
	-- lm.startTask("flooder", txQueue1, 319)
	lm.waitForTasks()
end


function timestamper(txQueue, rxQueue, udp, randomSrc, vlan)
	local filter = rxQueue.qid ~= 0
	log:info("Testing timestamping %s %s rx filtering for %d seconds.",
		udp and "UDP packets to port " .. udp or "L2 PTP packets",
		filter and "with" or "without",
		RUN_TIME
	)
	if randomSrc then
		log:info("Using multiple flows, this can be slower on some NICs.")
	end
	if vlan then
		log:info("Adding VLAN tag, this is not supported on some NICs.")
	end
	local runtime = timer:new(RUN_TIME)
	local hist = hist:new()
	local timestamper
	if udp then
		timestamper = ts:newUdpTimestamper(txQueue, rxQueue)
	else
		timestamper = ts:newTimestamper(txQueue, rxQueue)
	end
	while lm.running() and runtime:running() do
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
end

function flooder(queue, port)
	log:info("Flooding link with UDP packets with the same flow 5-tuple.")
	log:info("This tests whether the filter matches on payload.")
	local mempool = memory.createMemPool(function(buf)
		local pkt = buf:getUdpPtpPacket()
		pkt:fill{
			ethSrc = queue,
		}
		-- the filter should not match this
		pkt.ptp:setVersion(0xFF)
		pkt.udp:setDstPort(port)
	end)
	local bufs = mempool:bufArray()
	local runtime = timer:new(RUN_TIME + 0.1)
	while lm.running() and runtime:running() do
		bufs:alloc(60)
		queue:send(bufs)
	end
end

