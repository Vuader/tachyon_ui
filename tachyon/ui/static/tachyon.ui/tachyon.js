
/**
  * Disable Error popup for Datatables.
  * It will throw a javascript error rather.
  */
$.fn.dataTable.ext.errMode = 'throw';

/**
  * Function to load content into div and submit form
  *
  * @param string element (HTML Element to populate with result)
  * @param string url (URL to open)
  * @param string form_id Serialize Data from Form to post
  *
  */
function ajax_query(element, url, form, form_save=false) {
    $('html, body').animate({ scrollTop: 0 }, 'fast');
    document.getElementById('confirm').style.display = 'none';
    //url = url.replace(/\/\/+/g, '/');
    if (typeof(form) !== 'undefined') {
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
                    if (form_save == false) {
                        $(element).html(result);
                        document.getElementById('loading').style.display = "none";
                        $("#window_content button").on("click", function(e) {
                            link(this);
                            e.preventDefault()
                        });
                        $("#service button").on("click", function(e) {
                            link(this);
                            e.preventDefault()
                        });
                        $("#window_content form").submit(function( e )  {
                            link(this);
                            e.preventDefault()
                        });
                        $("#service_form form").submit(function( e )  {
                            link(this);
                            e.preventDefault()
                        });
                    }
                    else
                    {
                        success("Succesfully saved")
                    }
                    document.getElementById('loading').style.display = "none";
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    error(XMLHttpRequest.responseText);
                    //$(element).html(XMLHttpRequest.responseText);
                    document.getElementById('loading').style.display = "none";
                }
            });
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
                    if (form_save == false) {
                        $(element).html(result);
                        $("#window_content button").on("click", function(e) {
                            link(this);
                            e.preventDefault()
                        });
                        $("#service button").on("click", function(e) {
                            link(this);
                            e.preventDefault()
                        });
                        $("#window_content form").submit(function( e )  {
                            link(this);
                            e.preventDefault()
                        });
                        $("#service_form form").submit(function( e )  {
                            link(this);
                            e.preventDefault()
                        });
                    }
                    else
                    {
                        success("Succesfully saved")
                    }
                    document.getElementById('loading').style.display = "none";
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    error(XMLHttpRequest.responseText);
                    //$(element).html(XMLHttpRequest.responseText);
                    document.getElementById('loading').style.display = "none";
                }
            });
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
                $("#window_content button").on("click", function(e) {
                    link(this);
                    e.preventDefault()
                });
                $("#service button").on("click", function(e) {
                    link(this);
                    e.preventDefault()
                });
                $("#window_content form").submit(function( e )  {
                    link(this);
                    e.preventDefault()
                });
                $("#service_form form").submit(function( e )  {
                    link(this);
                    e.preventDefault()
                });
                document.getElementById('loading').style.display = "none";
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                document.getElementById('locked').style.display = "none";
                document.getElementById('window').style.display = "none";
                error(XMLHttpRequest.responseText);
                document.getElementById('loading').style.display = "none";
                //$(element).html(XMLHttpRequest.responseText);
            }
        });
        return false;
    }
}

/**
  * Display or hide Admin Window
  */
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

/**
  * Lock or Unlock background
  */
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

/**
  * Display or hide Loading
  */
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

/**
  * Close window
  */
function close_window() {
    document.getElementById('locked').style.display = "none";
    document.getElementById('window').style.display = "none";
}

/**
  * Open window
  */
function open_window() {
    document.getElementById('locked').style.display = "block";
    document.getElementById('window').style.display = "block";
}


/*
  * This is function is automatically triggerd on any button / form within window or service
  *
  * Open link in admin window or service and or submit form
  * depending on which is active...
  * requires data-url for link
  * optional data-name for title
  *          if not specified gets from button text
  * optional data-save set this to any value to save form and not open link in window
  *          you should see success or errors popup
  * optional data-confirm causes a pop to appear to confirm.. 
  *          set this value to the confirmation question...
  *
  * for example button: <button data-url='/ui/users' data-name='Edit Users'>
  * for example link: <a href="#" data-url="/ui/users">
  * for example form: <form data-url="/ui/users">
  * for example form save: <form data-url="/ui/users" data-save="yes">
  */
function link(element) {
    window_display = document.getElementById('window').style.display;
    if ("url" in element.dataset) {
        url = element.dataset.url;
        name = element.dataset.name;
        tag = element.tagName.toLowerCase();
        if ("save" in element.dataset) {
            save = true;
        }
        else {
            save = false;
        }
        if ("confirm" in element.dataset) {
            document.getElementById('confirmation').innerHTML = element.dataset.confirm;
            document.getElementById('confirm').style.display = 'block';
            document.getElementById('continue').onclick = function() {
                confirm = String(element.dataset.confirm);
                document.getElementById('confirm').style.display = 'none';
                delete element.dataset.confirm;
                link(element);
                element.dataset.confirm = confirm;
            }
        }
        else
            {
            if (window_display == "none" || window_display == "")
            {
                // Inside Customer area
                if (save == false) {
                    document.getElementById('service').innerHTML = '';
                }
                if (tag != "form") {
                    document.getElementById('title').innerHTML = element.innerHTML;
                }
                if ("name" in element.dataset) {
                    document.getElementById('title').innerHTML = name;
                }
                if (tag == "form") {
                    ajax_query("#service", url, element, save); 
                }
                else {
                    ajax_query("#service", url); 
                }
            }   
            else
            {   
                // Inside Admin Window
                if (save == false) {
                    document.getElementById('window_content').innerHTML = '';
                }
                if (tag == "form") {
                    ajax_query("#window_content", url, element, save); 
                }
                else {
                    ajax_query("#window_content", url); 
                }
                document.getElementById('locked').style.display = "block";
                if (tag != "form") {
                    document.getElementById('window_title').innerHTML = element.innerHTML;
                }
                if ("name" in element.dataset) {
                    document.getElementById('window_title').innerHTML = name;
                }
                document.getElementById('window').style.display = "block";
            }   
        }
        return false
    }
}

