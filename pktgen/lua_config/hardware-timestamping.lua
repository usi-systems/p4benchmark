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
    parser:option("-r --rate", "Sending rate"):default(1000):convert(tonumber):target("rate")
    parser:option("-t --time", "Set running duration"):default(30):convert(tonumber):target("time")
    parser:option("-n --number", "Number of headers"):default(2):convert(tonumber):target("number")
    parser:option("-p --packet", "Number of packets"):default(nil):convert(tonumber):target("packet")
    parser:option("-s --size", "Header size"):default(8):convert(tonumber):target("size")
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

    if args.packet then
        mg.startTask("send_N_packets", txQueue0, rxQueue0, args.rate, args.packet, args.number, args.size)
    else
        mg.startTask("send_N_seconds", txQueue0, rxQueue0, args.rate, args.time, args.number, args.size)
    end

    mg.waitForTasks()
end

function send_N_seconds(txQueue, rxQueue, rate, n_seconds, number, size)
    local filter = rxQueue.qid ~= 0
    log:info("Sending Rate %d Mbps, %s %s rx filtering for %d seconds.",
        rate,
        "L2 PTP packets",
        filter and "with" or "without",
        n_seconds
    )
    txQueue:setRate(rate)
    local runtime = timer:new(n_seconds)
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
    hist:save("histogram.csv")
    print()
end

function send_N_packets(txQueue, rxQueue, rate, N, number, size)
    local filter = rxQueue.qid ~= 0
    log:info("Sending Rate %d Mbps, %s %s rx filtering for %d packets.",
        rate,
        "L2 PTP packets",
        filter and "with" or "without",
        N
    )
    txQueue:setRate(rate)
    local hist = hist:new()
    local timestamper = ts:newTimestamper(txQueue, rxQueue)
    local i = 0
    while i < N and mg.running() do
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
        i = i + 1
    end
    hist:print()
    if hist.numSamples == 0 then
        log:error("Received no packets.")
    end
    hist:save("histogram.csv")
    print()
end