document.addEventListener("DOMContentLoaded", function() {
    const navbarButton = document.getElementById("navbarButton");
    const navbarMenu = document.getElementById("navbarMenu");
    const content = document.querySelector(".content");

    navbarButton.addEventListener("mouseover", function() {
        navbarMenu.style.left = "0";
    });

    navbarMenu.addEventListener("mouseleave", function() {
        navbarMenu.style.left = "-250px";
    });

    navbarButton.addEventListener("click", function() {
        navbarMenu.style.left = "0";
    });

    content.addEventListener("click", function() {
        navbarMenu.style.left = "-250px";
    });
});
