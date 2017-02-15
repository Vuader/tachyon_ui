/**
  * Function to load content into div and submit form
  *
  * @param string element (HTML Element to populate with result)
  * @param string url (URL to open)
  * @param string form_id Serialize Data from Form to post
  *
  */
function ajax(element, url, form_id) {
    url = url.replace(/\/\/+/g, '/');
	if (typeof(form_id) !== 'undefined') {
		var form = document.getElementById(form_id);
        if (typeof(window.FormData) == 'undefined') {
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
			return false;
        }
        else {
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
            return false;
        }
	}
	else {
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
		return false;
    }
}

// Clear Modal on close
$(document).on('hidden.bs.modal', function (e) {
    var target = $(e.target);
    target.removeData('bs.modal')
    .find(".modal-body").html('');
	$('#dialog').html('<div class="modal-body">Loading...</div>');
});

