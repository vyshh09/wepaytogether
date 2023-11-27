const buttonsTransaction = document.querySelectorAll('.butten1');
buttonsTransaction.forEach(button => {
    button.addEventListener('click', function () {
        const user = this.parentNode.parentNode.parentNode;
        const uid = user.getAttribute('id');
        const group = this.parentNode.parentNode;
        gid = group.getAttribute('id');
        const group_txn_id = this.getAttribute('id');
        const data = {
            uid: uid,
            gid: gid,
            group_txn_id: group_txn_id
        };

        fetch('/group-txn-page-dump', {
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
