
    document.querySelector('#user').addEventListener('click', function (event) {
        console.log('user')
        localStorage.setItem('type', 'user')

        fetch('/receive_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'type': 'user'})
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error));
    })
    document.querySelector('#administrator').addEventListener('click', function (event) {
        console.log('administrator')
        localStorage.setItem('type', 'administrator')

        fetch('/receive_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'type': 'administrator'})
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error));
    })
