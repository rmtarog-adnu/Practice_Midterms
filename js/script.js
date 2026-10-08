console.log("Mini Management System loaded.");


const searchInput = document.getElementById("searchInput");
const tableRows = document.querySelectorAll("tbody tr");

if (searchInput) {
    searchInput.addEventListener("input", function () {

        const searchValue = searchInput.value.toLowerCase();

        tableRows.forEach(function (row) {

            const rowText = row.textContent.toLowerCase();

            if (rowText.includes(searchValue)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }

        });

    });
}

