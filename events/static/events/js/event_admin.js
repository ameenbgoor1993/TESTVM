(function () {
    'use strict';

    console.log('Event admin JS loaded');

    function initGenderToggle() {
        // Get all radio buttons for gender_preference
        const radios = document.querySelectorAll('input[name="gender_preference"]');
        console.log('Found radios:', radios.length);

        if (radios.length === 0) {
            console.warn('No gender preference radio buttons found');
            return;
        }

        // Get the form rows - Jazzmin uses .form-group instead of .form-row
        const generalRow = document.querySelector('.form-group.field-required_volunteers');
        const specificRow1 = document.querySelector('.form-group.field-required_males');
        const specificRow2 = document.querySelector('.form-group.field-extra_males');

        console.log('General row:', generalRow);
        console.log('Specific row 1:', specificRow1);
        console.log('Specific row 2:', specificRow2);

        function updateVisibility() {
            // Find which radio is checked
            let selectedValue = null;
            radios.forEach(radio => {
                if (radio.checked) {
                    selectedValue = radio.value;
                }
            });

            console.log('Selected value:', selectedValue);

            if (selectedValue === 'GENERAL') {
                // Show general fields, hide specific
                if (generalRow) generalRow.style.display = '';
                if (specificRow1) specificRow1.style.display = 'none';
                if (specificRow2) specificRow2.style.display = 'none';
            } else if (selectedValue === 'SPECIFIC') {
                // Hide general fields, show specific
                if (generalRow) generalRow.style.display = 'none';
                if (specificRow1) specificRow1.style.display = '';
                if (specificRow2) specificRow2.style.display = '';
            }
        }

        // Attach change listeners
        radios.forEach(radio => {
            radio.addEventListener('change', updateVisibility);
        });

        // Set initial state
        updateVisibility();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGenderToggle);
    } else {
        initGenderToggle();
    }
})();
