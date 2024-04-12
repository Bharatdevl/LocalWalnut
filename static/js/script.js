//*** Header ****//
$(function () {
    $("#header").load("header.html");
});

//*** Sidebar ***//
$(function () {
    $("#sidebar-container").load("sidebar.html");
});

//*** Toggle ***//
function showMenu() {
    var element = document.getElementById("sidebar-wrapper");
    element.classList.toggle("mob-menu");
}
