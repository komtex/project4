let targetUsername = document.querySelector("#user").dataset.target;

document.addEventListener('DOMContentLoaded', function () {
    if (!loggedUsername || loggedUsername === targetUsername) {
        // add event listener to any "other"user
        return;
    }

    document.querySelector("#follow-btn").addEventListener("click", () => {
        fetch(`/follow/${targetUsername}`, {
            method: 'PUT'
        })
            .then(response => response.json())
            .then(result => {
                console.log(result);

                location.reload(true);
            });
    })
});
