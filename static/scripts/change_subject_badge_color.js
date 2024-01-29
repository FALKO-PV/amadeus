let subjectBadge = document.querySelector(".subject-badge");
let subject = document.querySelector(".subject").innerHTML;

if (subject === "Evangelische Religion" || subject === "Musik") {
    subjectBadge.style.backgroundColor = "#FFE8DB"
    subjectBadge.style.color = "#DC692A"
} else if (subject === "Deutsch" || subject === "Englisch" || subject === "Latein") {
    subjectBadge.style.backgroundColor = "#FFD9E8"
    subjectBadge.style.color = "#8F1D4A"
} else if (subject === "Mathematik") {
    subjectBadge.style.backgroundColor = "#D5FFEF"
    subjectBadge.style.color = "#449879"
} else if (subject === "Allgemeine Lehrevaluation") {
    subjectBadge.style.backgroundColor = "#F0F0F0"
    subjectBadge.style.color = "#535353"
}