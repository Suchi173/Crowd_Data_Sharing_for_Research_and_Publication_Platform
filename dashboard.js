document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar on mobile
    const mobileToggle = document.querySelector('.mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 992 && 
                !sidebar.contains(event.target) && 
                !mobileToggle.contains(event.target) &&
                sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        });
    }

    // File upload area
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#document');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const fileName = e.target.files[0].name;
                const fileSize = formatFileSize(e.target.files[0].size);
                
                document.querySelector('.upload-text').textContent = fileName;
                document.querySelector('.upload-subtext').textContent = `Size: ${fileSize}`;
            }
        });
        
        // Drag and drop for file upload
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadArea.classList.add('highlighted');
        }
        
        function unhighlight() {
            uploadArea.classList.remove('highlighted');
        }
        
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            
            if (files.length > 0) {
                const fileName = files[0].name;
                const fileSize = formatFileSize(files[0].size);
                
                document.querySelector('.upload-text').textContent = fileName;
                document.querySelector('.upload-subtext').textContent = `Size: ${fileSize}`;
            }
        }
    }
    
    // Format file size helper
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Document filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    const documentItems = document.querySelectorAll('.document-item');
    
    if (filterBtns.length > 0 && documentItems.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const filter = this.getAttribute('data-filter');
                
                // Update active button
                filterBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Filter documents
                if (filter === 'all') {
                    documentItems.forEach(item => item.style.display = 'flex');
                } else {
                    documentItems.forEach(item => {
                        const itemType = item.getAttribute('data-type');
                        if (itemType === filter) {
                            item.style.display = 'flex';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }
            });
        });
    }

    // Handle document delete confirmations
    const deleteButtons = document.querySelectorAll('.delete-document');
    
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const documentId = this.getAttribute('data-document-id');
                
                if (confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
                    document.getElementById(this.getAttribute('data-form-id')).submit();
                }
            });
        });
    }

    // Toggle sections in dashboard
    const sectionTogglers = document.querySelectorAll('.section-toggler');
    
    if (sectionTogglers.length > 0) {
        sectionTogglers.forEach(toggler => {
            toggler.addEventListener('click', function() {
                const target = document.querySelector(this.getAttribute('data-target'));
                
                if (target) {
                    target.classList.toggle('collapsed');
                    
                    // Toggle icon
                    const icon = this.querySelector('i');
                    if (icon) {
                        if (icon.classList.contains('fa-chevron-down')) {
                            icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
                        } else {
                            icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
                        }
                    }
                }
            });
        });
    }
});
