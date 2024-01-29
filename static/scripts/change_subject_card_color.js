function change_subject_card_color() {
    selectedId = document.getElementById("select-subject").value;
    subjectCard = document.querySelector(".subject-card");
    subjectCardIcon = document.querySelector(".subject-card-icon");

    subjectCardIcon.setAttribute("src", "/static/icons/subjects/"+selectedId.replace(" ","")+".svg")

    green = ['#449879','#89facf', '#449879']
    red = ['#692545','#d07c9f','#d8b1e0']
    orange = ['#C16431','#eca57f','#e6c4b2']
    gray = ['#7A7A7A','#DBDBDB','#333333']

    let selectedColorCodes;

    if (selectedId === "Evangelische Religion" || selectedId === "Musik") {
        selectedColorCodes = orange
    } else if (selectedId === "Deutsch" || selectedId === "Englisch" || selectedId === "Latein") {
        selectedColorCodes = red
    } else if (selectedId === "Mathematik") {
        selectedColorCodes = green
    } else if (selectedId === "Allgemeine Lehrevaluation") {
        selectedColorCodes = gray
    }
    
    imageString = 'radial-gradient(at top left, '+selectedColorCodes[0]+', transparent), radial-gradient(at top right, '+selectedColorCodes[1]+', transparent), radial-gradient(at top left, '+selectedColorCodes[2]+', transparent)';
    subjectCard.style.backgroundImage = imageString;
}
