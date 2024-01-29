function read_more() {
  var dots = document.getElementById("dots");
  var moreText = document.getElementById("more");
  var btnText = document.querySelector(".show-more-text");
  var showMoreIcon = document.querySelector(".show-more-icon");

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btnText.innerHTML = "Mehr Anzeigen";
    moreText.style.display = "none";
    showMoreIcon.style.transform = "rotate(0deg)";
  } else {
    dots.style.display = "none";
    btnText.innerHTML = "Weniger Anzeigen";
    moreText.style.display = "inline";
    showMoreIcon.style.transform = "rotate(180deg)";
  }
}
