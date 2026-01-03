const searchInput = document.getElementById('searchInput');
const dropdown = document.getElementById('dropdown');
const toast = document.getElementById('toast');
const bookGrid = document.getElementById('wishlist');
const paginationControls = document.getElementById('pagination');
const prevBtn = document.getElementById('prevPage');
const nextBtn = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');

// Search Pagination State
let debounceTimer;
let currentSearchPage = 1;
let isSearching = false;
let hasMoreResults = true;
let currentQuery = '';

let currentPage = 1;
const pageSize = 9;
let currentBooksData = [];

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    fetchBooks(1);
    checkAdmin();
});

async function fetchBooks(page = 1) {
    currentPage = page;
    try {
        const res = await fetch(`/api/toread?page=${page}&size=${pageSize}`);
        const data = await res.json();
        
        currentBooksData = data.items;
        
        // Smooth Transition: Fade Out
        bookGrid.classList.add('fade-out');
        
        setTimeout(() => {
            renderBooks(data.items);
            renderPagination(data);
            
            // Smooth Transition: Fade In
            bookGrid.classList.remove('fade-out');
            bookGrid.classList.add('fade-in');
            setTimeout(() => bookGrid.classList.remove('fade-in'), 400);
            
            // Scroll to top of list section smoothly
            document.querySelector('.toread-section').scrollIntoView({ behavior: 'smooth' });
        }, 400);

    } catch (error) {
        console.error("Error fetching books:", error);
    }
}

function renderBooks(books) {
    bookGrid.innerHTML = '';
    
    if (books.length === 0) {
        bookGrid.innerHTML = '<div class="empty-list">Your to-read list is empty. Start adding books!</div>';
        return;
    }

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'book-card';
        // Add click listener to open details (excluding clicks on the toggle)
        card.onclick = (e) => {
            if (!e.target.closest('.owned-toggle')) {
                openBookDetails(book);
            }
        };

        // Determine Owned UI
        let ownedUI = '';
        if (adminPassword) {
            // Admin Toggle
            ownedUI = `
                <div class="owned-toggle" onclick="toggleOwnership(${book.id}, ${book.is_owned}, this)">
                    <span class="toggle-icon">${book.is_owned ? '✅' : '⬜'}</span>
                    <span class="toggle-text">${book.is_owned ? 'Owned' : 'Mark as Owned'}</span>
                </div>
            `;
        } else {
            // Guest Badge (Static)
            ownedUI = book.is_owned ? '<span class="owned-tag">✅ Owned</span>' : '';
        }
        
        card.innerHTML = `
            <h3 class="book-title">${book.title}</h3>
            <p class="book-author">by ${book.author}</p>
            <div class="book-meta">
                <span class="location">📍 ${book.region}</span>
                <span class="category-tag">${book.is_fiction}</span>
            </div>
            <div class="book-tags">
                ${book.subjects.map(s => `<span class="tag">${s}</span>`).join('')}
            </div>
            ${ownedUI}
        `;
        bookGrid.appendChild(card);
    });
}

function renderPagination(data) {
    const { page, total_pages, total } = data;
    
    if (total === 0) {
        paginationControls.classList.add('hidden');
        return;
    }
    
    paginationControls.classList.remove('hidden');
    pageInfo.textContent = `Page ${page} of ${total_pages}`;
    
    prevBtn.disabled = page === 1;
    nextBtn.disabled = page === total_pages;
}

prevBtn.addEventListener('click', () => {
    if (currentPage > 1) fetchBooks(currentPage - 1);
});

nextBtn.addEventListener('click', () => {
    fetchBooks(currentPage + 1);
});

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    clearTimeout(debounceTimer);
    
    if (query.length < 2) {
        dropdown.classList.add('hidden');
        return;
    }

    debounceTimer = setTimeout(() => {
        currentQuery = query;
        currentSearchPage = 1;
        hasMoreResults = true;
        fetchResults(query, 1);
    }, 300);
});

