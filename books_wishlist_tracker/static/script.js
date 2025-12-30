const searchInput = document.getElementById('searchInput');
const dropdown = document.getElementById('dropdown');
const toast = document.getElementById('toast');
const wishlistGrid = document.getElementById('wishlist');
const paginationControls = document.getElementById('pagination');
const prevBtn = document.getElementById('prevPage');
const nextBtn = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');

let debounceTimer;
let currentPage = 1;
const pageSize = 15;

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    fetchWishlist(1);
    checkAdmin();
});

async function fetchWishlist(page = 1) {
    currentPage = page;
    try {
        const res = await fetch(`/api/wishlist?page=${page}&size=${pageSize}`);
        const data = await res.json();
        
        // Smooth Transition: Fade Out
        wishlistGrid.classList.add('fade-out');
        
        setTimeout(() => {
            renderWishlist(data.items);
            renderPagination(data);
            
            // Smooth Transition: Fade In
            wishlistGrid.classList.remove('fade-out');
            wishlistGrid.classList.add('fade-in');
            setTimeout(() => wishlistGrid.classList.remove('fade-in'), 400);
            
            // Scroll to top of wishlist section smoothly
            document.querySelector('.wishlist-section').scrollIntoView({ behavior: 'smooth' });
        }, 400);

    } catch (error) {
        console.error("Error fetching wishlist:", error);
    }
}

function renderWishlist(books) {
    wishlistGrid.innerHTML = '';
    
    if (books.length === 0) {
        wishlistGrid.innerHTML = '<div class="empty-wishlist">Your wishlist is empty. Start adding books!</div>';
        return;
    }

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'book-card';
        // Add click listener
        card.onclick = () => openBookDetails(book);
        
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
        `;
        wishlistGrid.appendChild(card);
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
    if (currentPage > 1) fetchWishlist(currentPage - 1);
});

nextBtn.addEventListener('click', () => {
    fetchWishlist(currentPage + 1);
});

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    clearTimeout(debounceTimer);
    
    if (query.length < 2) {
        dropdown.classList.add('hidden');
        return;
    }

    debounceTimer = setTimeout(() => {
        fetchResults(query);
    }, 300);
});

async function fetchResults(query) {
    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        renderDropdown(data);
    } catch (error) {
        console.error("Error fetching results:", error);
    }
}

function renderDropdown(results) {
    dropdown.innerHTML = '';
    
    if (results.length === 0) {
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
    }
    
    dropdown.classList.remove('hidden');
}

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
            fetchWishlist(); // Refresh wishlist
        } else {
            showToast(data.detail || "Failed to add book", true);
        }
    } catch (error) {
        showToast("Error connecting to server", true);
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
    if (adminPassword) {
        searchSection.classList.remove('hidden');
        adminLoginBtn.classList.add('hidden');
        adminLogoutBtn.classList.remove('hidden');
    } else {
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
            showToast("Logged in as Admin");
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
