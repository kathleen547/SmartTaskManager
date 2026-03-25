/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */


function func1() {
  document.getElementById("filter-dropdown").classList.toggle("show");
}

function func2() {
  document.getElementById("status-dropdown").classList.toggle("show");
}

function confirmDelete(){
    return confirm("Are you sure to delete this task?");
}


const table = document.getElementById("project-table");
const tableBody = table.getElementsByTagName("tbody")[0];
const rows = tableBody.querySelectorAll("tr");
const flag = {Task: false, Status: false, Priority: false, DueDate: false, AssignedTo: false, Actions: false};
let data = [];

rows.forEach((row) => {
const title = row.querySelector(".task-title").textContent;
const status = row.querySelector(".task-status").textContent;
const priority = row.querySelector(".task-priority").textContent;
const dueDate = row.querySelector(".task-date").textContent;
const assigned = row.querySelector(".task-owner").textContent;
const actions = row.querySelector(".task-actions").textContent;

let task = {
    Task: title.trim().toLowerCase(),
    Status: status.trim().toLowerCase(),
    Priority: priority.trim().toLowerCase(),
    DueDate: dueDate.trim(),
    AssignedTo: assigned.trim(),
    Actions: actions.trim(),
    rowElement: row
    };
data.push(task);
});

// dropdown
function setupDropdown(buttonId, dropdownId) {
    const button = document.getElementById(buttonId);
    const dropdown = document.getElementById(dropdownId);
    const options = dropdown.querySelectorAll("a");

    button.addEventListener("click", (event) => {
        event.stopPropagation();

        document.querySelectorAll(".dropdown-content").forEach((menu) => {
            if (menu !== dropdown) {
                menu.classList.remove("show");
            }
    });

    dropdown.classList.toggle("show");
});

    options.forEach((option) => {
        option.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            const selectedValue = option.dataset.value;
            const selectedText = option.textContent.trim();

            button.dataset.value = selectedValue;
            button.textContent = selectedText;

            dropdown.classList.remove("show");

            applyFilters();
        });
    });

    return { button, dropdown };
}

const statusUI = setupDropdown("statusFilter", "status-dropdown");
const priorityUI = setupDropdown("priorityFilter", "priority-dropdown");

document.addEventListener("click", (event) => {
    if (
        !statusUI.button.contains(event.target) &&
        !statusUI.dropdown.contains(event.target)
    ) {
        statusUI.dropdown.classList.remove("show");
    }

    if (
        !priorityUI.button.contains(event.target) &&
        !priorityUI.dropdown.contains(event.target)
    ) {
        priorityUI.dropdown.classList.remove("show");
    }
});


function applyFilters() {
    const searchValue = document
        .getElementById("searchInput")
        .value
        .trim()
        .toLowerCase();

    const statusValue = document
        .getElementById("statusFilter")
        .dataset.value
        .trim()
        .toLowerCase();

    const priorityValue = document
        .getElementById("priorityFilter")
        .dataset.value
        .trim()
        .toLowerCase();

    const message = document.getElementById("noResultsMessage");

    let hasVisibleItems = false;

    data.forEach((task) => {
        const matchesSearch = task.Task.includes(searchValue);
        const matchesStatus = statusValue === "all" || task.Status === statusValue;
        const matchesPriority = priorityValue === "all" || task.Priority === priorityValue;

        if (matchesSearch && matchesStatus && matchesPriority) {
            task.rowElement.style.display = "";
            hasVisibleItems = true;
        } else {
            task.rowElement.style.display = "none";
        }
    });

    if (hasVisibleItems) {
        message.style.display = "none";
    } else {
        message.style.display = "block";
    }
}