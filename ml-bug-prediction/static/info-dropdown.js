// Info Dropdown Functionality Fix
function toggleInfoDropdown() {
    console.log('🔧 toggleInfoDropdown function called!');
    const dropdown = document.getElementById('infoDropdownMenu');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible) {
            // Close dropdown when clicking outside
            setTimeout(() => {
                document.addEventListener('click', function closeDropdown(e) {
                    if (!e.target.closest('.info-dropdown')) {
                        dropdown.style.display = 'none';
                        document.removeEventListener('click', closeDropdown);
                    }
                });
            }, 100);
        }
    } else {
        console.error('❌ Info dropdown menu element not found!');
    }
}

// Ensure function is globally available
window.toggleInfoDropdown = toggleInfoDropdown;

console.log('✅ Info dropdown function registered successfully from external file'); 