function showPopUp(id) {
  var elName = "popup".concat(id)
  document.getElementById(elName).style.display = 'block';
}
function closePopUp(id) {
  var elName = "popup".concat(id)
  document.getElementById(elName).style.display = 'none';
}
