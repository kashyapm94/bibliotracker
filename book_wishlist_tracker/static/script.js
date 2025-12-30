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
const pageSize = 10;

// Initial load
document.addEventListener('DOMContentLoaded', () => fetchWishlist(1));

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
        
        card.innerHTML = `
            <h3 class="book-title">${book.title}</h3>
            <p class="book-author">by ${book.author}</p>
            <p class="book-description">${book.description || 'No description available.'}</p>
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
            headers: { 'Content-Type': 'application/json' },
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

// Close dropdown if clicked outside
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});
