const express = require("express");
const { spawn } = require("child_process");
const PYTHON_PATH = process.env.PYTHON_PATH || "python";
const app = express();
const PORT = 3000;

app.use(express.json());


// Home page
app.get("/", (req, res) => {
    res.send("Routing Simulation Server is running!");
});


// Find best route
app.get("/route", (req, res) => {

    const { start, destination } = req.query;

    if (!start || !destination) {
        return res.status(400).json({
            error: "Please provide start and destination"
        });
    }

    const python = spawn(PYTHON_PATH, ["main.py", start, destination]);

    let output = "";
    let error = "";

    python.stdout.on("data", (data) => {
        output += data.toString();
    });

    python.stderr.on("data", (data) => {
        error += data.toString();
    });

    python.on("close", (code) => {

        if (code !== 0) {
            return res.status(500).json({
                error: error
            });
        }

        try {
            const result = JSON.parse(output);
            res.json(result);

        } catch (err) {
            res.status(500).json({
                error: "Invalid response from Python",
                details: output
            });
        }
    });
});


// Reroute after road blockage
app.get("/reroute", (req, res) => {

    const { start, destination, blockedRoad } = req.query;

    if (!start || !destination || !blockedRoad) {
        return res.status(400).json({
            error: "Please provide start, destination and blockedRoad"
        });
    }

    const [blockedStart, blockedEnd] = blockedRoad.split(",");

    if (!blockedStart || !blockedEnd) {
        return res.status(400).json({
            error: "blockedRoad format should be: Location1,Location2"
        });
    }
        const python = spawn(PYTHON_PATH, [
        "main.py",
        start,
        destination,
        blockedStart,
        blockedEnd
    ]);

    let output = "";
    let error = "";

    python.stdout.on("data", (data) => {
        output += data.toString();
    });

    python.stderr.on("data", (data) => {
        error += data.toString();
    });

    python.on("close", (code) => {

        if (code !== 0) {
            return res.status(500).json({
                error: error
            });
        }

        try {
            const result = JSON.parse(output);

            res.json(result);

        } catch (err) {
            res.status(500).json({
                error: "Invalid response from Python",
                details: output
            });
        }
    });
});


// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
