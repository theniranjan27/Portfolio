// Niranjan Portfolio Main Client Script
document.addEventListener("DOMContentLoaded", () => {
    // Clear any leftover legacy auth cookies
    ["admin_logged_in", "user_logged_in", "user_name"].forEach(cookieName => {
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    });

    // Auto-fade flash messages
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            msg.style.opacity = "0";
            msg.style.transform = "translateY(-10px)";
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});