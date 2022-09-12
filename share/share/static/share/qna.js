"use strict"
// Sends a new request to update the to-do list
function getGlobal(item_id) {
    let xhr = new XMLHttpRequest()
    // let response = JSON.parse(xhr.responseText)
    // let item_id = response['item_id']
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePage(xhr, item_id)
    }
    // xhr.open("GET", "/share/get_product?id=" + item_id, true)
    xhr.open("GET", "/share/get_product/" + item_id, true)

    xhr.send()
}

function updatePage(xhr, item_id) {
    if (xhr.status == 200) {
        let response = JSON.parse(xhr.responseText)
        updateQuestion(response, item_id)
        updateAnswer(response, item_id)
        return
    }

    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }
    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function updateQuestion(items, item_id) {
    let questions = items['questions']
    let list = document.getElementById("item_questions_go_here")
    let new_question = document.getElementById("post_question_go_here")
    new_question.innerHTML = '<label >' + 'New Question:' + '</label>' +
        '<input type="text" name="question_text" id="id_question_input_text">' +
        '<button id="id_post_question_button" onclick="addQuestion()">' + 'Submit' + '</button>'

    // Adds each new question item to the list
    for (let i = 0; i < questions.length; i++) {
        let question = questions[i]
        if (!document.body.contains(document.getElementById("id_question_div_" + question.id))) {
            let element = document.createElement("div")
            let time = new Date(question.creation_time).toLocaleDateString() + " " + new Date(question.creation_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
            element.setAttribute('id', 'id_question_div_' + question.id)
            element.innerHTML =
                // '<a class = "profile"' + 'href="/share/profile/' + question.user_id + '"' + 'id="id_post_profile_'+question.id+'">' + question.user + '</a>' +
                '<div>' + question.user + '</div>' +
                '<span id="id_question_text_'+question.id+'">' + sanitize(question.text) + '</span>' +
                '<span class="date" id="id_question_date_time_'+question.id+'">' + time + '</span>' +
                '<div id="question_'+question.id+'_answers_go_here"></div>' +
                '<label >' + 'Answer:' + '</label>' +
                '<input type="text" name="answer_text" id="id_answer_input_text_'+question.id+'">' +
                '<button id="id_answer_button_'+question.id+'" onclick="addAnswer('+question.id+')">' + 'Submit' + '</button>'
            //list.appendChild(element)
            list.prepend(element)
        }
    }
}

function updateAnswer(items) {
    let answers = items['answers']
    let questions = items['questions']

    for (let i = 0; i < questions.length; i++) {
        let question = questions[i]
        for(let j = 0; j < answers.length; j++) {
            let answer = answers[j]
            if (answer.question_id == question.id) {
                let answer_list = document.getElementById("question_" + question.id + "_answers_go_here")
                if (!document.body.contains(document.getElementById("id_answer_div_" + answer.id))) {
                    let time = new Date(answer.creation_time).toLocaleDateString() + " " + new Date(answer.creation_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
                    let element = document.createElement("div")
                    element.setAttribute('id', 'id_answer_div_' + answer.id)
                    element.innerHTML =
                        // '<a class = "profile"' + 'href="/share/profile/' + answer.user_id + '"' + 'id="id_answer_profile_'+answer.id+'">' + answer.user + '</a>' +
                        '<div>' + answer.user + '</div>' +
                        '<span id="id_answer_text_'+answer.id+'">' + sanitize(answer.text) + '</span>' +
                        '<span class="date" id="id_answer_date_time_'+answer.id+'">' + time + '</span>'
                    answer_list.prepend(element)
                }
            }
        }
    }
}

function parseDate(s) {
    let d = new Date(s)
    d.toLocaleDateString()
    d.toLocaleTimeString()
    return d
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

function addAnswer(question_id) {
    let id = 'id_answer_input_text_' + question_id
    let itemTextElement = document.getElementById(id)
    let itemTextValue   = itemTextElement.value
    // Clear input box and old error message (if any)
    itemTextElement.value = ''

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePage(xhr)
    }

    xhr.open("POST", postAnswerURL, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("answer_text="+itemTextValue+"&csrfmiddlewaretoken="+getCSRFToken()+"&question_id="+question_id);
}

function addQuestion() {
    let itemTextElement = document.getElementById('id_question_input_text')
    let itemTextValue   = itemTextElement.value
    // Clear input box and old error message (if any)
    itemTextElement.value = ''

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePage(xhr)
    }

    xhr.open("POST", postQuestionURL, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("question_text="+itemTextValue+"&csrfmiddlewaretoken="+getCSRFToken());
}