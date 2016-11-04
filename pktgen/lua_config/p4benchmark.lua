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
    parser:argument("file", "Pcap file"):args(1):convert(tostring)
    parser:option("-r --rate", "Sending rate"):default(1000):convert(tonumber):target("rate")
    parser:option("-t --timeout", "Read timeout"):default(15):convert(tonumber):target("timeout")
    parser:option("-n --number", "Number of headers"):default(2):convert(tonumber):target("number")
    parser:option("-p --packet", "Number of packets"):default(1000):convert(tonumber):target("packet")
    parser:option("-s --size", "Header size"):default(8):convert(tonumber):target("size")
    parser:option("-d --duration", "Maximum test duration"):default(600):convert(tonumber):target("duration")
    local args = parser:parse()
    return args
end

function master(args)
    local dev1 = device.config{port = 0, txQueues = 1, rxQueues = 1}
    local dev2 = device.config{port = 1, txQueues = 1, rxQueues = 1}
    local dev3 = device.config{port = 2, txQueues = 1, rxQueues = 1}
    local dev4 = device.config{port = 3, txQueues = 1, rxQueues = 1}
    device.waitForLinks()

    -- mg.startTask("loadSlave", dev2:getTxQueue(0), args.rate, args.file)
    -- mg.startTask("loadSlave", dev3:getTxQueue(0), args.rate, args.file)
    -- mg.startTask("loadSlave", dev4:getTxQueue(0), args.rate, args.file)
    mg.startTask("timeStamper", dev1:getTxQueue(0), dev2:getRxQueue(0), args.packet, args.number, args.size, args.timeout, args.duration)
    -- mg.startTask("counterSlave", dev1:getRxQueue(0))
    -- mg.startTask("counterSlave", dev3:getRxQueue(0))
    -- mg.startTask("counterSlave", dev4:getRxQueue(0))
    -- DEBUG
    -- mg.startTask("dumpSlave", dev2:getRxQueue(0))
    mg.waitForTasks()
end

function loadSlave(queue, rate, file)
    queue:setRate(rate)
    local mempool = memory:createMemPool()
    local bufs = mempool:bufArray()
    local pcapFile = pcap:newReader(file)
    local txCtr = stats:newDevTxCounter(queue, "csv")
    local file_name = table.concat({"txDev", queue.id, ".csv"})
    local file = io.open(file_name, "w+")
    io.output(file)
    while mg.running() do
        local n = pcapFile:read(bufs)
        if n == 0 then
            pcapFile:reset()
        end
        queue:sendN(bufs, n)
	mpps, mbit, wireMbit, total, totalBytes = txCtr:getStats()
        io.write(string.format("%f,%f,%f,%d,%d\n", mpps.avg, mbit.avg, wireMbit.avg, total, totalBytes))
    end
    mpps, mbit, wireMbit, total, totalBytes = txCtr:getStats()
    io.write(string.format("%f,%f,%f,%d,%d\n", mpps.avg, mbit.avg, wireMbit.avg, total, totalBytes))
    io.close(file)
end

function counterSlave(queue)
    local rxCtr = stats:newDevRxCounter(queue, "csv")
    local bufs = memory.bufArray()
    local file_name = table.concat({"rxDev", queue.id, ".csv"})
    local file = io.open(file_name, "w+")
    io.output(file)
    while mg.running() do
        local rx = queue:recv(bufs)
	mpps, mbit, wireMbit, total, totalBytes = rxCtr:getStats()
        io.write(string.format("%f,%f,%f,%d,%d\n", mpps.avg, mbit.avg, wireMbit.avg, total, totalBytes))
        bufs:freeAll()
    end
    mpps, mbit, wireMbit, total, totalBytes = rxCtr:getStats()
    io.write(string.format("%f,%f,%f,%d,%d\n", mpps.avg, mbit.avg, wireMbit.avg, total, totalBytes))
    io.close(file)
end


function timeStamper(txQueue, rxQueue, N, number, size, read_timeout, duration)
    local hist = hist:new()
    mg.sleepMillis(1000) -- ensure that the load task is running
    local timestamper = ts:newTimestamper(txQueue, rxQueue)
    -- local rateLimit = timer:new(read_timeout)
    local runtime = timer:new(duration)
    local counter = 0
    while counter < N and runtime:running() and mg.running() do
        local lat, numPkts = timestamper:measureLatency(PKT_SIZE, function(buf)
            local eth = buf:getEthPacket()
            -- mark reserved field for padding
            eth.payload.uint8[5] = 1
            local ptp = buf:getPtpPacket()
            for i = 0, 0 + number-1 do
                ptp.payload.uint8[i*size + 11] = 1
            end
        end, read_timeout) -- Wait x ms if there isn't any returned packets
        hist:update(lat)
        counter = counter + numPkts
        -- rateLimit:wait()
        -- rateLimit:reset()
    end
    mg.stop()
    hist:print()
    if hist.numSamples == 0 then
        log:error("Received no packets.")
    end
    hist:save("histogram.csv")
    print()
end

function dumpSlave(queue)
    local bufs = memory.bufArray()
    local pktCtr = stats:newPktRxCounter("Packets counted", "plain")
    while mg.running() do
        local rx = queue:tryRecv(bufs, 100)
        for i = 1, rx do
            local buf = bufs[i]
            buf:dump()
            pktCtr:countPacket(buf)
        end
        bufs:free(rx)
        pktCtr:update()
    end
    pktCtr:finalize()
end