async function fetchResults(query, page = 1) {
    if (isSearching) return;
    isSearching = true;

    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&page=${page}`);
        const data = await res.json();
        
        if (data.length === 0) {
            hasMoreResults = false;
        }
        
        renderDropdown(data, page);
    } catch (error) {
        console.error("Error fetching results:", error);
    } finally {
        isSearching = false;
    }
}

function renderDropdown(results, page) {
    if (page === 1) {
        dropdown.innerHTML = '';
    }
    
    if (results.length === 0 && page === 1) {
        const empty = document.createElement('div');
        empty.className = 'dropdown-item';
        empty.innerHTML = '<span class="item-meta">No results found</span>';
        dropdown.appendChild(empty);
    } else {
        results.forEach(book => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            
            item.innerHTML = `
                <span class="item-title">${book.title}</span>
                <span class="item-meta">${book.authors}</span>
            `;
            
            item.addEventListener('click', () => selectBook(book));
            dropdown.appendChild(item);
        });
        
        // Setup Infinite Scroll on the dropdown container provided it has content
        if (page === 1 && results.length > 0) {
             // Ensure we don't attach multiple listeners if called multiple times (though page 1 implies fresh start)
             // But actually it's cleaner to attach once globally or ensure we don't duplicate.
             // Since we clear innerHTML, we might lose the scroll position or state, but the listener is on the container 'dropdown'
             // which is NOT cleared (it's a div in HTML). So we should attach the listener ONCE outside or check it here.
             // Better to attach it once in global scope, but we need closure over current variables.
             // Actually, Global variables are used, so global listener is fine.
        }
    }
    
    if (page === 1) {
        dropdown.classList.remove('hidden');
        dropdown.scrollTop = 0;
    }
}

// Dropdown Infinite Scroll
dropdown.addEventListener('scroll', () => {
    if (dropdown.scrollTop + dropdown.clientHeight >= dropdown.scrollHeight - 50) {
        if (hasMoreResults && !isSearching) {
            currentSearchPage++;
            fetchResults(currentQuery, currentSearchPage);
        }
    }
});

async function selectBook(book) {
    // UI Feedback
    searchInput.value = book.title;
    dropdown.classList.add('hidden');
    
    // Optimistic UI updates could go here
    
    try {
        const payload = {
            book_key: book.key,
            title: book.title,
            authors_str: book.authors,
            subjects: book.subjects || []
        };

        const res = await fetch('/api/add', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'x-admin-password': adminPassword || ''
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        
        if (res.ok) {
            showToast(data.message);
            searchInput.value = ''; // clear only on success
            fetchBooks(); // Refresh list
        } else {
            showToast(data.detail || "Failed to add book", true);
        }
    } catch (error) {
        showToast("Error connecting to server", true);
    }
}

async function toggleOwnership(bookId, currentStatus, element) {
    if (!adminPassword) return; // double check

    const newStatus = !currentStatus;
    
    // Optimistic UI update could be done, but let's wait for server to be safe or simple toggle
    // Let's optimistic update the icon
    const icon = element.querySelector('.toggle-icon');
    const text = element.querySelector('.toggle-text');
    icon.textContent = '⏳'; 

    try {
        const res = await fetch(`/api/books/${bookId}`, {
            method: 'PATCH',
            headers: { 
                'Content-Type': 'application/json',
                'x-admin-password': adminPassword 
            },
            body: JSON.stringify({ is_owned: newStatus })
        });
        
        if (res.ok) {
            // Success
            showToast("Updated ownership status");
            // Refresh interactions
            fetchBooks(currentPage); 
        } else {
            showToast("Failed to update status", true);
            // Revert UI implicitly by fetching list or manually resetting
            fetchBooks(currentPage);
        }
    } catch (error) {
        console.error(error);
        showToast("Error updating status", true);
        fetchBooks(currentPage);
    }
}

function showToast(message, isError = false) {
    toast.textContent = message;
    toast.className = `toast ${isError ? 'error' : ''}`; // remove hidden
    setTimeout(() => {
        toast.className = 'toast hidden';
    }, 3000);
}

// Modal Logic
const detailsModal = document.getElementById('detailsModal');
const closeModalBtn = document.getElementById('closeModal');

function openBookDetails(book) {
    document.getElementById('modalTitle').textContent = book.title;
    document.getElementById('modalAuthor').textContent = `by ${book.author}`;
    document.getElementById('modalDescription').textContent = book.description || 'No description available.';
    document.getElementById('modalRegion').textContent = `📍 ${book.region}`;
    document.getElementById('modalCategory').textContent = book.is_fiction;
    
    // Add Owned Status to Modal (Dynamically created or added to HTML first)
    // For now, let's append it to the meta row if not exists, or just append to description for simplicity
    // Or better: update the modal HTML in index.html to have a slot for it.
    // Let's assume we can add it to the meta row dynamically here.
    let ownedSpan = document.getElementById('modalOwned');
    if (!ownedSpan) {
        ownedSpan = document.createElement('span');
        ownedSpan.id = 'modalOwned';
        ownedSpan.className = 'category-tag owned-tag-modal';
        document.querySelector('.modal-meta-row').appendChild(ownedSpan);
    }
    
    if (book.is_owned) {
        ownedSpan.textContent = "✅ Owned";
        ownedSpan.style.display = 'inline-block';
        ownedSpan.style.background = 'var(--accent)';
        ownedSpan.style.color = 'white';
    } else {
        ownedSpan.style.display = 'none';
    }
    
    const tagsContainer = document.getElementById('modalTags');
    tagsContainer.innerHTML = book.subjects.map(s => `<span class="tag">${s}</span>`).join('');
    
    // Set Amazon Link
    const amazonLink = document.getElementById('amazonLink');
    const searchTerm = `${book.title} ${book.author}`;
    amazonLink.href = `https://www.amazon.de/s?k=${encodeURIComponent(searchTerm)}`;
    
    detailsModal.classList.remove('hidden');
}