/**
  * Open service/customer view for menu
  */
function service(a) {
    document.getElementById('service').innerHTML = '';
    ajax_query("#service", a.href); 
    document.getElementById('title').innerHTML = a.innerHTML;
    document.getElementById('locked').style.display = "none";
    document.getElementById('window').style.display = "none";
    return false
}

/**
  * Open admin view for menu
  */
function admin(a) {
    document.getElementById('window_content').innerHTML = '';
    ajax_query("#window_content", a.href); 
    document.getElementById('locked').style.display = "block";
    document.getElementById('window_title').innerHTML = a.innerHTML;
    document.getElementById('window').style.display = "block";
    return false
}

/**
  * Set title
  */
function title(title) {
    var display = document.getElementById('window').style.display;
    if (display == "none" || display == "")
    {
        document.getElementById('title').innerHTML = title;
    }
    else
    {
        document.getElementById('window_title').innerHTML = title;
    }
}

/**
  * POPUPS Below... 
  */
notices = 0

function notice(n, css) {
    notices++;
    var divid = String("popup" + notices);
    n = "<div id=\"" + divid + "\" class=\"popup " + css + "\"><div style='width: 270px; float:left;'>" + n + "</div><div style='float:left;'><button class=\"close\" type=\"button\" onclick=\"close_notice('"+divid+"');\">x</button></div></div>"
    $("#popup").prepend(n);
    $('#'+divid).hide()
    $('#'+divid).fadeIn()
    if (css == 'error') {
        setTimeout(function() { close_notice(divid); }, 30000);
    }
    else {
        setTimeout(function() { close_notice(divid); }, 10000);
    }

}

/**
  * Information popup notification... 
  */
function info(n) {
    notice(n, 'info')
}

/**
  * Success popup notification... 
  */
function success(n) {
    notice(n, 'success')
}

/**
  * Error popup notification... 
  */
function error(n) {
    notice(n, 'error')
}

/**
  * Warning popup notification... 
  */
function warning(n) {
    notice(n, 'warning')
}

/**
  * close popup notification... 
  */
function close_notice(n) {
    $('#'+n).fadeOut('slow',function() { delete_notice(n) })
}

/**
  * delete popup notification... 
  */
function delete_notice(n) {
    popup = document.getElementById(n);
    if(typeof popup.remove === 'function') {
        popup.remove()
    } else {
        popup.style.display = "none";
    }
}


/**
  * Long messaging polling...... 
  */
var login = false;

/**
  * Actions for messages received from webui /messaging view. 
  */
function action(data) {
    for (i=0; i < data.length; i++){
        // if type is 'goto' then redirect to 'link'
        if (data[i].type == 'goto') {
            window.location.replace(data[i].link);
            login = false;
        }
    }
}

/**
  * AJAX Polling function
  */
function poll() {
    if (login == true) {
        $.ajax({ url: "/ui/messaging",
        success: function(data) {
            action(data);
            poll();
        },
        dataType: "json",
        //complete: poll,
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            setTimeout(poll, 60000);
        },
        timeout: 300000 });
    }
    else {
        setTimeout(poll, 1000);
    }
}

/**
  * Run Polling function
  */
$( document ).ready(function() {
    poll()
});

/**
  * Show menu item you clicked on.
  */
$( document ).ready(function() {
    $(".nav-stacked .nav-link").on("click", function() {
        $(".nav li").removeClass("active");
        $(this).addClass("active");
    });
    $(".navbar-fixed-top .nav-link").on("click", function() {
        $(".navbar-fixed-top .nav-link").removeClass("active");
        $(this).addClass("active");
    });
});

/**
  * Inactive user auto logout
  * Work in progess!!! TODO!!!
  */

/**
var idleTime = 0;
$(document).ready(function () {
    //Increment the idle time counter every minute.
    var idleInterval = setInterval(timerIncrement, 60000); // 1 minute

    //Zero the idle timer on mouse movement.
    $(this).mousemove(function (e) {
        idleTime = 0;
    });
    $(this).keypress(function (e) {
        idleTime = 0;
    });
});

function timerIncrement() {
    idleTime = idleTime + 1;
    if (idleTime > 1) { // 20 minutes
		var url = window.location.href;    
		if (url.indexOf('?') > -1){
		   url += '&logout=1'
		}else{
		   url += '?logout=1'
		}
		window.location.href = url;
	}
}
**/
