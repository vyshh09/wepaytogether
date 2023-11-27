const buttons = document.querySelectorAll('.add_button');
buttons.forEach(button => {
    button.addEventListener('click', function () {
        const user = this.parentNode.parentNode.parentNode;
        const uid = user.getAttribute('id');
        const group = this.parentNode.parentNode;
        const gid = group.getAttribute('id');
        const friend_id = this.getAttribute('id');

        const data = {
            uid: uid,
            gid: gid,
            friend_id: friend_id
        };

        fetch('/add_member_to_group', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.text())
            .then(html => {
                // insert the rendered HTML into a DOM element
                document.open();
                document.write(html);
                document.close();
            })
            .catch(error => {
                console.log('Error sending data:', error);
            });
    });
});
