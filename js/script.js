console.log("Mini Management System loaded.");

// =========================
// ADD RECORD
// =========================

const recordForm = document.getElementById("recordForm");

if (recordForm) {

    recordForm.addEventListener("submit", function (event) {

        event.preventDefault();

        const name = document.getElementById("name").value;
        const description = document.getElementById("description").value;
        const category = document.getElementById("category").value;

        const tableBody = document.querySelector("tbody");

        const newRow = document.createElement("tr");

        const newId = tableBody.rows.length + 1;

        newRow.innerHTML = `
    <td>${newId}</td>
    <td>${name}</td>
    <td>${description}</td>
    <td>${category}</td>
    <td>
        <button type="button" class="edit-btn">
            Edit
        </button>

        <button type="button" class="delete-btn">
            Delete
        </button>
    </td>
`;

        tableBody.appendChild(newRow);

        // Make the new Edit button work
        setupEditButton(newRow.querySelector(".edit-btn"));
        setupDeleteButton(newRow.querySelector(".delete-btn"));

        // Clear the form
        recordForm.reset();

    });

}


// =========================
// SEARCH RECORDS
// =========================

const searchInput = document.getElementById("searchInput");

if (searchInput) {

    searchInput.addEventListener("input", function () {

        const searchValue = searchInput.value.toLowerCase();

        const tableRows = document.querySelectorAll("tbody tr");

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


// =========================
// EDIT RECORD
// =========================

const editModal = document.getElementById("editModal");
const editForm = document.getElementById("editForm");
const cancelEdit = document.getElementById("cancelEdit");


// Function for Edit buttons
function setupEditButton(button) {

    if (!button) {
        return;
    }

    button.addEventListener("click", function () {

        const row = button.closest("tr");

        document.getElementById("editName").value =
            row.cells[1].textContent.trim();

        document.getElementById("editDescription").value =
            row.cells[2].textContent.trim();

        document.getElementById("editCategory").value =
            row.cells[3].textContent.trim();

        editModal.style.display = "block";

        editForm.dataset.rowIndex = row.rowIndex;

    });

}


// Setup existing Edit buttons
if (editModal && editForm) {

    const editButtons = document.querySelectorAll(".edit-btn");

    editButtons.forEach(function (button) {
        setupEditButton(button);
    });


    // Cancel Edit
    if (cancelEdit) {

        cancelEdit.addEventListener("click", function () {

            editModal.style.display = "none";

        });

    }


    // Save Changes
    editForm.addEventListener("submit", function (event) {

        event.preventDefault();

        const rowIndex = editForm.dataset.rowIndex;

        const tableBody = document.querySelector("tbody");

        const row = tableBody.rows[rowIndex - 1];

        row.cells[1].textContent =
            document.getElementById("editName").value;

        row.cells[2].textContent =
            document.getElementById("editDescription").value;

        row.cells[3].textContent =
            document.getElementById("editCategory").value;

        editModal.style.display = "none";

    });

}

// =========================
// DELETE RECORD
// =========================

function setupDeleteButton(button) {

    if (!button) {
        return;
    }

    button.addEventListener("click", function () {

        const row = button.closest("tr");

        const recordName = row.cells[1].textContent;

        const confirmDelete = confirm(
            "Are you sure you want to delete " + recordName + "?"
        );

        if (confirmDelete) {

            row.remove();

        }

    });

}


// Setup existing Delete buttons
const deleteButtons = document.querySelectorAll(".delete-btn");

deleteButtons.forEach(function (button) {
    setupDeleteButton(button);
});

// =========================
// FILTER RECORDS
// =========================

const categoryFilter = document.getElementById("categoryFilter");

if (categoryFilter) {

    categoryFilter.addEventListener("change", function () {

        const selectedCategory =
            categoryFilter.value.toLowerCase();

        const tableRows =
            document.querySelectorAll("tbody tr");

        tableRows.forEach(function (row) {

            const category =
                row.cells[3].textContent.toLowerCase().trim();

            if (
                selectedCategory === "all" ||
                category === selectedCategory
            ) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    });

}

// =========================
// LOADING MESSAGE
// =========================

const loadingMessage = document.getElementById("loadingMessage");

if (loadingMessage) {

    setTimeout(function () {

        loadingMessage.style.display = "none";

    }, 1000);

}