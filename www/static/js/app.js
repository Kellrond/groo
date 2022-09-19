/* 
## Form functions ##
These are called from html elements with onclick or onchange attributes
*/

function checkPasswordsMatch(input) {
    console.log(document.getElementById('new_password').value != input.value)
    if (document.getElementById('new_password').value != input.value) {
        input.setCustomValidity('Password must be matching.');
    } else {
        input.setCustomValidity('');
    }
}

function replaceHtml (id_to_rplc, api_url, api_value=undefined, id_for_value=false) {
    let url_args = '';
    if (typeof id_to_rplc == 'object') {
        let placed_widget = false;
        if (id_for_value != false) { 
            url_args = api_value
            api_value = document.getElementById(id_for_value).value 
        }  
        fetch(`${api_url}${api_value}${url_args}`).then((response) => {
            response.json().then((data) => {
                for (const id of id_to_rplc) {
                    if (placed_widget == false) {
                        if (document.getElementById(id)) {
                            document.getElementById(id).outerHTML = data;
                            placed_widget = true;
                        } 
                    }
                }
                if (placed_widget == false) {
                    document.getElementById('page_body').innerHTML += data;
                }
                launchToast();
            })    
        })
    } else {
        let placed_widget = false;
        if (id_for_value != false) { 
            url_args = api_value
            api_value = document.getElementById(id_for_value).value 
        }  
        fetch(`${api_url}${api_value}${url_args}`).then((response) => {
            response.json().then((data) => {
                if (document.getElementById(id_to_rplc)) {
                    document.getElementById(id_to_rplc).outerHTML = data;
                } else {
                    document.getElementById('page_body').innerHTML += data;
                }
                launchToast();
            })
        })
    }
}


function resizeMultipleSelect (elem_id) {
    let elem = document.getElementById(elem_id);
    elem.size = elem.length;
}

function toggleVisible (elem_ids, set_visible) {
    if (typeof elem_ids == 'object') {
        for (const id of elem_ids) {
            let elem = document.getElementById(id);
            if (elem.style.display === "none") {
                if (set_visible || set_visible == undefined) {
                    elem.style.display = "block";
                }
            } else {
                if (!set_visible || set_visible == undefined) {
                    elem.style.display = "none";
                }
            }
        }
    } else {
        let elem = document.getElementById(elem_ids);
        if (elem.style.display === "none") {
            if (set_visible || set_visible == undefined) {
                elem.style.display = "block";
            }
        } else {
            if (!set_visible || set_visible == undefined) {
                elem.style.display = "none";
            }
        }        
    }
}

/* This function conditionally triggers a function. Used to test against the value of another element */
function triggerWhen (cond_elem_id, cond_value, js_if_str, js_else_str) {
    let elem = document.getElementById(cond_elem_id);
    if (elem.value == cond_value) {
        eval(js_if_str)
    } else {
        eval(js_else_str)
    }
}

/* 
Misc utility functions 
*/
function expandTableRow(row_id) {
    row = document.getElementById(row_id)
    if (row.className == 'overflow-shown') {
        row.className = 'overflow-hidden'
    } else {
        row.className = 'overflow-shown'
    }
}

// Handles toasts that were generated in PageBuilder
if (document.getElementById('msg-body')) {
    window.onload = (event) => { 
        setTimeout(() => {
            var toastElList = [].slice.call(document.querySelectorAll('.toast'))
            var toastList = toastElList.map(function (toastEl) {
              return new bootstrap.Toast(toastEl, {}).show()
            })
        }, 250)
    }
}

function launchToast() {
    setTimeout(() => {
        var toastElList = [].slice.call(document.querySelectorAll('.toast'))
        var toastList = toastElList.map(function (toastEl) {
          return new bootstrap.Toast(toastEl, {}).show()
        })
    }, 250)
}

function sortTable(n, table_id) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById(table_id);
    switching = true;
    dir = "asc";
    // Make a loop that will continue until no switching has been done: 
    while (switching) {
      switching = false;
      rows = table.rows;
      for (i = 1; i < (rows.length - 1); i++) {
        // Start by saying there should be no switching:
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("TD")[n];
        y = rows[i + 1].getElementsByTagName("TD")[n];
        if (!isNaN(x.innerHTML) * !isNaN(y.innerHTML)) { // Is x and y a number
            if (dir == "asc") {
                if (Number(x.innerHTML) > Number(y.innerHTML)) {
                  shouldSwitch = true;
                  break;
                }
              } else if (dir == "desc") {
                if (Number(x.innerHTML) < Number(y.innerHTML)) {
                  shouldSwitch = true;
                  break;
                }
              }
        } else { // Not a number
            if (dir == "asc") {
              if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
              }
            } else if (dir == "desc") {
              if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
              }
            }
        }
      }
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;
      } else {
        if (switchcount == 0 && dir == "asc") {
          dir = "desc";
          switching = true;
        }
      }
    }
  }