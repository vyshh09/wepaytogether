const buttons = document.querySelectorAll('.add_button');
buttons.forEach(button => {
    button.addEventListener('click', function () {
        const user = this.parentNode.parentNode;
        const uid=user.getAttribute('id');
        const candidate_id = this.getAttribute('id');

        const data = {
            uid:uid,
            candidate_id: candidate_id
        };
        
        fetch('/addfriend', {
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
