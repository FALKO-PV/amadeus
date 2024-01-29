var acc = document.getElementsByClassName("section-item-accordion");
var i;

for (i = 0; i < acc.length; i++) {
  let rotateAngle = 0;
  acc[i].addEventListener("click", function () {
    let arrowIcon = this.querySelector(".arrow-icon");
    rotateAngle += 180;
    arrowIcon.setAttribute("style", "transform: rotate(" + rotateAngle + "deg)");
    console.log(arrowIcon);
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}
