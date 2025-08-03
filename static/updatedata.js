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

        const select = document.getElementById("champion-select");
        const form = document.getElementById("champion-form");
        const status = document.getElementById("status");

        select.addEventListener("change", () => {
            const champId = select.value;
            fetch(`/get-champion-stats/${champId}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById("champ_id").value = champId;
                    document.getElementById("winrate").value = data.winrate;
                    document.getElementById("pickrate").value = data.pickrate;
                    document.getElementById("banrate").value = data.banrate;
                    form.style.display = "block";
                    
                });
        });

        form.addEventListener("submit", (formdata) => {
            formdata.preventDefault();
            const champId = document.getElementById("champ_id").value;
            const winrate = document.getElementById("winrate").value;
            const pickrate = document.getElementById("pickrate").value;
            const banrate = document.getElementById("banrate").value;

            fetch("/update-champion", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ champId, winrate, pickrate, banrate })
            })
            .then(res => res.json())
            .then(data => {
                status.textContent = data.message;
                status.style.color = data.success ? "green" : "red";

                setTimeout(() => {
                    status.textContent = "";
                    }, 2500);
            });
        });