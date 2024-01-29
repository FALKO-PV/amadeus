let imageSelectors = document.querySelectorAll(".circle-img-selector");
let images = document.querySelectorAll(".card-img");
let cardTitle = document.querySelector(".card-img-title");
let currentIndex = -1;
const titles = ["1. Evaluation erstellen", "2. Schüler:innen QR-Code scannen lassen", "3. Evaluationsergebnisse einsehen"];

function showImage(imageIndex) {
  currentIndex = imageIndex;
  for (let i = 0; i < images.length; i++) {
    if (imageIndex === i) {
      images[i].style.opacity = '1';
      imageSelectors[i].style.backgroundColor = "rgba(255, 255, 255, 0.5)";
      cardTitle.innerHTML = titles[i];
    } else {
      images[i].style.opacity = '0';
      imageSelectors[i].style.backgroundColor = "rgba(255, 255, 255, 0.3)";
    }
  }
}

function rotateImages() {
  currentIndex = (currentIndex + 1) % images.length;
  showImage(currentIndex);
  setTimeout(rotateImages, 3000); // rotate every 5 seconds
}

for (let i = 0; i < imageSelectors.length; i++) {
  imageSelectors[i].addEventListener("click", () => {
    showImage(i);
  });
}

rotateImages(); // start automatic rotation
