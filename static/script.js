function saveAll() {
    let inputs = document.querySelectorAll("input[data-id]");
    let grades = [];

    inputs.forEach(input => {
        grades.push({
            id: input.getAttribute("data-id"),
            grade: input.value
        });
    });

    fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(grades)
    })
    .then(res => res.text())
    .then(msg => alert("Calificaciones guardadas correctamente."));
}
