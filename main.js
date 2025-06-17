document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // Get current theme
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            // Toggle theme
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Set the new theme
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            
            // Save theme preference
            localStorage.setItem('theme', newTheme);
        });
    }
    
    // Auto-redirect from welcome page to role selection after 5 seconds
    const redirectMessage = document.getElementById('redirectMessage');
    const countdownSpan = document.getElementById('countdown');
    const getStartedBtn = document.getElementById('getStartedBtn');
    
    if (redirectMessage && countdownSpan && getStartedBtn) {
        let count = 5;
        redirectMessage.style.display = 'block';
        
        const countdownTimer = setInterval(function() {
            count--;
            countdownSpan.textContent = count;
            
            if (count <= 0) {
                clearInterval(countdownTimer);
                // Redirect to role selection page
                window.location.href = getStartedBtn.getAttribute('href');
            }
        }, 1000);
    }
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle role selection cards
    const roleCards = document.querySelectorAll('.role-card');
    if (roleCards.length > 0) {
        roleCards.forEach(card => {
            card.addEventListener('click', function() {
                const role = this.getAttribute('data-role');
                if (role) {
                    document.getElementById('role').value = role;
                    document.getElementById('role-form').submit();
                }
            });
        });
    }

    // Handle file input display
    const fileInputs = document.querySelectorAll('.custom-file-input');
    if (fileInputs.length > 0) {
        fileInputs.forEach(input => {
            input.addEventListener('change', function(e) {
                const fileName = e.target.files[0].name;
                const label = e.target.nextElementSibling;
                label.textContent = fileName;
            });
        });
    }

    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                const closeButton = message.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }, 5000);
        });
    }

    // Handle password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    if (passwordToggles.length > 0) {
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const passwordField = document.getElementById(this.getAttribute('data-target'));
                if (passwordField) {
                    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordField.setAttribute('type', type);
                    
                    // Toggle icon
                    this.innerHTML = type === 'password' ? 
                        '<i class="fas fa-eye"></i>' : 
                        '<i class="fas fa-eye-slash"></i>';
                }
            });
        });
    }

    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // Set theme based on localStorage or user preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    }
});
