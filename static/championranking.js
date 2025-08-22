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

// Handle "Update Data" button click
document.getElementById("update-button").addEventListener("click", () => {
    const password = prompt("Enter the admin password:"); // Prompt for password

    if (password === null) {
        return; // Do nothing if user cancels
    }

    // Send entered password to app.py to check
    fetch("/check-password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success == true) {
            window.location.href = "/updatedata"; // Redirect if password correct
        } else {
            const status = document.getElementById("update-status");
            status.textContent = "Incorrect password."; // Show error
            status.style.color = "red";

            setTimeout(() => {
                status.textContent = ""; // Clear error after 2.5s
            }, 2500);
        }
    })
});
