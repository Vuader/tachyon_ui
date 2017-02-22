/**
  * Function to load content into div and submit form
  *
  * @param string element (HTML Element to populate with result)
  * @param string url (URL to open)
  * @param string form_id Serialize Data from Form to post
  *
  */

function ajax_query(element, url, form_id) {
    //url = url.replace(/\/\/+/g, '/');
    if (typeof(form_id) !== 'undefined') {
        var form = document.getElementById(form_id);
        if (typeof(window.FormData) == 'undefined') {
            document.getElementById('loading').style.display = "block";
            $.ajax({url: url,
                type: 'POST',
                async: true,
                cache: false,
                context: document.body,
                processData: true,
                data: $(form).serialize(),
                success: function(result) {
                    $(element).html(result);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $(element).html(XMLHttpRequest.responseText);
                }
            });
            document.getElementById('loading').style.display = "none";
            return false;
        }
        else {
            document.getElementById('loading').style.display = "block";
            $.ajax({url: url,
                type: 'POST',
                async: true,
                cache: false,
                contentType: false,
                processData: false,
                data: new FormData(form),
                success: function(result) {
                    $(element).html(result);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $(element).html(XMLHttpRequest.responseText);
                }
            });
            document.getElementById('loading').style.display = "none";
            return false;
        }
    }
    else {
        document.getElementById('loading').style.display = "block";
        $.ajax({url: url,
            type: 'GET',
            async:true,
            cache: false,
            context: document.body,
            success: function(result) {
                $(element).html(result);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $(element).html(XMLHttpRequest.responseText);
            }
        });
        document.getElementById('loading').style.display = "block";
        return false;
    }
}

function toggle_window() {
    var display = document.getElementById('window').style.display;
    if (display == "none" || display == "")
    {
        document.getElementById('window').style.display = "block";
    }   
    else
    {   
        document.getElementById('window').style.display = "none";
    }   
}

function toggle_locked() {
    var display = document.getElementById('locked').style.display;
    if (display == "none" || display == "")
    {
        document.getElementById('locked').style.display = "block";
    }   
    else
    {   
        document.getElementById('locked').style.display = "none";
    }   
}

function toggle_loading() {
    var display = document.getElementById('loading').style.display;
    if (display == "none" || display == "")
    {
        document.getElementById('loading').style.display = "block";
    }   
    else
    {   
        document.getElementById('loading').style.display = "none";
    }   
}

function close_window() {
    toggle_locked();
    toggle_window();
}


function service(a) {
    document.getElementById('service').innerHTML = '';
    ajax_query("#service", a.href); 
    document.getElementById('title').innerHTML = a.innerHTML;
    document.getElementById('locked').style.display = "none";
    document.getElementById('window').style.display = "none";
    return false
}


function admin(a) {
    document.getElementById('window_content').innerHTML = '';
    ajax_query("#window_content", a.href); 
    document.getElementById('locked').style.display = "block";
    document.getElementById('window_title').innerHTML = a.innerHTML;
    document.getElementById('window').style.display = "block";
    return false
}

function admin_title(title) {
    document.getElementById('window_title').innerHTML = title;
}

function form_service(form_id) {
    var form = document.getElementById(form_id);
    ajax_query("#service", form.action, form_id); 
    return false
}

function form_admin(form_id) {
    var form = document.getElementById(form_id);
    ajax_query("#window_content", form.action, form_id); 
    return false
}

notices = 0

function notice(n, css) {
    notices++;
    divid = "popup" + notices;
    n = "<div class=\"popup " + css + "\"><div style='width: 270px; float:left;'>" + n + "</div><div style='float:left;'><button class=\"close\" type=\"button\" onclick=\"close_notice('"+divid+"');\">x</button></div></div>"
    $("#popup").prepend(n);
    $('#'+divid).hide()
    $('#'+divid).fadeIn()
    if (css != 'error') {
        setTimeout(function() { close_notice(divid); }, 10000);
    }
    return String(divid)
}

function info(n) {
    div = notice(n, 'info')
}

function success(n) {
    div = notice(n, 'success')
}

function error(n) {
    div = notice(n, 'error')
}

function warning(n) {
    div = notice(n, 'warning')
}

function close_notice(n) {
    $('#'+n).fadeOut('slow',function() { delete_notice(n) })
}

function delete_notice(n) {
    popup = document.getElementById(n);
    if(typeof popup.remove === 'function') {
        popup.remove()
    } else {
        popup.style.display = "none";
    }
}

