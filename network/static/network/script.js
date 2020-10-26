
let loggedUsername = document.querySelector("#scripts").dataset.user;

function edit(postId) {
    let contentElement = document.querySelector(`#content-${postId}`);
    //get the current content
    let content = contentElement.innerHTML;
    //get the edit button and hide it
    let editBtn = document.querySelector(`#edit-${postId}`);
    editBtn.style.display = "none";
    //make a form show up
    contentElement.innerHTML =`
        <form id="edit-form">
            <textarea type="text" id="edit-content" class="form-control" required>${content}</textarea>
            <button class="btn btn-primary" type="submit">Edit</button>
        </form>
    `;
    //change the content
    document.querySelector('#edit-form').onsubmit = () => {
        fetch('/edit', {
            method: 'PUT',
            body: JSON.stringify({
                postId: postId,
                content: document.querySelector('#edit-content').value
            })
        })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                //hide the form/go back to just showing the content
                contentElement.innerHTML = document.querySelector('#edit-content').value;
                //show the hide button again
                editBtn.style.display = "block";
            });

        return false;
    }
}

function like(postId) {
    fetch('/like', {
        method: 'PUT',
        body: JSON.stringify({
            postId: postId
        })
    })
        .then(response => response.json())
        .then(result => {
            let heart = document.querySelector(`#heart-${postId}`);
            let like = parseInt(document.querySelector(`#counter-${postId}`).innerHTML);
            //change the heart to filled or empty and update likes count
            if (result["liked"]) {
                heart.innerHTML = "<span style = 'font-size: 200%; color: red;'>&#9829;</span>";
                like++;
                document.querySelector(`#counter-${postId}`).innerHTML = like;
            } else {
                heart.innerHTML = "<span style = 'font-size: 200%; color: red;'>&#9825;</span>";
                like--;
                document.querySelector(`#counter-${postId}`).innerHTML = like;
            }
        });
}
