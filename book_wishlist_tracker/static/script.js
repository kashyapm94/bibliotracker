const searchInput = document.getElementById('searchInput');
const dropdown = document.getElementById('dropdown');
const toast = document.getElementById('toast');
let debounceTimer;

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
            
            const yearStr = book.year ? `(${book.year})` : '';
            item.innerHTML = `
                <span class="item-title">${book.title} ${yearStr}</span>
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
            original_year: book.year,
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
