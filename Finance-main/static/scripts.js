const submitButton = document.querySelector('#submitButton');
    document.querySelector('#submitEntry').onkeyup = function () {
        if (document.querySelector('#submitEntry').value === '') {
            submitButton.disabled = true;
        } else {
            console.log('test');
            submitButton.disabled = false;
        }
    };