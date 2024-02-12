// This code is for creating an accordion functionality with clickable sections
// and rotating arrow icons to expand/collapse content.

// Select all elements with the class "section-item-accordion"
var acc = document.getElementsByClassName("section-item-accordion");

// Initialize a variable to keep track of the current section
var i;

// Loop through all the elements with the class "section-item-accordion"
for (i = 0; i < acc.length; i++) {
  // Initialize a variable to keep track of the rotation angle
  let rotateAngle = 0;

  // Add a click event listener to each section
  acc[i].addEventListener("click", function () {
    // Find the arrow icon within the clicked section
    let arrowIcon = this.querySelector(".arrow-icon");

    // Increase the rotation angle by 180 degrees
    rotateAngle += 180;

    // Rotate the arrow icon
    arrowIcon.setAttribute("style", "transform: rotate(" + rotateAngle + "deg)");

    // Find the panel associated with the clicked section
    var panel = this.nextElementSibling;

    // Toggle the display of the panel (show/hide)
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}
