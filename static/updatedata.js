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

        const champSelect = document.getElementById("champion-select");
        const laneSelectContainer = document.getElementById("lane-select-container");
        const form = document.getElementById("champion-form");
        const status = document.getElementById("status");

        champSelect.addEventListener("change", () => {
            const champId = champSelect.value;
            form.style.display = "none";
            
            fetch(`/get-available-lanes/${champId}`)
                .then(res => res.json())
                .then(data => {
                    const laneSelect = document.getElementById("lane-select");
                    laneSelect.innerHTML = `<option>-- Choose a Lane --</option>`;

                    data.lanes.forEach(lane => {
                        const option = document.createElement("option");
                        option.value = lane.lane_id;
                        option.textContent = lane.lane_name;
                        laneSelect.appendChild(option);
                    });
                    laneSelectContainer.style.display = "flex";
                });
        });

        document.getElementById("lane-select").addEventListener("change", () => {
            const champId = document.getElementById("champion-select").value;
            const laneId = document.getElementById("lane-select").value;

            fetch(`/get-champion-stats/${champId}/${laneId}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById("champ_id").value = champId;
                    document.getElementById("lane_id").value = laneId;
                    document.getElementById("winrate").value = data.winrate;
                    document.getElementById("pickrate").value = data.pickrate;
                    document.getElementById("banrate").value = data.banrate;
                    form.style.display = "block";
                });
        });


        form.addEventListener("submit", (formdata) => {
            formdata.preventDefault();
            const champId = document.getElementById("champ_id").value;
            const laneId = document.getElementById("lane_id").value;
            const winrate = document.getElementById("winrate").value;
            const pickrate = document.getElementById("pickrate").value;
            const banrate = document.getElementById("banrate").value;

            fetch("/update-champion", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ champId, laneId, winrate, pickrate, banrate })
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