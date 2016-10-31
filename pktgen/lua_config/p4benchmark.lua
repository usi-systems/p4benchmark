--- Demonstrates and tests hardware timestamping capabilities

local mg     = require "moongen"
local device = require "device"
local memory = require "memory"
local ts     = require "timestamping"
local hist   = require "histogram"
local timer  = require "timer"
local log    = require "log"
local stats  = require "stats"
local pcap   = require "pcap"

local PKT_SIZE = 192

function configure(parser)
    parser:description("Demonstrate and test hardware timestamping capabilities.\n")
    parser:argument("dev", "Device use for tx and rx."):args(3):convert(tonumber)
    parser:argument("file", "Pcap file"):args(1):convert(tostring)
    parser:option("-r --rate", "Sending rate"):default(1000):convert(tonumber):target("rate")
    parser:option("-t --time", "Set running duration"):default(30):convert(tonumber):target("time")
    parser:option("-n --number", "Number of headers"):default(2):convert(tonumber):target("number")
    parser:option("-p --packet", "Number of packets"):default(nil):convert(tonumber):target("packet")
    parser:option("-s --size", "Header size"):default(8):convert(tonumber):target("size")
    local args = parser:parse()
    return args
end

function master(args)
    local dev1 = device.config{port = args.dev[1], txQueues = 1, rxQueues = 1}
    local dev2 = device.config{port = args.dev[2], txQueues = 1, rxQueues = 1}
    local dev3 = device.config{port = args.dev[3], txQueues = 1}
    device.waitForLinks()

    if args.packet then
        mg.startTask("loadSlave", dev1:getTxQueue(0), args.rate, args.file)
        mg.startTask("loadSlave", dev3:getTxQueue(0), args.rate, args.file)
        mg.startTask("counterSlave", dev2:getRxQueue(0))
        mg.startTask("timeStamper", dev2:getTxQueue(0), dev1:getRxQueue(0), args.packet, args.number, args.size)
    end
    mg.waitForTasks()
end

function loadSlave(queue, rate, file)
    queue:setRate(rate)
    local mempool = memory:createMemPool()
    local bufs = mempool:bufArray()
    local pcapFile = pcap:newReader(file)
    local txCtr = stats:newDevTxCounter(queue, "plain")
    while mg.running() do
        local n = pcapFile:read(bufs)
        if n == 0 then
            pcapFile:reset()
        end
        queue:sendN(bufs, n)
        txCtr:update()
    end
    txCtr:finalize()
end

function counterSlave(queue)
    local rxCtr = stats:newDevRxCounter(queue, "plain")
    local bufs = memory.bufArray()
    while mg.running() do
        local rx = queue:recv(bufs)
        rxCtr:update()
        bufs:freeAll()
    end
    rxCtr:finalize()
end


function timeStamper(txQueue, rxQueue, N, number, size)
    local hist = hist:new()
    mg.sleepMillis(1000) -- ensure that the load task is running
    local timestamper = ts:newTimestamper(txQueue, rxQueue)
    local rateLimit = timer:new(0.01)
    local counter = 0
    while counter < N and mg.running() do
        local lat = timestamper:measureLatency(PKT_SIZE, function(buf)
            local eth = buf:getEthPacket()
            -- mark reserved field for padding
            eth.payload.uint8[5] = 1
            local ptp = buf:getPtpPacket()
            for i = 0, 0 + number-1 do
                ptp.payload.uint8[i*size + 10] = i + 1
            end
        end, 100) -- Wait 100 ms if there isn't any returned packets
        hist:update(lat)
        counter = counter + 1
        rateLimit:wait()
        rateLimit:reset()
    end
    mg.stop()
    hist:print()
    if hist.numSamples == 0 then
        log:error("Received no packets.")
    end
    hist:save("histogram.csv")
    print()
end