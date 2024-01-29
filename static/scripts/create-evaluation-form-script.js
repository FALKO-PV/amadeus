// Checkbox Functionality NWFG Study

var checkboxNWFGStudy = document.querySelector(".checkbox-nwfg-study");
var nwfgContainer = document.querySelector(".nwfg-code-container");
var timeSelectionContainer = document.querySelector(
  ".time-selection-container"
);

// function updateSectionsBasedOnNWFGInput() {
//   if (!checkboxNWFGStudy.checked) {
//     nwfgContainer.style.display = "none";
//     timeSelectionContainer.style.display = "flex";
//   } else {
//     nwfgContainer.style.display = "flex";
//     timeSelectionContainer.style.display = "none";
//   }
// }

// updateSectionsBasedOnNWFGInput()

// checkboxNWFGStudy.addEventListener("change", function () {
//   updateSectionsBasedOnNWFGInput();
// });

// Checkbox Functionality 24 Hours

var checkbox24Hours = document.querySelector(".checkbox-24-hours");
var datePicker = document.querySelector(".date-picker");
var nwfgCode = document.querySelector(".nwfg-code-input");

datePicker.style.display = "none";

function updateSectionsBasedOn24HoursInput() {
  if (checkbox24Hours.checked) {
    datePicker.style.display = "none";
  } else {
    datePicker.style.display = "block";
  }
}

updateSectionsBasedOn24HoursInput();

checkbox24Hours.addEventListener("change", function () {
  updateSectionsBasedOn24HoursInput();
});

// Set default values for Time Input

startDateInput = document.querySelector(".evaluation-start-input");
endDateInput = document.querySelector(".evaluation-end-input");

var tzoffset = new Date().getTimezoneOffset() * 60000; //offset in milliseconds

var nowDateObject = new Date(Date.now() - tzoffset)
var nowplus24HoursDateObject = new Date(nowDateObject); 
nowplus24HoursDateObject.setDate(nowplus24HoursDateObject.getDate() + 1)

var timeNowString = nowDateObject.toISOString().slice(0, -1);
var timeIn24HoursString = nowplus24HoursDateObject.toISOString().slice(0, -1);

startDateInput.min = timeNowString.slice(0, -7);
startDateInput.value = timeNowString.slice(0, -7);

endDateInput.min = timeIn24HoursString.slice(0, -7);
endDateInput.value = timeIn24HoursString.slice(0, -7);

console.log(endDateInput.min);
