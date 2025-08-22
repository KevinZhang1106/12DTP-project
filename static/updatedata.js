// Get the search input, champion links, and "no matches" message
const searchbar = document.getElementById("searchbar");
const links = document.querySelectorAll(".champion-link");
const matches = document.getElementById("matches-text");

// Listen for input in the search bar to filter champion links
searchbar.addEventListener("input", function () {
    const searchText = this.value.toLowerCase();
    let hasMatches = false;

    links.forEach(link => {
        const champion = link.getAttribute("data-name");
        if (searchText.length > 0 && champion.includes(searchText)) { // checks if there is input and if any champions names includes the input
            link.style.display = "block"; // Show matching champion
            hasMatches = true;
        } else {
            link.style.display = "none"; // Hide non-matching champion
        }
    });

    // Show "No matches found" if nothing matches
    if (searchText.length > 0 && hasMatches == false) {
        matches.style.display = "block";
    } else {
        matches.style.display = "none";
    }
});

// Get form and select elements for updating champion stats
const champSelect = document.getElementById("champion-select");
const laneSelectContainer = document.getElementById("lane-select-container");
const form = document.getElementById("champion-form");
const status = document.getElementById("status");

// When a champion is selected, fetch available lanes and show lane dropdown
champSelect.addEventListener("change", () => {
    const champId = champSelect.value;
    form.style.display = "none"; // Hide form until lane is selected
    
    fetch(`/get-available-lanes/${champId}`)
        .then(res => res.json())
        .then(data => {
            const laneSelect = document.getElementById("lane-select");
            laneSelect.innerHTML = `<option>-- Choose a Lane --</option>`;

            data.lanes.forEach(lane => {
                const option = document.createElement("option");
                option.value = lane.lane_id;
                option.textContent = lane.lane_name;
                laneSelect.appendChild(option); // Add lane options dynamically
            });
            laneSelectContainer.style.display = "flex"; // Show lane select container
        });
});

// When a lane is selected, fetch champion stats and add form data
document.getElementById("lane-select").addEventListener("change", () => {
    const champId = document.getElementById("champion-select").value;
    const laneId = document.getElementById("lane-select").value;

    fetch(`/get-champion-stats/${champId}/${laneId}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("winrate").value = data.winrate;
            document.getElementById("pickrate").value = data.pickrate;
            document.getElementById("banrate").value = data.banrate;
            form.style.display = "block"; // Show form after data is received
        });
});

// Handle form submission to update champion stats
form.addEventListener("submit", (formdata) => {
    formdata.preventDefault(); // Prevent default form submission
    const champId = document.getElementById("champ_id").value;
    const laneId = document.getElementById("lane_id").value;
    const winrate = document.getElementById("winrate").value;
    const pickrate = document.getElementById("pickrate").value;
    const banrate = document.getElementById("banrate").value;

    // Send updated stats to server
    fetch("/update-champion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ champId, laneId, winrate, pickrate, banrate })
    })
    .then(res => res.json())
    .then(data => {
        status.textContent = data.message; // Show success/error message
        status.style.color = data.success ? "green" : "red";

        setTimeout(() => {
            status.textContent = ""; // Clear message after 2.5s
        }, 2500);
    });
});