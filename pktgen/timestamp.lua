--- This script can be used to measure timestamping precision and accuracy.
--  Connect cables of different length between two ports (or a fiber loopback cable on a single port) to use this.
local mg		= require "moongen"
local ts		= require "timestamping"
local device		= require "device"
local hist		= require "histogram"
local memory		= require "memory"
local stats		= require "stats"
local pcap		= require "pcap"

local PKT_SIZE = 128

local NUM_PKTS = 10^5

local ETH_SRC ="0C:C4:7A:A3:25:34"
local ETH_DST ="0C:C4:7A:A3:25:35"


function configure(parser)
	parser:argument("txPort", "Device use for tx."):args(1):convert(tonumber)
	parser:argument("rxPort", "Device use for rx."):args(1):convert(tonumber)
	-- parser:argument("file", "File to replay."):args(1)
	parser:option("-l --load", "replay as fast as possible"):default(0):convert(tonumber):target("load")
	parser:flag("-r --repeat", "Repeat pcap file.")
	local args = parser:parse()
	return args
end

function master(args)
	local txDev = device.config({port = args.txPort, rxQueues = 2, txQueues = 2})
	local rxDev = device.config({port = args.rxPort, rxQueues = 2, txQueues = 2})
	device.waitForLinks()
	if args.load then
		-- set the wire rate and not the payload rate
		load = args.load * PKT_SIZE / (PKT_SIZE + 24)
		txDev:getTxQueue(0):setRate(load)
		mg.startTask("loadSlave", txDev:getTxQueue(0), true)
		mg.sleepMillis(500)
	end
	runTest(txDev:getTxQueue(1), rxDev:getRxQueue(1))
end

function loadSlave(queue, showStats)
	local mem = memory.createMemPool(function(buf)
		buf:getEthPacket():fill{
			ethSrc = ETH_SRC,
			ethDst = ETH_DST
		}
	end)
	bufs = mem:bufArray()
	local ctr = stats:newDevTxCounter(queue.dev, "plain")
	local i = 0
	while i < NUM_PKTS and mg.running() do
		bufs:alloc(PKT_SIZE)
		queue:send(bufs)
		i = i + 1
		if showStats then ctr:update() end
	end
	if showStats then ctr:finalize() end
	mg.sleepMillis(1000)
	mg.stop()
end

function runTest(txQueue, rxQueue)
	local timestamper = ts:newTimestamper(txQueue, rxQueue)
	local hist = hist:new()
	while mg.running() do
		hist:update(timestamper:measureLatency())
	end
	hist:save("histogram.csv")
	hist:print()
end
