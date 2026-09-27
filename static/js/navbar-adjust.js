// navbar-adjust.js
// Dynamically adjusts navbar links depending on whether the site
// is running via Flask (port 5000) or statically (Live Server / file protocol).

document.addEventListener("DOMContentLoaded", () => {
    // Detect Flask vs Static
    const isFlask = window.location.port === "5000" || window.location.port === "";

    const homeLinks = document.querySelectorAll(".nav-link-home");
    const projectsLinks = document.querySelectorAll(".nav-link-projects");
    const aboutLinks = document.querySelectorAll(".nav-link-about");
    const blogLinks = document.querySelectorAll(".nav-link-blog");
    const contactLinks = document.querySelectorAll(".nav-link-contact, .nav-btn-contact");
    const brandLink = document.querySelector(".navbar .brand");

    if (isFlask) {
        homeLinks.forEach(el => el.setAttribute("href", "/"));
        projectsLinks.forEach(el => el.setAttribute("href", "/projects"));
        aboutLinks.forEach(el => el.setAttribute("href", "/about"));
        blogLinks.forEach(el => el.setAttribute("href", "/blog"));
        contactLinks.forEach(el => el.setAttribute("href", "/contact"));
    } else {
        homeLinks.forEach(el => el.setAttribute("href", "../../templates/index.html"));
        projectsLinks.forEach(el => el.setAttribute("href", "../../templates/projects.html"));
        aboutLinks.forEach(el => el.setAttribute("href", "../../templates/about.html"));
        blogLinks.forEach(el => el.setAttribute("href", "../../templates/blog.html"));
        contactLinks.forEach(el => el.setAttribute("href", "../../templates/contact.html"));
    }

    if (brandLink) {
        brandLink.style.cursor = "pointer";
        brandLink.addEventListener("click", () => {
            window.location.href = isFlask ? "/" : "../../templates/index.html";
        });
    }
});
