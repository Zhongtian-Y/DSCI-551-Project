
    document.querySelector('#user').addEventListener('click', function (event) {
        // console.log(document.querySelector('form').querySelector('input[type="radio"]').value)
        console.log('user')
        localStorage.setItem('type', 'user')
    })
    document.querySelector('#administrator').addEventListener('click', function (event) {
        // console.log(document.querySelector('form').querySelector('input[type="radio"]').value)
        console.log('administrator')
        localStorage.setItem('type', 'administrator')

    })
