const searchbar = document.getElementById("searchbar");
        const links = document.querySelectorAll(".champion-link");
        const matches = document.getElementById("matches-text");

        searchbar.addEventListener("input", function () {
            const searchText = this.value.toLowerCase();
            let hasMatches = false;

            links.forEach(link => {
                const champion = link.getAttribute("data-name");
                if (searchText.length > 0 && champion.includes(searchText)) {
                    link.style.display = "block";
                    hasMatches = true;
                } else {
                    link.style.display = "none";
                }
            });

            if (searchText.length > 0 && hasMatches == false) {
                matches.style.display = "block";
            }
            else {
                matches.style.display = "none";
            }
        });


        document.getElementById("update-button").addEventListener("click", () => {
            const password = prompt("Enter the admin password:");

            if (password === null) {
                return;
            }

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
                    window.location.href = "/updatedata";
                } else {
                    const status = document.getElementById("update-status");
                    status.textContent = "Incorrect password.";
                    status.style.color = "red";

                    setTimeout(() => {
                        status.textContent = "";
                        }, 2500);
                }
            })
        });