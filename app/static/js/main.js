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

function searchItems() {
    let input = document
        .getElementById("searchInput")
        .value
        .trim()
        .toLowerCase();

    let hasVisibleItems = false;

    data.forEach((e) => {
        if (e.Task.includes(input)) {
            e.rowElement.style.display = "";
            hasVisibleItems = true;
        } else {
            e.rowElement.style.display = "none";
        }
    });

    const message = document.getElementById("noResultsMessage");

    if (hasVisibleItems || input === "") {
        message.style.display = "none";
    } else {
        message.style.display = "block";
    }
}