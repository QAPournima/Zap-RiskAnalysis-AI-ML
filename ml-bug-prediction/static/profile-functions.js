        // ========================================================================================
        // 👤 USER PROFILE DROPDOWN FUNCTIONALITY
        // ========================================================================================

        // Profile Dropdown Functionality
        function toggleProfileDropdown() {
            const dropdown = document.getElementById("profileDropdownMenu");
            if (dropdown) {
                const isVisible = dropdown.style.display === "block";
                dropdown.style.display = isVisible ? "none" : "block";
                
                if (!isVisible) {
                    // Close dropdown when clicking outside
                    setTimeout(() => {
                        document.addEventListener("click", function closeDropdown(e) {
                            if (!e.target.closest(".profile-dropdown")) {
                                dropdown.style.display = "none";
                                document.removeEventListener("click", closeDropdown);
                            }
                        });
                    }, 100);
                }
            }
        }

        function closeProfileDropdown() {
            const dropdown = document.getElementById("profileDropdownMenu");
            if (dropdown) {
                dropdown.style.display = "none";
            }
        }

        // ========================================================================================
        // 👤 PROFILE MODAL FUNCTIONALITY  
        // ========================================================================================

        // Open Profile Sidebar
        function openProfileModal() {
            // Create sidebar if it doesn't exist
            if (!document.getElementById('profileSidebar')) {
                createProfileSidebar();
            }
            
            const sidebar = document.getElementById('profileSidebar');
            if (sidebar) {
                // Load current profile data into sidebar
                loadProfileInSidebar();
                
                // Show sidebar with slide-in animation
                sidebar.style.display = 'flex';
                setTimeout(() => {
                    sidebar.classList.add('active');
                }, 10);
                
                // Add escape key handler
                document.addEventListener('keydown', handleSidebarEscape);
                
                // Prevent body scrolling
                document.body.style.overflow = 'hidden';
                
                console.log('👤 Profile sidebar opened');
            } else {
                console.error('❌ Profile sidebar element not found');
            }
        }

        // Create Profile Sidebar HTML
        function createProfileSidebar() {
            const sidebarHTML = `
                <div id="profileSidebar" class="profile-sidebar">
                    <div class="profile-sidebar-overlay" onclick="closeProfileSidebar()"></div>
                    <div class="profile-sidebar-content">
                        <div class="profile-sidebar-header">
                            <h3><i class="fas fa-user"></i> User Profile</h3>
                            <p>Manage your account settings</p>
                            <button class="profile-sidebar-close" onclick="closeProfileSidebar()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <div class="profile-sidebar-body">
                            <div class="profile-sidebar-tabs">
                                <button class="profile-sidebar-tab active" data-tab="profile">
                                    <i class="fas fa-user"></i> Edit Profile
                                </button>
                                <button class="profile-sidebar-tab" data-tab="password">
                                    <i class="fas fa-lock"></i> Change Password
                                </button>
                            </div>

                            <!-- Profile Tab -->
                            <div class="profile-sidebar-tab-content active" id="profileSidebarTabContent">
                                <div class="profile-sidebar-alert profile-sidebar-alert-success" id="profileSidebarSuccessAlert">
                                    <i class="fas fa-check-circle"></i>
                                    <span id="profileSidebarSuccessMessage"></span>
                                </div>
                                <div class="profile-sidebar-alert profile-sidebar-alert-danger" id="profileSidebarErrorAlert">
                                    <i class="fas fa-exclamation-circle"></i>
                                    <span id="profileSidebarErrorMessage"></span>
                                </div>
                                <form id="profileSidebarForm">
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarName" class="profile-sidebar-form-label">Full Name</label>
                                        <input type="text" id="sidebarName" name="name" class="profile-sidebar-form-control" required>
                                    </div>
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarEmail" class="profile-sidebar-form-label">Email Address</label>
                                        <input type="email" id="sidebarEmail" name="email" class="profile-sidebar-form-control" disabled>
                                    </div>
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarCompanyName" class="profile-sidebar-form-label">Company Name</label>
                                        <input type="text" id="sidebarCompanyName" name="company_name" class="profile-sidebar-form-control" required>
                                    </div>
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarRole" class="profile-sidebar-form-label">Role</label>
                                        <select id="sidebarRole" name="role" class="profile-sidebar-form-control" required>
                                            <option value="">Select Role...</option>
                                            <option value="QA Engineer">QA Engineer</option>
                                            <option value="Software Developer">Software Developer</option>
                                            <option value="Project Manager">Project Manager</option>
                                            <option value="Team Lead">Team Lead</option>
                                            <option value="DevOps Engineer">DevOps Engineer</option>
                                            <option value="Product Manager">Product Manager</option>
                                            <option value="Other">Other</option>
                                        </select>
                                    </div>
                                    <button type="submit" class="profile-sidebar-btn profile-sidebar-btn-primary">
                                        <i class="fas fa-save"></i> Update Profile
                                    </button>
                                </form>
                            </div>

                            <!-- Password Tab -->
                            <div class="profile-sidebar-tab-content" id="passwordSidebarTabContent">
                                <div class="profile-sidebar-alert profile-sidebar-alert-success" id="passwordSidebarSuccessAlert">
                                    <i class="fas fa-check-circle"></i>
                                    <span id="passwordSidebarSuccessMessage"></span>
                                </div>
                                <div class="profile-sidebar-alert profile-sidebar-alert-danger" id="passwordSidebarErrorAlert">
                                    <i class="fas fa-exclamation-circle"></i>
                                    <span id="passwordSidebarErrorMessage"></span>
                                </div>
                                <form id="passwordSidebarForm">
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarCurrentPassword" class="profile-sidebar-form-label">Current Password</label>
                                        <input type="password" id="sidebarCurrentPassword" name="current_password" class="profile-sidebar-form-control" required>
                                    </div>
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarNewPassword" class="profile-sidebar-form-label">New Password</label>
                                        <input type="password" id="sidebarNewPassword" name="new_password" class="profile-sidebar-form-control" required>
                                    </div>
                                    <div class="profile-sidebar-form-group">
                                        <label for="sidebarConfirmPassword" class="profile-sidebar-form-label">Confirm New Password</label>
                                        <input type="password" id="sidebarConfirmPassword" name="confirm_password" class="profile-sidebar-form-control" required>
                                    </div>
                                    <button type="submit" class="profile-sidebar-btn profile-sidebar-btn-danger">
                                        <i class="fas fa-lock"></i> Change Password
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Add CSS if not already present
            if (!document.getElementById('profileSidebarCSS')) {
                const css = `
                    <style id="profileSidebarCSS">
                        /* Profile Sidebar Styles */
                        .profile-sidebar {
                            position: fixed;
                            top: 0;
                            right: 0;
                            width: 100%;
                            height: 100%;
                            z-index: 10001;
                            display: none;
                            pointer-events: none;
                            transition: all 0.3s ease;
                        }
                        
                        .profile-sidebar.active {
                            pointer-events: all;
                        }
                        
                        .profile-sidebar-overlay {
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            background: rgba(0, 0, 0, 0.5);
                            opacity: 0;
                            transition: opacity 0.3s ease;
                        }
                        
                        .profile-sidebar.active .profile-sidebar-overlay {
                            opacity: 1;
                        }
                        
                        .profile-sidebar-content {
                            position: absolute;
                            top: 0;
                            right: 0;
                            width: 400px;
                            height: 100%;
                            background: white;
                            box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
                            transform: translateX(100%);
                            transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                            display: flex;
                            flex-direction: column;
                            overflow: hidden;
                        }
                        
                        .profile-sidebar.active .profile-sidebar-content {
                            transform: translateX(0);
                        }
                        
                        .profile-sidebar-header {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 2rem;
                            position: relative;
                            flex-shrink: 0;
                        }
                        
                        .profile-sidebar-header h3 {
                            margin: 0 0 0.5rem 0;
                            font-size: 1.4rem;
                            font-weight: 600;
                        }
                        
                        .profile-sidebar-header p {
                            margin: 0;
                            opacity: 0.9;
                            font-size: 0.95rem;
                        }
                        
                        .profile-sidebar-close {
                            position: absolute;
                            top: 1rem;
                            right: 1rem;
                            background: rgba(255, 255, 255, 0.2);
                            color: white;
                            border: none;
                            padding: 0.5rem;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 1rem;
                            width: 2.5rem;
                            height: 2.5rem;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: background 0.2s ease;
                        }
                        
                        .profile-sidebar-close:hover {
                            background: rgba(255, 255, 255, 0.3);
                        }
                        
                        .profile-sidebar-body {
                            flex: 1;
                            overflow-y: auto;
                            padding: 0;
                        }
                        
                        .profile-sidebar-tabs {
                            display: flex;
                            border-bottom: 1px solid #e9ecef;
                            background: #f8f9fa;
                        }
                        
                        .profile-sidebar-tab {
                            flex: 1;
                            padding: 1rem;
                            background: none;
                            border: none;
                            cursor: pointer;
                            font-size: 0.9rem;
                            font-weight: 500;
                            color: #6c757d;
                            border-bottom: 3px solid transparent;
                            transition: all 0.2s ease;
                        }
                        
                        .profile-sidebar-tab.active {
                            color: #667eea;
                            border-bottom-color: #667eea;
                            background: white;
                        }
                        
                        .profile-sidebar-tab:hover {
                            background: rgba(102, 126, 234, 0.1);
                        }
                        
                        .profile-sidebar-tab-content {
                            display: none;
                            padding: 2rem;
                        }
                        
                        .profile-sidebar-tab-content.active {
                            display: block;
                        }
                        
                        .profile-sidebar-form-group {
                            margin-bottom: 1.5rem;
                        }
                        
                        .profile-sidebar-form-label {
                            display: block;
                            margin-bottom: 0.5rem;
                            font-weight: 500;
                            color: #333;
                            font-size: 0.9rem;
                        }
                        
                        .profile-sidebar-form-control {
                            width: 100%;
                            padding: 0.75rem;
                            border: 2px solid #e9ecef;
                            border-radius: 6px;
                            font-size: 0.9rem;
                            transition: border-color 0.2s ease;
                            box-sizing: border-box;
                        }
                        
                        .profile-sidebar-form-control:focus {
                            outline: none;
                            border-color: #667eea;
                            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                        }
                        
                        .profile-sidebar-form-control:disabled {
                            background: #f8f9fa;
                            color: #6c757d;
                        }
                        
                        .profile-sidebar-btn {
                            padding: 0.75rem 1.5rem;
                            border: none;
                            border-radius: 6px;
                            font-size: 0.9rem;
                            cursor: pointer;
                            text-decoration: none;
                            display: inline-flex;
                            align-items: center;
                            gap: 0.5rem;
                            transition: all 0.2s ease;
                            font-weight: 500;
                            width: 100%;
                            justify-content: center;
                        }
                        
                        .profile-sidebar-btn-primary {
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }
                        
                        .profile-sidebar-btn-primary:hover {
                            transform: translateY(-1px);
                            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                        }
                        
                        .profile-sidebar-btn-danger {
                            background: #dc3545;
                            color: white;
                        }
                        
                        .profile-sidebar-btn-danger:hover {
                            background: #c82333;
                            transform: translateY(-1px);
                            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
                        }
                        
                        .profile-sidebar-alert {
                            padding: 0.75rem;
                            border-radius: 6px;
                            margin-bottom: 1rem;
                            display: none;
                            align-items: center;
                            gap: 0.5rem;
                            font-size: 0.9rem;
                        }
                        
                        .profile-sidebar-alert.show {
                            display: flex;
                        }
                        
                        .profile-sidebar-alert-success {
                            background: #d4edda;
                            color: #155724;
                            border: 1px solid #c3e6cb;
                        }
                        
                        .profile-sidebar-alert-danger {
                            background: #f8d7da;
                            color: #721c24;
                            border: 1px solid #f5c6cb;
                        }
                        
                        /* Dark mode support */
                        .dark-mode .profile-sidebar-content {
                            background: #2d3748;
                            color: #e2e8f0;
                        }
                        
                        .dark-mode .profile-sidebar-tabs {
                            background: #1a202c;
                            border-bottom-color: #4a5568;
                        }
                        
                        .dark-mode .profile-sidebar-tab.active {
                            background: #2d3748;
                        }
                        
                        .dark-mode .profile-sidebar-form-control {
                            background: #4a5568;
                            border-color: #718096;
                            color: #e2e8f0;
                        }
                        
                        .dark-mode .profile-sidebar-form-control:disabled {
                            background: #2d3748;
                            color: #a0aec0;
                        }
                        
                        .dark-mode .profile-sidebar-form-label {
                            color: #e2e8f0;
                        }
                        
                        /* Mobile responsive */
                        @media (max-width: 768px) {
                            .profile-sidebar-content {
                                width: 100%;
                            }
                            
                            .profile-sidebar-header {
                                padding: 1.5rem;
                            }
                            
                            .profile-sidebar-tab-content {
                                padding: 1.5rem;
                            }
                            
                            .profile-sidebar-tabs {
                                flex-direction: column;
                            }
                            
                            .profile-sidebar-tab {
                                border-bottom: 1px solid #e9ecef;
                                border-right: none;
                            }
                            
                            .profile-sidebar-tab.active {
                                border-bottom-color: #667eea;
                                border-right-color: transparent;
                            }
                        }
                    </style>
                `;
                
                document.head.insertAdjacentHTML('beforeend', css);
            }

            // Insert sidebar HTML into document
            document.body.insertAdjacentHTML('beforeend', sidebarHTML);
            
            // Add event listeners after DOM insertion
            setTimeout(initializeProfileSidebar, 100);
        }

        // Initialize Profile Sidebar Event Listeners
        function initializeProfileSidebar() {
            // Tab switching
            const profileTabs = document.querySelectorAll('.profile-sidebar-tab');
            profileTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabName = this.dataset.tab;
                    switchProfileSidebarTab(tabName);
                });
            });
            
            // Form submissions
            const profileForm = document.getElementById('profileSidebarForm');
            if (profileForm) {
                profileForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    updateProfileFromSidebar();
                });
            }
            
            const passwordForm = document.getElementById('passwordSidebarForm');
            if (passwordForm) {
                passwordForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    changePasswordFromSidebar();
                });
            }
        }

        // Close Profile Sidebar
        function closeProfileSidebar() {
            const sidebar = document.getElementById('profileSidebar');
            if (sidebar) {
                sidebar.style.display = 'none';
                
                // Remove escape key handler
                document.removeEventListener('keydown', handleSidebarEscape);
                
                // Restore body scrolling
                document.body.style.overflow = '';
                
                // Clear forms and alerts
                clearProfileSidebarForms();
                hideAllProfileSidebarAlerts();
                
                console.log('👤 Profile sidebar closed');
            }
        }

        // Handle Escape Key
        function handleSidebarEscape(e) {
            if (e.key === 'Escape') {
                closeProfileSidebar();
            }
        }

        // Load Profile Data into Sidebar
        async function loadProfileInSidebar() {
            try {
                const response = await fetch('/api/profile');
                const data = await response.json();
                
                if (data.success) {
                    const profile = data.profile;
                    
                    // Update sidebar form fields
                    const sidebarName = document.getElementById('sidebarName');
                    const sidebarEmail = document.getElementById('sidebarEmail');
                    const sidebarCompanyName = document.getElementById('sidebarCompanyName');
                    const sidebarRole = document.getElementById('sidebarRole');
                    
                    if (sidebarName) sidebarName.value = profile.name || '';
                    if (sidebarEmail) sidebarEmail.value = profile.email || '';
                    if (sidebarCompanyName) sidebarCompanyName.value = profile.company_name || '';
                    if (sidebarRole) sidebarRole.value = profile.role || '';
                    
                    console.log('✅ Profile data loaded into sidebar');
                } else {
                    throw new Error(data.error || 'Failed to load profile');
                }
            } catch (error) {
                console.error('❌ Error loading profile into sidebar:', error);
                showProfileSidebarAlert('profileSidebarErrorAlert', 'profileSidebarErrorMessage', 'Failed to load profile data');
            }
        }

        function switchProfileSidebarTab(tabName) {
            // Remove active class from all tabs
            document.querySelectorAll('.profile-sidebar-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Add active class to clicked tab
            const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
            if (activeTab) activeTab.classList.add('active');
            
            // Hide all tab contents
            document.querySelectorAll('.profile-sidebar-tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Show selected tab content
            if (tabName === 'profile') {
                const profileTab = document.getElementById('profileSidebarTabContent');
                if (profileTab) profileTab.classList.add('active');
            } else if (tabName === 'password') {
                const passwordTab = document.getElementById('passwordSidebarTabContent');
                if (passwordTab) passwordTab.classList.add('active');
            }
            
            // Hide alerts when switching tabs
            hideAllProfileSidebarAlerts();
        }

        // Update Profile from Sidebar
        async function updateProfileFromSidebar() {
            try {
                const formData = new FormData(document.getElementById('profileSidebarForm'));
                const profileData = {
                    name: formData.get('name'),
                    company_name: formData.get('company_name'),
                    role: formData.get('role')
                };
                
                const response = await fetch('/api/profile', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(profileData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showProfileSidebarAlert('profileSidebarSuccessAlert', 'profileSidebarSuccessMessage', data.message);
                    
                    // Update the header profile display
                    const profileName = document.getElementById('profileName');
                    const dropdownUserName = document.getElementById('dropdownUserName');
                    
                    if (profileName) {
                        profileName.textContent = profileData.name || 'User';
                    }
                    if (dropdownUserName) {
                        dropdownUserName.textContent = profileData.name || 'User Name';
                    }
                    
                    console.log('✅ Profile updated successfully');
                } else {
                    throw new Error(data.error || 'Failed to update profile');
                }
            } catch (error) {
                console.error('❌ Error updating profile:', error);
                showProfileSidebarAlert('profileSidebarErrorAlert', 'profileSidebarErrorMessage', error.message);
            }
        }

        // Change Password from Sidebar
        async function changePasswordFromSidebar() {
            try {
                const formData = new FormData(document.getElementById('passwordSidebarForm'));
                const passwordData = {
                    current_password: formData.get('current_password'),
                    new_password: formData.get('new_password'),
                    confirm_password: formData.get('confirm_password')
                };
                
                const response = await fetch('/api/profile/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(passwordData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showProfileSidebarAlert('passwordSidebarSuccessAlert', 'passwordSidebarSuccessMessage', data.message);
                    const passwordForm = document.getElementById('passwordSidebarForm'); 
                    if (passwordForm) passwordForm.reset();
                    console.log('✅ Password changed successfully');
                } else {
                    throw new Error(data.error || 'Failed to change password');
                }
            } catch (error) {
                console.error('❌ Error changing password:', error);
                showProfileSidebarAlert('passwordSidebarErrorAlert', 'passwordSidebarErrorMessage', error.message);
            }
        }

        // Profile Alert Functions
        function showProfileSidebarAlert(alertId, messageId, message) {
            hideAllProfileSidebarAlerts();
            const alert = document.getElementById(alertId);
            const messageElement = document.getElementById(messageId);
            
            if (alert && messageElement) {
                messageElement.textContent = message;
                alert.classList.add('show');
                
                setTimeout(() => {
                    alert.classList.remove('show');
                }, 5000);
            }
        }

        function hideAllProfileSidebarAlerts() {
            const alerts = document.querySelectorAll('.profile-sidebar-alert');
            alerts.forEach(alert => {
                alert.classList.remove('show');
            });
        }

        // Clear Profile Forms
        function clearProfileSidebarForms() {
            const passwordForm = document.getElementById('passwordSidebarForm');
            if (passwordForm) {
                passwordForm.reset();
            }
        }

        // ========================================================================================
        // 👤 ENHANCED LOGOUT FUNCTIONALITY
        // ========================================================================================

        // Enhanced Logout Functionality
        async function logoutUser() {
            try {
                // Show custom confirmation modal instead of basic confirm
                const confirmed = await showSignOutConfirmation();
                if (!confirmed) {
                    return;
                }

                // Close profile dropdown and sidebar
                closeProfileDropdown();
                closeProfileSidebar();

                // Show logout process
                if (typeof showNotification === "function") {
                    showNotification("🔄 Signing out...", "info", 2000);
                }

                // Call logout API
                const response = await fetch("/api/auth/logout", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                if (response.ok) {
                    // Clear any local storage/session data
                    sessionStorage.clear();
                    
                    // Clear specific items from localStorage that might contain session data
                    const keysToRemove = [
                        "user_session",
                        "auth_token", 
                        "remember_user",
                        "dashboard_state",
                        "theme_preference",
                        "notifications-disabled"
                    ];
                    keysToRemove.forEach(key => localStorage.removeItem(key));

                    // Show success message
                    if (typeof showNotification === "function") {
                        showNotification("✅ Signed out successfully", "success", 3000);
                    }

                    // Prevent back navigation to dashboard by clearing history
                    if (window.history.replaceState) {
                        window.history.replaceState(null, null, "/login");
                    }
                    
                    // Disable back button navigation
                    window.onpopstate = function () {
                        window.location.replace("/login");
                    };

                    // Redirect to login page after brief delay
                    setTimeout(() => {
                        window.location.replace("/login");
                    }, 1000);

                } else {
                    throw new Error("Sign out failed");
                }

            } catch (error) {
                console.error("Sign out error:", error);
                if (typeof showNotification === "function") {
                    showNotification("❌ Sign out failed. Please try again.", "error", 5000);
                } else {
                    alert("❌ Sign out failed. Please try again.");
                }
            }
        }

        // Custom Sign Out Confirmation Modal
        function showSignOutConfirmation() {
            return new Promise((resolve) => {
                // Remove existing sign out modal if any
                const existingModal = document.getElementById('signOutModal');
                if (existingModal) {
                    existingModal.remove();
                }

                // Create simple sign out confirmation modal
                const modalHTML = `
                    <div id="signOutModal" class="signout-modal" style="display: flex;">
                        <div class="signout-modal-overlay"></div>
                        <div class="signout-modal-content">
                            <div class="signout-modal-body">
                                <h3>Sign Out Confirmation</h3>
                                <p>Are you sure you want to sign out?</p>
                            </div>
                            
                            <div class="signout-modal-footer">
                                <button class="signout-btn signout-btn-cancel" onclick="closeSignOutModal(false)">
                                    Cancel
                                </button>
                                <button class="signout-btn signout-btn-confirm" onclick="closeSignOutModal(true)">
                                    Sign Out
                                </button>
                            </div>
                        </div>
                    </div>
                `;

                // Add simple CSS for sign out modal
                const modalCSS = `
                    <style id="signOutModalCSS">
                        .signout-modal {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            z-index: 10002;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            padding: 2rem;
                        }
                        
                        .signout-modal-overlay {
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            background: rgba(0, 0, 0, 0.5);
                            backdrop-filter: blur(4px);
                        }
                        
                        .signout-modal-content {
                            position: relative;
                            background: white;
                            border-radius: 12px;
                            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                            width: 100%;
                            max-width: 400px;
                            overflow: hidden;
                            animation: modalFadeIn 0.2s ease-out;
                        }
                        
                        @keyframes modalFadeIn {
                            from {
                                opacity: 0;
                                transform: scale(0.95);
                            }
                            to {
                                opacity: 1;
                                transform: scale(1);
                            }
                        }
                        
                        .signout-modal-body {
                            padding: 2rem;
                            text-align: center;
                        }
                        
                        .signout-modal-body h3 {
                            margin: 0 0 1rem 0;
                            font-size: 1.3rem;
                            font-weight: 600;
                            color: #333;
                        }
                        
                        .signout-modal-body p {
                            margin: 0;
                            color: #666;
                            font-size: 1rem;
                            line-height: 1.4;
                        }
                        
                        .signout-modal-footer {
                            padding: 1rem 2rem 2rem 2rem;
                            display: flex;
                            gap: 1rem;
                            justify-content: center;
                        }
                        
                        .signout-btn {
                            padding: 0.75rem 1.5rem;
                            border: none;
                            border-radius: 8px;
                            font-size: 0.95rem;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s ease;
                            min-width: 100px;
                        }
                        
                        .signout-btn-cancel {
                            background: #f8f9fa;
                            color: #333;
                            border: 1px solid #dee2e6;
                        }
                        
                        .signout-btn-cancel:hover {
                            background: #e9ecef;
                            border-color: #adb5bd;
                        }
                        
                        .signout-btn-confirm {
                            background: #dc3545;
                            color: white;
                        }
                        
                        .signout-btn-confirm:hover {
                            background: #c82333;
                        }
                        
                        /* Dark mode support */
                        .dark-mode .signout-modal-content {
                            background: #2d3748;
                            color: #e2e8f0;
                        }
                        
                        .dark-mode .signout-modal-body h3 {
                            color: #e2e8f0;
                        }
                        
                        .dark-mode .signout-modal-body p {
                            color: #a0aec0;
                        }
                        
                        .dark-mode .signout-btn-cancel {
                            background: #4a5568;
                            color: #e2e8f0;
                            border-color: #718096;
                        }
                        
                        .dark-mode .signout-btn-cancel:hover {
                            background: #2d3748;
                            border-color: #4a5568;
                        }
                        
                        /* Mobile responsive */
                        @media (max-width: 768px) {
                            .signout-modal {
                                padding: 1rem;
                            }
                            
                            .signout-modal-content {
                                max-width: 90vw;
                            }
                            
                            .signout-modal-body {
                                padding: 1.5rem;
                            }
                            
                            .signout-modal-footer {
                                padding: 1rem 1.5rem 1.5rem 1.5rem;
                                flex-direction: column;
                            }
                            
                            .signout-btn {
                                width: 100%;
                            }
                        }
                    </style>
                `;

                // Add CSS if not already present
                if (!document.getElementById('signOutModalCSS')) {
                    document.head.insertAdjacentHTML('beforeend', modalCSS);
                }

                // Insert modal HTML
                document.body.insertAdjacentHTML('beforeend', modalHTML);

                // Store resolve function globally so buttons can access it
                window.signOutModalResolve = resolve;

                // Prevent body scrolling
                document.body.style.overflow = 'hidden';

                // Auto-close on escape key
                const handleEscape = (e) => {
                    if (e.key === 'Escape') {
                        closeSignOutModal(false);
                        document.removeEventListener('keydown', handleEscape);
                    }
                };
                document.addEventListener('keydown', handleEscape);
            });
        }

        // Close Sign Out Modal
        function closeSignOutModal(confirmed) {
            const modal = document.getElementById('signOutModal');
            if (modal) {
                // Simple fade out
                modal.style.opacity = '0';
                modal.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    modal.remove();
                    // Restore body scrolling
                    document.body.style.overflow = '';
                    
                    // Call the resolve function
                    if (window.signOutModalResolve) {
                        window.signOutModalResolve(confirmed);
                        delete window.signOutModalResolve;
                    }
                }, 150);
            }
        }

        // Add exit animation CSS
        document.addEventListener('DOMContentLoaded', function() {
            if (!document.getElementById('signOutExitCSS')) {
                const exitCSS = `
                    <style id="signOutExitCSS">
                        .signout-modal {
                            transition: opacity 0.15s ease-out, transform 0.15s ease-out;
                        }
                        
                        .signout-btn:focus {
                            outline: 2px solid rgba(102, 126, 234, 0.3);
                            outline-offset: 2px;
                        }
                        
                        .signout-btn-confirm:focus {
                            outline: 2px solid rgba(220, 53, 69, 0.3);
                        }
                    </style>
                `;
                document.head.insertAdjacentHTML('beforeend', exitCSS);
            }
        });

        // Load user profile information on page load
        async function loadUserProfile() {
            try {
                const response = await fetch("/api/profile");
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        const profile = data.profile;
                        
                        // Update profile button and dropdown
                        const profileName = document.getElementById("profileName");
                        const dropdownUserName = document.getElementById("dropdownUserName");
                        const dropdownUserEmail = document.getElementById("dropdownUserEmail");
                        
                        if (profileName) {
                            profileName.textContent = profile.name || "User";
                        }
                        if (dropdownUserName) {
                            dropdownUserName.textContent = profile.name || "User Name";
                        }
                        if (dropdownUserEmail) {
                            dropdownUserEmail.textContent = profile.email || "user@example.com";
                        }

                        console.log("✅ User profile loaded:", profile.name);
                    }
                }
            } catch (error) {
                console.error("Error loading user profile:", error);
            }
        }

        console.log("👤 User Profile Management System with Modal Support loaded!");

        // ========================================================================================
        // 👤 SIDEBAR COMPATIBILITY FUNCTIONS  
        // ========================================================================================

        // Legacy function names for backward compatibility  
        function closeProfileModal() {
            closeProfileSidebar();
        }

        // Profile Sidebar Alert Functions
        function showProfileSidebarAlert(alertId, messageId, message) {
            hideAllProfileSidebarAlerts();
            const alert = document.getElementById(alertId);
            const messageElement = document.getElementById(messageId);
            
            if (alert && messageElement) {
                messageElement.textContent = message;
                alert.classList.add('show');
                
                setTimeout(() => {
                    alert.classList.remove('show');
                }, 5000);
            }
        }

        function hideAllProfileSidebarAlerts() {
            const alerts = document.querySelectorAll('.profile-sidebar-alert');
            alerts.forEach(alert => {
                alert.classList.remove('show');
            });
        }

        // Clear Profile Sidebar Forms
        function clearProfileSidebarForms() {
            const passwordForm = document.getElementById('passwordSidebarForm');
            if (passwordForm) {
                passwordForm.reset();
            }
        }

        console.log('👤 Profile Sidebar System loaded!');

