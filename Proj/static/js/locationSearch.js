// used on the locations page. Updates location search results
function searchAndUpdate(){
    const searchBar = document.getElementById("search-input");
    const query = searchBar.value;
    const resultsContainer = document.getElementById("results-container");
    
    // Construct the URL to your search endpoint
    const url = `/search_locations?q=${encodeURIComponent(query)}`;
    
    // Use the Fetch API to make an asynchronous request
    fetch(url)
        .then(response => {
            // Check if the request was successful
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // The server returns HTML text, so we parse it as text
            return response.text(); 
        })
        .then(html => {
            // Update the content of the results container with the new HTML
            resultsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            resultsContainer.innerHTML = '<p class="text-danger mt-4">Could not load results. Please try again.</p>';
        });
}