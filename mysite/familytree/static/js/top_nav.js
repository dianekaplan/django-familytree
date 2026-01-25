// Refactor for unobtrusive JavaScript on logout

document.addEventListener('DOMContentLoaded', function () {
    // Delegate logout functionality to all logout links
    var logoutLinks = document.querySelectorAll('.logout-link');
    var logoutForm = document.getElementById('logout-form');
    if (logoutForm) {
        logoutLinks.forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                logoutForm.submit();
            });
        });
    }
});
