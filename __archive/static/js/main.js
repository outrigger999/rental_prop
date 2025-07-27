document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired. main.js is running.');
    // Initial fetch of boxForm to ensure it exists on page load.
    // We will re-fetch it inside the click handler to ensure we have the latest reference.
    let initialBoxForm = document.getElementById('boxForm');

    if (initialBoxForm) {
        console.log('Initial boxForm element found on DOMContentLoaded:', initialBoxForm);
    } else {
        console.error('CRITICAL: boxForm element NOT found on DOMContentLoaded!');
        // We might still proceed to set up the listener, as the form could be dynamically added.
        // However, this is a strong indicator of a problem.
    }

    // The submit button is now correctly inside the form.
    // Remove the custom click handler and let the browser handle form submission natively.
    // This will allow HTML5 validation and normal form submission to work.
    console.log('Custom submit button click handler removed. Form will submit natively.');

    // --- Quick Add Category Modal Logic ---
    const quickAddCategoryBtn = document.getElementById('quickAddCategory');
    const quickCategoryModal = document.getElementById('quickCategoryModal');
    const quickCategoryForm = document.getElementById('quickCategoryForm');
    const addCategoryBtn = document.getElementById('addCategoryBtn');
    const newCategoryNameInput = document.getElementById('newCategoryName');
    const categorySelect = document.getElementById('category');
    
    // Use the search filter that's now in the HTML template
    if (categorySelect) {
        console.log('[CategorySearch] Setting up category search filter');
        try {
            const searchInput = document.getElementById('categorySearch');
            
            if (searchInput) {
                console.log('[CategorySearch] Found search input in HTML');
                
                // Add filtering functionality with visual feedback
                searchInput.addEventListener('input', function() {
                    const filter = this.value.toLowerCase();
                    console.log(`[CategorySearch] Filtering for: "${filter}"`);
                    let matchCount = 0;
                    
                    // Get status message from the HTML template
                    const statusMessage = document.getElementById('categoryFilterStatus');
                    
                    // Show clear button when there's text in the search box
                    const clearButton = document.getElementById('clearCategorySearch');
                    if (clearButton) {
                        clearButton.style.display = filter ? 'block' : 'block';
                    }
                    
                    // Apply filtering to options - HIDE non-matching options
                    Array.from(categorySelect.options).forEach(option => {
                        if (option.value === '') return; // Skip the placeholder option
                        const match = option.text.toLowerCase().includes(filter);
                        
                        // Actually hide non-matching options
                        if (match) {
                            option.style.display = ''; // Show matching options
                            option.style.backgroundColor = '#d4edda'; // Light green background
                            option.style.color = '#155724'; // Darker green text
                            option.style.fontWeight = 'bold';
                            matchCount++;
                        } else {
                            option.style.display = 'none'; // Hide non-matching options
                            // Reset styles (will apply when filter is cleared)
                            option.style.backgroundColor = '';
                            option.style.color = '';
                            option.style.fontWeight = '';
                        }
                    });
                    
                    // Update status message
                    if (filter) {
                        statusMessage.textContent = `Found ${matchCount} matching categories`;
                        statusMessage.style.color = matchCount > 0 ? '#28a745' : '#dc3545';
                    } else {
                        statusMessage.textContent = '';
                    }
                    
                    console.log(`[CategorySearch] Found ${matchCount} matching categories`);
                });
                
                // Focus the search input when clicking on the select
                categorySelect.addEventListener('click', function() {
                    if (searchInput.value === '') {
                        searchInput.focus();
                    }
                });
                
                // Add clear button functionality
                const clearButton = document.getElementById('clearCategorySearch');
                if (clearButton) {
                    clearButton.addEventListener('click', function() {
                        // Clear the search input
                        searchInput.value = '';
                        
                        // Reset the status message
                        const statusMessage = document.getElementById('categoryFilterStatus');
                        if (statusMessage) {
                            statusMessage.textContent = '';
                        }
                        
                        // Show all options and reset their styles
                        Array.from(categorySelect.options).forEach(option => {
                            option.style.display = '';
                            option.style.backgroundColor = '';
                            option.style.color = '';
                            option.style.fontWeight = '';
                        });
                        
                        // Focus back on the search input for convenience
                        searchInput.focus();
                    });
                }
                
                console.log('[CategorySearch] Category search filter setup successfully');
            } else {
                console.error('[CategorySearch] Search input element not found in HTML!');
            }
        } catch (err) {
            console.error('[CategorySearch] Failed to setup search filter:', err);
        }
    } else {
        console.error('[CategorySearch] Category select element not found!');
    }

    if (quickAddCategoryBtn && quickCategoryModal) {
        // Make the button easier to tap on mobile
        if (window.innerWidth <= 768) { // Mobile view
            quickAddCategoryBtn.style.height = '38px';
            quickAddCategoryBtn.style.padding = '6px 12px';
        }
        
        quickAddCategoryBtn.addEventListener('click', function() {
            console.log('[QuickAddCategory] + button clicked.');
            if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
                console.error('[QuickAddCategory] Bootstrap.Modal is not available!');
                alert('Error: Bootstrap modal JS is not loaded. Please check your scripts.');
                return;
            }
            if (!quickCategoryModal) {
                console.error('[QuickAddCategory] Modal element not found in DOM!');
                alert('Error: Modal element missing.');
                return;
            }
            try {
                const modal = new bootstrap.Modal(quickCategoryModal);
                modal.show();
                setTimeout(() => {
                    if (newCategoryNameInput) newCategoryNameInput.focus();
                }, 300);
            } catch (err) {
                console.error('[QuickAddCategory] Failed to show modal:', err);
                alert('Error: Failed to display add category dialog.');
            }
        });
    } else {
        if (!quickAddCategoryBtn) {
            console.warn('[QuickAddCategory] + button not found in DOM.');
        }
        if (!quickCategoryModal) {
            console.warn('[QuickAddCategory] Modal element not found in DOM.');
        }
    }

    if (addCategoryBtn && quickCategoryForm && categorySelect) {
        addCategoryBtn.addEventListener('click', async function() {
            const newCategoryName = newCategoryNameInput.value.trim();
            if (!newCategoryName) {
                newCategoryNameInput.classList.add('is-invalid');
                newCategoryNameInput.focus();
                return;
            }
            addCategoryBtn.disabled = true;
            addCategoryBtn.textContent = 'Adding...';

            try {
                // POST to the backend to add the new category
                const response = await fetch('/api/categories', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: newCategoryName })
                });
                if (!response.ok) {
                    // Try to extract error message from backend
                    let errorMsg = 'Failed to add category';
                    try {
                        const errJson = await response.json();
                        if (errJson && errJson.detail) errorMsg = errJson.detail;
                    } catch {}
                    throw new Error(errorMsg);
                }
                const newCategory = await response.json();

                // Check if the category name already exists in the dropdown
                const existingOptions = Array.from(categorySelect.options);
                const duplicate = existingOptions.find(opt => 
                    opt.textContent.toLowerCase() === newCategory.name.toLowerCase());
                
                if (duplicate) {
                    // If it exists, just select that option instead of adding a duplicate
                    duplicate.selected = true;
                    alert(`Category "${newCategory.name}" already exists! Using the existing category.`);
                } else {
                    // Add the new category to the select dropdown
                    const option = document.createElement('option');
                    option.value = newCategory.id;
                    option.textContent = newCategory.name;
                    option.selected = true;
                    categorySelect.appendChild(option);
                }

                // Hide the modal
                const modal = bootstrap.Modal.getInstance(quickCategoryModal);
                modal.hide();

                // Reset the input (since quickCategoryForm is now a div)
                newCategoryNameInput.value = '';
                newCategoryNameInput.classList.remove('is-invalid');
            } catch (error) {
                alert('Error adding category: ' + error.message);
            } finally {
                addCategoryBtn.disabled = false;
                addCategoryBtn.textContent = 'Add Category';
            }
        });

        // Remove invalid class on input
        newCategoryNameInput.addEventListener('input', function() {
            newCategoryNameInput.classList.remove('is-invalid');
        });
    }

    // Always reset modal form and validation when modal is closed
    if (quickCategoryModal && quickCategoryForm && newCategoryNameInput) {
        quickCategoryModal.addEventListener('hidden.bs.modal', function() {
            // Since quickCategoryForm is now a div, just clear the input and validation
            if (newCategoryNameInput) {
                newCategoryNameInput.value = '';
                newCategoryNameInput.classList.remove('is-invalid');
            }
        });
    }
    // --- End Quick Add Category Modal Logic ---
});
