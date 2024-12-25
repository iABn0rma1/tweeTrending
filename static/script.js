function runScript() {
    // Hide the "Run Script" button
    document.getElementById("run-script-btn").style.display = "none";

    const runAgainButton = document.getElementById("run-again-btn");
    if (runAgainButton) {
        // Disable the "Run Again" button
        runAgainButton.disabled = true;
    }

    fetch("/run-script") // Fetch the data from the scraper script
        .then((response) => response.json())
        .then((data) => {
            let html = `
                    <p>These are the most happening topics as on ${data.timestamp
                }:</p>
                    <ul>
                        <li>${data.trend1}</li>
                        <li>${data.trend2}</li>
                        <li>${data.trend3}</li>
                        <li>${data.trend4}</li>
                        <li>${data.trend5}</li>
                    </ul>
                    <p>The IP address used for this query was ${data.ip_address
                }.</p>
                    <div class="pre-wrapper"> <!-- Wrapper for the "Copy" button -->
                        <pre id="data-pre">${JSON.stringify(
                    data,
                    null,
                    4
                )}</pre>
                        <button class="copy-btn" onclick="copyToClipboard()">Copy</button>
                    </div>
                `;
            document.getElementById("results").innerHTML = html;

            if (!runAgainButton) {
                // Create and append the "Run Again" button, if not already present
                const newRunAgainButton = document.createElement("button");
                newRunAgainButton.id = "run-again-btn";
                newRunAgainButton.textContent =
                    "Click here to run the query again";
                newRunAgainButton.onclick = runScript;
                document
                    .querySelector(".container")
                    .appendChild(newRunAgainButton);
            } else {
                // Enable the "Run Again" button after completion
                runAgainButton.disabled = false;
            }
        })
        .catch((error) => {
            console.error("Error fetching data:", error);
            if (runAgainButton) {
                // Re-enable the "Run Again" button on error
                runAgainButton.disabled = false;
            }
        });
}

function copyToClipboard() {
    const preContent = document.getElementById("data-pre").textContent;
    navigator.clipboard
        .writeText(preContent) // Write the content of <pre> to clipboard
        .catch((err) => console.error("Error copying to clipboard: ", err));
}