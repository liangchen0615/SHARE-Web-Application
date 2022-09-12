var Global=true
function loadPosts() {
    let xhr = new XMLHttpRequest()
    Global=true
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePage(xhr)
    }


    xhr.open("GET", "/socialnetwork/get-items", true)
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status == 200) {

        let response = JSON.parse(xhr.responseText)
        updateList(response)
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



function updateList(items) {
    // Removes the old to-do list items
    let list = document.getElementById("item-grid")

    // Adds each new todo-list item to the list
    for (let i = 0; i < items['post'].length; i++) {

        let item = items['post'][i]
        if(! document.body.contains(document.getElementById("id_post_div_"+item.id))){
        let element = document.createElement("div")
        element.setAttribute('id',"id_post_div_"+item.id)
        element.innerHTML =
      '  <a class="post_profile"'+ 'href="/socialnetwork/otherProfile/'+item.user_id+'"'+
        'id="id_post_profile_'+item.id+'">'
       + item.user +
        '</a>'+
        '<span id="id_post_text_'+item.id+'">'+
        sanitize(item.text)+
        '</span>'+
        '<span class="post_time" id="id_post_date_time_'+item.id+'">'+
        item.date_time+
        '</span>'
        + '<div id = "post-'+item.id+'-comments-go-here"' +'class="comment"></div>"'

        // Adds the todo-list item to the HTML list

        let commentbox = document.createElement("div")
        commentbox.setAttribute('class',"comment_button")
        commentbox.innerHTML =
        '<br>'+
        '<lable>Comment:</lable>'+
        '<input type="text" id="id_comment_input_text_'+item.id+'">'+
        '<button type="submit" id="id_comment_button_'+item.id+'"'+'onclick="addComment('+item.id+')"'+'>Submit</button>'+
        '<br>'
        element.appendChild(commentbox)
        list.prepend(element)
        }
    }

     for (let i = 0; i < items['comment'].length; i++) {
        let item = items['comment'][i]
        if(! document.body.contains(document.getElementById("id_comment_div_"+item.id))){
        let comment_list = document.getElementById("post-"+item.post_id+"-comments-go-here")
        let comment = document.createElement("div")
        comment.setAttribute('id',"id_comment_div_"+item.id)
        comment.setAttribute('class',"comment_div")
        comment.innerHTML=
        '  <a class="comment_style"'+ 'href="/socialnetwork/otherProfile/'+item.user_id+'"'+
        'id="id_comment_profile_'+item.id+'">'
       + item.user +
        '</a>'+
        '<span id="id_comment_text_'+item.id+'">'+
        sanitize(item.comment_text)+
        '</span>'+
        '<span class="comment_style" id="id_comment_date_time_'+item.id+'">'+
        item.date_time+
        '</span>'

        comment_list.appendChild(comment)
        }
     }

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

function displayError(message) {
    let errorElement = document.getElementById("errorlist")
    errorElement.innerHTML = message
}

//back to top function
topButton = document.getElementById("id_backtotop_button");
window.onscroll = function() {
    scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        topButton.style.display = "block";
    } else {
        topButton.style.display = "none";
    }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}