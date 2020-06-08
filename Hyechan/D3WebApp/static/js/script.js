function showPopUp(index) {
    if (index != 0) {
        document.getElementById(index).style.display = 'block';
    }
}

function closePopUp(index) {
    if (index != 0) {
        document.getElementById(index).style.display = 'none';
    }
}