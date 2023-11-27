const buttonsGroups = document.querySelectorAll('.groupdetail');
buttonsGroups.forEach(button => {
    button.addEventListener('click', function () {
        const user=this.parentNode;
        const uid=user.getAttribute('id');
        const gid = this.getAttribute('id');

        const data = {
            uid:uid,
            gid: gid
        };

        fetch('/group-dump', {
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
