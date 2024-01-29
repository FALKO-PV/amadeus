function createStatsCard(statsData, dimSubject) {
    const subject = dimSubject;
    const barColor = '#FF4545';
    const likertScale = {
        5: 'Trifft zu (5).',
        4: 'Trifft eher zu (4).',
        3: 'Teils, teils (3).',
        2: 'Trifft eher nicht zu (2).',
        1: 'Trifft nicht zu (1).',
    }

    const dimDescription = {"1": {"title": "1. Auswahl und Thematisierung von Inhalten und Fachmethoden", "text": "Lerngegenstände und Fachmethoden sind für den Unterricht von besonderer Bedeutung. Deshalb werden hier Aspekte wie Altersangemessenheit, Lebensweltbezug, Relevanz, Strukturierung und didaktische Aufbereitung beachtet."},
            "2": {"title": "2. Kognitive Aktivierung", "text": "Der Anregungsgehalt des Unterrichts zu selbstständigem vertieftem Nachdenken, zu einer elaborierten Auseinandersetzung mit dem Lerngegenstand und zu metakognitiven Prozessen bei Schüler:innen sind Facetten kognitiver Aktivierung, die hier unter anderem evaluiert werden."},
            "3": {"title": "3. Unterstützung des Übens", "text": "Wiederholung und Variationsreichtum sind nur zwei Aspekte des Übens, die diese Dimension umfasst. Eine weitere Facette stellt der konstruktive Umgang mit hierbei auftretenden Fehlern dar."},
            "4": {"title": "4. Formatives Assessment", "text": "Eine klare Ausrichtung der Beurteilung auf die zu erlernenden Kompetenzen, eine regelmäßige Überprüfung des Verständnisses der Schüler:innen und ein differenziertes Feedback an die Schüler:innen  sind einige Aspekte, die zu einem lernförderlichen formativen Assessment gehören."},
            "5": {"title": "5. Unterstützung des Lernens aller Schüler:innen", "text": "Die aktive Beteiligung und Mitwirkung aller Schüler:innen unter Berücksichtigung ihrer individuellen Lernvoraussetzungen und -bedürfnisse ist ein weiteres Kriterium qualitätsvollen Unterrichts. Hierzu zählen unter anderem ein produktives Lernumfeld ebenso wie Ansätze innerer und äußerer Differenzierung."},
            "6_1": {"title": "6a. Sozio-emotionale Unterstützung: Beziehung Lehrkraft - Schüler:innen", "text": "Ein gutes Klassenklima, das durch wertschätzende Aufmerksamkeit, gegenseitigen Respekt und einen freundlichen Umgangston geprägt ist, gilt als wesentliche Determinante von Unterrichtsqualität. Hier sehen Sie die Bewertung der Beziehung der Lehrkraft zu den Schüler:innen."},
            "6_2": {"title": "6b. Sozio-emotionale Unterstützung: Beziehung Schüler:innen untereinander", "text": "Die andere wichtige Komponente für ein gutes Klassenklima ist die Beziehung der Schüler:innen untereinander."},
            "7_1": {"title": "7a. Klassenführung: Verhaltensmanagement", "text": "Unter dem Aspekt der Klassenführung werden im Allgemeinen zwei Gütekriterien gefasst: Verhaltens- und Zeitmanagement. Die Bewertung des Verhaltensmanagements berücksichtigt unter anderem den Umgang mit auftretenden Unterrichtsstörungen, die Prävention von Unterbrechungen des Unterrichts und auch die Kommunikation von Verhaltensegeln."},
            "7_2": {"title": "7b. Klassenführung: Zeitmanagement", "text": "In das Zeitmanagement gehen Prozessmerkmale wie Unterrichtstempo und -organisation ein."},
            "8": {"title": "8. Ästhetisch-emotionales Lernen", "text": "Unterricht zielt nicht nur auf das Erreichen kognitiver Lernziele, sondern ebenso auf ästhetisch-emotionales Lernen ab. Aspekte wie die Anregung ästhetischer Wahrnehmungsprozesse, die Schaffung von Freiräumen für emotionale Erfahrungen und eine kritische Reflexion über Gefahren ästhetisch-emotionaler Beeinflussung werden hier abgebildet."},
            "9": {"title": "9. Fachspezifische Qualitätsmerkmale", "text": "Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale.",
                "Deutsch": "In Deutsch sind dies beispielsweise Rückmeldung hinsichtlich Tiefenstrukturen, Berücksichtigung eines erweiterten Textbegriffs oder vielfältige Produktionsgelegenheiten.",
                "Englisch": "In Englisch sind dies beispielsweise Kommunikation der Lehrkraft in sprachlich und fachlich korrektem und/aber dem Lernstand angepasstem Englisch, Schaffung und Nutzung interdisziplinärer Bezüge zwischen (schulischen) Fremdsprachen als Lerngelegenheiten oder Schaffung hoher Sprechanteile.",
                "Evangelische Religion": "In Evangelischer Religion sind dies beispielsweise Authentizität, Dialogorientierung, Interreligiöses Lernen, Subjektorientierung oder Seelsorge.",
                "Mathematik": "In Mathematik sind dies beispielsweise Gendersensibler Unterricht, Modellierung, (Historische) Kontextualisierung oder Sinnvolle Nutzung (digitaler) Medien.",
                "Latein": "In Latein sind dies beispielsweise Verwendung der Sprache als Reflexionsgegenstand, Aktiver Gebrauch der Sprache als Kommunikationsmedium, Auswahl und Berücksichtigung bedeutsamer Rezeptionsdokumente oder Kritische Reflexion über die gegenwärtige (und zukünftige) kulturelle wie auch gesellschaftliche Relevanz des Fachs.",
                "Musik": "In Musik sind dies beispielsweise Bewahrung der Würde des Einzelnen und Umgang mit Fehlern, Raum- und Materialmanagement oder kognitiv-motorische Aktivierung."}};

    // a function for dynamically creating the bars
    function buildBars(dim) {
        let likerts = statsData[dim]['counts'][0].slice().reverse() // likert 5 on top!
        let counts = statsData[dim]['counts'][1].slice().reverse()

        let maxCount = Math.max(...counts);
        let sumCounts = counts.reduce((acc, cur) => {
            return acc + cur;
        }, 0);

        let head = document.querySelector('#evaluation-result-title');
        let title = document.createElement('p');
        title.innerHTML = dimDescription[dim].title;
        title.className = 'evaluation-result-title-text'

        let headText = document.createElement('p');
        headText.innerHTML = dimDescription[dim].text;
        if (parseInt(dim) === 9) {
            headText.innerHTML += "\n ";
            headText.innerHTML += dimDescription[dim][subject];
        }
        headText.className = 'evaluation-result-description-text';

        head.appendChild(title);
        head.appendChild(headText);

        let t = document.querySelector('#bar-example');

        // create tbody and td from statsData
        let tbody = document.createElement('tbody');

        // loop through statsData.dim.counts and create the rows for every likert answer
        for (let i = 0; i < likerts.length; i++) {
            let likert = likerts[i];

            let tr = document.createElement('tr');
            let th = document.createElement('th');

            th.textContent = likertScale[likert];

            // create stats for bar
            let count = counts[i];

            let td = document.createElement('td');
            if (count === 0) {
                td.style.cssText = `--size: 0.04; --color: ${barColor}; margin-left: 10px;`;
            } else {
                td.style.cssText = `--size: calc(${count}/${maxCount}); --color: ${barColor}; margin-left: 10px;`;
            }

            let span = document.createElement('span');
            span.className = 'bar-label';
            if (sumCounts === 0) {
                span.textContent = "0"
            } else {
                span.textContent = ((count / sumCounts) * 100).toFixed(0).replace(".", ",");
            }

            td.appendChild(span);
            tr.appendChild(th);
            tr.appendChild(td);
            tbody.appendChild(tr);
        }
        t.appendChild(tbody);
    }

    // initially build title, text and statistical bars for dimension 1
    buildBars(1);

    // initially fill the descriptive-statistics card with values for mean, std and median
    let descriptiveStatsCard = document.querySelector('.descriptive-statistics')

    let meanDiv = descriptiveStatsCard.firstElementChild
    let meanP = document.createElement('p')
    meanP.className = 'descriptive-statistics-value'
    meanP.textContent = statsData[1]['mean']
    meanDiv.appendChild(meanP)

    let stdDiv = meanDiv.nextElementSibling
    let stdP = document.createElement('p')
    stdP.className = 'descriptive-statistics-value'
    stdP.textContent = statsData[1]['std']
    stdDiv.appendChild(stdP)

    let medianDiv = stdDiv.nextElementSibling
    let medianP = document.createElement('p')
    medianP.className = 'descriptive-statistics-value'
    medianP.textContent = statsData[1]['median']
    medianDiv.appendChild(medianP)

    // add EventListener for user change of selection (dimension)
    const dimSelection = document.querySelector('#dim-selection')
    dimSelection.addEventListener('change', changeStatsForDim)

    // function to change the shown stats for selected dimension by user
    function changeStatsForDim() {
        let dim = dimSelection.value

        // remove the old data
        let oldTable = document.querySelector('#bar-example')
        let oldDescription = document.querySelector('#evaluation-result-title')
        oldTable.firstElementChild.remove()
        oldDescription.firstElementChild.nextElementSibling.remove()
        oldDescription.firstElementChild.remove()

        // create new title, text, tbody and td from statsData
        buildBars(dim)

        // change mean, std and median
        let descriptiveStatsCard = document.querySelector('.descriptive-statistics')

        let meanDiv = descriptiveStatsCard.firstElementChild
        meanDiv.lastElementChild.textContent = statsData[dim]['mean']

        let stdDiv = meanDiv.nextElementSibling
        stdDiv.lastElementChild.textContent = statsData[dim]['std']

        let medianDiv = stdDiv.nextElementSibling
        medianDiv.lastElementChild.textContent = statsData[dim]['median']
    }
}
