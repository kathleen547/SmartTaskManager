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