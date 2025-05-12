const fs = require('fs');
const readline = require('readline');

// Function to parse IPs and Ports from a chunk of lines and return the parsed lines
function parseIpsAndPortsFromLines(lines) {
    const pattern = /Discovered open port (\d+)\/tcp on (\d+\.\d+\.\d+\.\d+)/;
    const results = [];
    for (const line of lines) {
        const match = line.match(pattern);
        if (match) {
            const port = match[1];
            const ip = match[2];
            results.push(`${ip}:${port}\n`);
        }
    }
    return results;
}

// Async function to process a chunk of lines, write results, and update progress
async function processChunk(chunk, writer, progress) {
    const parsedLines = parseIpsAndPortsFromLines(chunk);
    for (const line of parsedLines) {
        await writer.write(line);
    }
    progress.processed += chunk.length;
    console.log(`${progress.processed}/${progress.total} lines processed.`);
}

// Main async function to read the input file, process it, and write to output file with maximum resource utilization
async function parseIpsConcurrently(inputFile, outputFile) {
    const progress = { total: 0, processed: 0 };

    const reader = readline.createInterface({
        input: fs.createReadStream(inputFile),
        crlfDelay: Infinity
    });

    const writer = fs.createWriteStream(outputFile);

    reader.on('line', async (line) => {
        const chunk = [line];
        // Process the current line
        await processChunk(chunk, writer, progress);
        progress.total++;
    });

    reader.on('close', () => {
        console.log(`All ${progress.processed} lines processed.`);
        writer.close();
    });
}

// Example usage
const readlineSync = require('readline-sync');
const input_file = readlineSync.question('Enter the input file path: ');
const output_file = 'iplist-' + input_file;
parseIpsConcurrently(input_file, output_file);
