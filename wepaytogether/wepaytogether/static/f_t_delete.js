const buttons = document.querySelectorAll('li button .butten2');
buttons.forEach(button => {
    button.addEventListener('click', function () {
        const user = this.parentNode.parentNode;
        const uid=user.getAttribute('id');
        const friend = this.parentNode;
        fid=friend.getAttribute('id');
        const tid = this.getAttribute('id');
        const data = {
            uid: uid,
            fid: fid,
            tid: tid
        };

        fetch('/delete-group-txn-dump', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (response.ok) {
                    console.log('Data sent successfully');
                } else {
                    console.log('Error sending data');
                }
            })
            .catch(error => {
                console.log('Error sending data:', error);
            });
    });
});
