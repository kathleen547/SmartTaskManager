/**
 * Client-side interactivity for the project task table.
 * Handles:
 *  - Filter dropdown toggle visibility
 *  - Task deletion confirmation dialog
 *  - Real-time search and filter logic for the task table
 */


// ─────────────────────────────────────────────
//  DROPDOWN TOGGLE HELPERS (legacy inline usage)
// ─────────────────────────────────────────────

/** Toggles visibility of the filter dropdown menu */
function func1() {
  document.getElementById("filter-dropdown").classList.toggle("show");
}

/** Toggles visibility of the status dropdown menu */
function func2() {
  document.getElementById("status-dropdown").classList.toggle("show");
}

/**
 * Displays a browser confirmation dialog before deleting a task.
 * @returns {boolean} true if user confirms, false if cancelled.
 */
function confirmDelete() {
  return confirm("Are you sure to delete this task?");
}


// ─────────────────────────────────────────────
//  TABLE DATA EXTRACTION
// ─────────────────────────────────────────────

const table = document.getElementById("project-table");
const tableBody = table.getElementsByTagName("tbody")[0];
const rows = tableBody.querySelectorAll("tr");

/**
 * Tracks sort direction state for each column.
 * Each key maps to a boolean: false = ascending, true = descending.
 */
const flag = {
  Task: false,
  Status: false,
  Priority: false,
  DueDate: false,
  AssignedTo: false,
  Actions: false
};

/** Parsed task data extracted from table rows for client-side filtering */
let data = [];

// Extract data from each row and store as structured objects
rows.forEach((row) => {
  const title   = row.querySelector(".task-title").textContent;
  const status  = row.querySelector(".task-status").textContent;
  const priority = row.querySelector(".task-priority").textContent;
  const dueDate = row.querySelector(".task-date").textContent;
  const assigned = row.querySelector(".task-owner").textContent;
  const actions = row.querySelector(".task-actions").textContent;

  // Store normalized (lowercased/trimmed) values alongside the DOM row reference
  let task = {
    Task:       title.trim().toLowerCase(),
    Status:     status.trim().toLowerCase(),
    Priority:   priority.trim().toLowerCase(),
    DueDate:    dueDate.trim(),
    AssignedTo: assigned.trim(),
    Actions:    actions.trim(),
    rowElement: row   // Reference to the actual <tr> for show/hide control
  };

  data.push(task);
});


// ─────────────────────────────────────────────
//  DROPDOWN SETUP
// ─────────────────────────────────────────────

/**
 * Sets up a custom dropdown component with click-outside-to-close behavior
 * and automatic filter triggering on option selection.
 *
 * @param {string} buttonId   - The ID of the button that toggles the dropdown.
 * @param {string} dropdownId - The ID of the dropdown content container.
 * @returns {{ button: HTMLElement, dropdown: HTMLElement }}
 *          References to the button and dropdown elements.
 */
function setupDropdown(buttonId, dropdownId) {
  const button   = document.getElementById(buttonId);
  const dropdown = document.getElementById(dropdownId);
  const options  = dropdown.querySelectorAll("a");

  // Toggle the dropdown open/closed when the button is clicked
  button.addEventListener("click", (event) => {
    event.stopPropagation(); // Prevent the document click listener from closing it immediately

    // Close all other open dropdowns before opening this one
    document.querySelectorAll(".dropdown-content").forEach((menu) => {
      if (menu !== dropdown) {
        menu.classList.remove("show");
      }
    });

    dropdown.classList.toggle("show");
  });

  // Handle option selection within the dropdown
  options.forEach((option) => {
    option.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();

      const selectedValue = option.dataset.value;   // Filter value (e.g. "todo")
      const selectedText  = option.textContent.trim(); // Display label

      // Update the button to reflect current selection
      button.dataset.value = selectedValue;
      button.textContent   = selectedText;

      dropdown.classList.remove("show");

      // Re-run filters with the newly selected value
      applyFilters();
    });
  });

  return { button, dropdown };
}

// Initialize both filter dropdowns
const statusUI   = setupDropdown("statusFilter",   "status-dropdown");
const priorityUI = setupDropdown("priorityFilter", "priority-dropdown");


// ─────────────────────────────────────────────
//  CLICK-OUTSIDE TO CLOSE DROPDOWNS
// ─────────────────────────────────────────────

/**
 * Global click listener that closes any open dropdown
 * when the user clicks outside of it.
 */
document.addEventListener("click", (event) => {
  // Close status dropdown if click is outside button and menu
  if (
    !statusUI.button.contains(event.target) &&
    !statusUI.dropdown.contains(event.target)
  ) {
    statusUI.dropdown.classList.remove("show");
  }

  // Close priority dropdown if click is outside button and menu
  if (
    !priorityUI.button.contains(event.target) &&
    !priorityUI.dropdown.contains(event.target)
  ) {
    priorityUI.dropdown.classList.remove("show");
  }
});


// ─────────────────────────────────────────────
//  FILTER LOGIC
// ─────────────────────────────────────────────

/**
 * Filters the task table rows based on the current search input,
 * selected status, and selected priority.
 *
 * A row is shown only if it matches ALL active filters simultaneously.
 * If no rows match, a "no results" message is displayed.
 */
function applyFilters() {
  // Read current search term (normalized to lowercase)
  const searchValue = document
    .getElementById("searchInput")
    .value.trim().toLowerCase();

  // Read selected status filter value from button's data attribute
  const statusValue = document
    .getElementById("statusFilter")
    .dataset.value.trim().toLowerCase();

  // Read selected priority filter value from button's data attribute
  const priorityValue = document
    .getElementById("priorityFilter")
    .dataset.value.trim().toLowerCase();

  const message = document.getElementById("noResultsMessage");
  let hasVisibleItems = false;

  data.forEach((task) => {
    // Check each filter condition independently
    const matchesSearch   = task.Task.includes(searchValue);
    const matchesStatus   = statusValue === "all"   || task.Status === statusValue;
    const matchesPriority = priorityValue === "all" || task.Priority === priorityValue;

    if (matchesSearch && matchesStatus && matchesPriority) {
      // Show row if all filters pass
      task.rowElement.style.display = "";
      hasVisibleItems = true;
    } else {
      // Hide row if any filter does not match
      task.rowElement.style.display = "none";
    }
  });

  // Toggle the empty-state message based on whether any rows are visible
  message.style.display = hasVisibleItems ? "none" : "block";
}