closeModalBtn.addEventListener('click', () => {
    detailsModal.classList.add('hidden');
});

// Close modal if clicked outside content
detailsModal.addEventListener('click', (e) => {
    if (e.target === detailsModal) {
        detailsModal.classList.add('hidden');
    }
});

// Admin Auth Logic
const searchSection = document.getElementById('searchSection');
const adminLoginBtn = document.getElementById('adminLogin');
const adminLogoutBtn = document.getElementById('adminLogout');

const loginModal = document.getElementById('loginModal');
const closeLoginModal = document.getElementById('closeLoginModal');
const adminPasswordInput = document.getElementById('adminPasswordInput');
const submitAdminLogin = document.getElementById('submitAdminLogin');
const loginError = document.getElementById('loginError');

let adminPassword = null;

function checkAdmin() {
    // Rerender list to update card toggles if books are loaded
    if (currentBooksData && currentBooksData.length > 0) {
         renderBooks(currentBooksData); 
    }

    if (adminPassword) {
        // Admin Mode
        searchSection.classList.remove('hidden');
        adminLoginBtn.classList.add('hidden');
        adminLogoutBtn.classList.remove('hidden');
    } else {
        // Guest Mode
        searchSection.classList.add('hidden');
        adminLoginBtn.classList.remove('hidden');
        adminLogoutBtn.classList.add('hidden');
    }
}

// Show Login Modal
adminLoginBtn.addEventListener('click', () => {
    loginModal.classList.remove('hidden');
    adminPasswordInput.value = '';
    loginError.classList.add('hidden'); // Clear previous errors
    setTimeout(() => adminPasswordInput.focus(), 100);
});

// Close Login Modal
closeLoginModal.addEventListener('click', () => {
    loginModal.classList.add('hidden');
});

// Hide error on input
adminPasswordInput.addEventListener('input', () => {
    loginError.classList.add('hidden');
});

// Submit Login
async function performLogin() {
    const pwd = adminPasswordInput.value;
    if (!pwd) return;

    try {
        const res = await fetch('/api/verify-admin', {
            method: 'POST',
            headers: { 'x-admin-password': pwd }
        });

        if (res.ok) {
            adminPassword = pwd;
            checkAdmin();
            showToast("Logged in");
            loginModal.classList.add('hidden');
        } else {
            // Show inline error instead of toast
            loginError.classList.remove('hidden');
            adminPasswordInput.value = '';
            adminPasswordInput.focus();
        }
    } catch (error) {
        showToast("Error verifying password", true);
    }
}

submitAdminLogin.addEventListener('click', performLogin);

adminPasswordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performLogin();
    }
});

adminLogoutBtn.addEventListener('click', () => {
    adminPassword = null;
    checkAdmin();
    showToast("Logged Out");
});

// Close dropdown if clicked outside
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});
