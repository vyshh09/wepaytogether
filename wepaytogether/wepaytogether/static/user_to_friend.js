const buttonsFriends = document.querySelectorAll('.frienddetail');
buttonsFriends.forEach(button => {
    button.addEventListener('click', function () {
        const user = this.parentNode;
        const uid = user.getAttribute('id');
        const fid = this.getAttribute('id');

        const data = {
            uid: uid,
            fid: fid
        };

        fetch('/friend-dump', {
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
