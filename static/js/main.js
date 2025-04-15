document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Enhanced mood selector functionality
    const moodOptions = document.querySelectorAll('.mood-option input[type="radio"]');
    const moodLabels = document.querySelectorAll('.mood-label');
    
    moodOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Add a subtle animation when selecting a mood
            if (this.checked) {
                const label = this.nextElementSibling;
                label.style.transform = 'scale(1.1)';
                
                setTimeout(() => {
                    label.style.transform = 'scale(1.05)';
                }, 150);
            }
        });
    });
    
    // Journal entry character counter (optional enhancement)
    const contentTextarea = document.querySelector('textarea[name="content"]');
    
    if (contentTextarea) {
        // Create and add a character counter element
        const counterDiv = document.createElement('div');
        counterDiv.className = 'form-text text-end mt-1';
        counterDiv.id = 'charCounter';
        contentTextarea.parentNode.appendChild(counterDiv);
        
        // Update the counter when typing
        contentTextarea.addEventListener('input', updateCharacterCount);
        
        // Initial count
        updateCharacterCount();
        
        function updateCharacterCount() {
            const count = contentTextarea.value.length;
            counterDiv.textContent = `${count} characters`;
        }
    }
});
