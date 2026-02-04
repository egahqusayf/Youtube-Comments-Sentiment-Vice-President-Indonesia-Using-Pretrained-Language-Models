let page = 1;
let localLabels = {}; // Simpan label di browser

const loadingEl = document.getElementById("loading");

function showLoading(show) {
    loadingEl.style.display = show ? "flex" : "none";
}

function loadData() {
    showLoading(true);
    fetch(`/get_data?page=${page}`)
        .then(res => res.json())
        .then(res => {
            showLoading(false);
            const container = document.getElementById("comments");
            container.innerHTML = "";

            res.data.forEach(item => {
                const isLabeled = item.label !== "";
                const cardClass = isLabeled ? "card done" : "card";
                container.innerHTML += `
                    <div class="${cardClass}">
                        <p>${item.comment}</p>
                        <div class="buttons">
                            <button ${isLabeled ? "disabled" : ""} onclick="setLabel(${item.idx}, -1)">😡 -1</button>
                            <button ${isLabeled ? "disabled" : ""} onclick="setLabel(${item.idx}, 0)">😐 0</button>
                            <button ${isLabeled ? "disabled" : ""} onclick="setLabel(${item.idx}, 1)">😊 1</button>
                        </div>
                    </div>
                `;
            });

            // Update stats realtime
            document.getElementById("total").innerText = res.stats.total;
            document.getElementById("neg").innerText = res.stats["-1"];
            document.getElementById("neu").innerText = res.stats["0"];
            document.getElementById("pos").innerText = res.stats["1"];
        })
        .catch(err => {
            showLoading(false);
            console.error(err);
        });
}

function setLabel(index, label) {
    localLabels[index] = label;
    loadData(); // Update UI langsung
}

function saveAll() {
    if (Object.keys(localLabels).length === 0) return;

    showLoading(true);
    fetch("/update_label", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bulk: localLabels })
    })
    .then(res => res.json())
    .then(res => {
        localLabels = {}; // clear setelah save
        loadData();
    })
    .catch(err => console.error(err))
    .finally(() => showLoading(false));
}

function nextPage() {
    page++;
    loadData();
}

function prevPage() {
    if (page > 1) page--;
    loadData();
}

// Load pertama kali
window.onload = loadData;
