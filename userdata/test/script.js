// Establish Connection with Python

let backend;

new QWebChannel(qt.webChannelTransport, function (channel) {
    backend = channel.objects.backend;
});

function callPython() {
    backend.send(label);
}


// trial






// trail ends



//declaring variables

let current_element;
let current_class_name;
let adding_element = false;
let prev_element;


const hover_box = document.createElement("div");
hover_box.setAttribute("id", "dev-hoverbox");
document.body.appendChild(hover_box);



// Helper Functions


function getRule(selector) {
    const rules = style.sheet.cssRules;

    for (const rule of rules) {
        if (rule.selectorText === selector) {
            return rule;
        }
    }

    return null;
}

function getStyle(selector) {

    let rule = getRule(selector);
    //console.log(rule.style);

    let properties = [
        "display",
        "flexDirection",
        "flexWrap",
        "alignContent",
        "justifyContent",
        "alignItems",
        "width",
        "height",
        "maxWidth",
        "minWidth",
        "maxHeight",
        "minHeight",
        "margin",
        "padding",
        "fontSize",
        "fontWeight",
        "textAlign",
        "color",
        "borderColor",
        "borderWidth",
        "borderStyle",
        "borderRadius",
        "backgroundColor",
        "backgroundImage",
    ];

    let css_mapped = {};

    if (rule != null) {

        properties.forEach(property => {
            if (rule.style[property] != "") {
                css_mapped[property] = rule.style[property];
            }
        });

    }

    console.log(css_mapped);

    return css_mapped;
}

function removeCssRule(selector) {
    for (let sheet of document.styleSheets) {
        try {
            const rules = sheet.cssRules || sheet.rules;
            if (!rules) continue;

            for (let i = rules.length - 1; i >= 0; i--) {
                if (rules[i].selectorText === selector) {
                    sheet.deleteRule(i);
                }
            }
        } catch (e) {
            // Ignore cross-origin stylesheets (security restriction)
            continue;
        }
    }
}


function render_selector_box(element_name = current_element) {
    let coords = element_name.getBoundingClientRect();

    select_box.style.top = String(coords.top + window.scrollY) + "px";
    select_box.style.right = String(coords.right) + "px";
    select_box.style.bottom = String(coords.bottom) + "px";
    select_box.style.left = String(coords.left) + "px";

    select_box.style.width = String(coords.width) + "px";
    select_box.style.height = String(coords.height) + "px";
}

function return_orientation(element_name) {
    const children = [...element_name.children];

    if (children.length >= 2) {
        const r1 = children[0].getBoundingClientRect();
        const r2 = children[1].getBoundingClientRect();

        const orientation =
            Math.abs(r1.top - r2.top) < Math.abs(r1.left - r2.left)
                ? 'horizontal'
                : 'vertical';

        return orientation;
    }
}


// Adding Components

let new_element;

const insert_box = document.createElement("span");
insert_box.setAttribute("id", "dev-insertbox");



function create_new_element(tag_name) {
    let a = document.createElement(tag_name);
    if (tag_name == "img") {
        a.src = "assets/img.png";
        return a;
    }
    if (tag_name == "a") {
        a.innerText = "Enter Text";
        return a;
    }

    //a.style.width = "100%";
    //a.style.height = "100%";
    a.style.minWidth = "50px";
    a.style.minHeight = "20px";
    console.log(a);
    return a;

}

function inserting_element(element_name = "p") {
    new_element = create_new_element(element_name);
    select_box.style.display = "none";
    adding_element = true;
    current_element = null;
    document.addEventListener("click", insert_element);
}

function abort_inserting() {
    adding_element = false;
    insert_box.style.display = "none";
    document.removeEventListener("click", insert_element);
}

function new_element_location(event) {
    if (!adding_element) return;
    el = event.target;

    if (el.tagName == "HTML") return;

    if (el.tagName == "DIV" || el.tagName == "BODY") {
        el.appendChild(insert_box);
        insert_box.style.display = "inline-block";
        return;
    }
    console.log(el);
    el.after(insert_box);
    insert_box.style.display = "inline-block";
}

function insert_element(event, element_name, location) {
    /* if (!adding_element) return;
    el = event.target;
    const element = document.createElement(element_name);
    if (location == "in") {

    }
    else if (location == "after") {
        el.after(element);
    }
    else if (location == "before") {
        el.before(element);
    } */

    insert_box.after(new_element);

    insert_box.style.display = "none";

    adding_element = false;
    document.removeEventListener("click", insert_element);
    backend.element_inserted();
}

function hide_insertbox(event) {
    if (!adding_element) return;
    const box = document.getElementById("dev-insertbox");
    box.style.display(none);
}





// Selecting Element


const select_box = document.createElement("div");
select_box.setAttribute("id", "dev-selectbox");
document.body.appendChild(select_box);

const label = document.createElement("span");
label.setAttribute("id", "dev-label")

select_box.appendChild(label);

document.addEventListener("click", function (event) {
    if (adding_element) return;

    const selected_element = event.target;

    if (selected_element === current_element) return;

    if (selected_element.tagName == "HTML" || selected_element.tagName == "BODY") return;


    current_element = selected_element;
    current_class_name = selected_element.className;
    let class_style = null;
    let text_content;


    label.innerText = (selected_element.tagName).toLowerCase();


    render_selector_box(selected_element);

    if (selected_element.getBoundingClientRect().top <= 0 || label.getBoundingClientRect().bottom > window.innerHeight) {
        label.style.top = "0px";
    }
    else if (selected_element.getBoundingClientRect().top >= 15) {
        label.style.top = "-15px"
    }

    if (current_class_name != null && current_class_name != "") {
        class_style = getStyle(`.${current_class_name}`);
    }


    /* const class_list = Array.from(selected_element.style).map(prop => [
        prop,
        selected_element.style.getPropertyValue(prop)
    ]); */

    //console.log(class_list);
    if (selected_element.tagName != "DIV") {
        text_content = selected_element.innerText;
    }
    else {
        text_content = "";
    }


    select_box.style.display = "block";
    console.log(label.innerText);
    backend.element_selected(label.innerText, selected_element.className, text_content, class_style);

});




// Styling Selected Element

//const style = document.createElement("style");
//document.head.appendChild(style);

const styles = document.getElementsByTagName("style");

const style = styles[0];

const sheet = style.sheet;

function update_class_name(value) {
    current_element.className = value;
    render_selector_box();
}

function apply_css(css_rule) {
    if (current_element.className == "") {
        console.log("empty class name");
        return;
    }
    removeCssRule(`.${current_element.className}`);
    style.sheet.insertRule(css_rule, style.sheet.cssRules.length);
    //console.log(style.sheet.cssRules);
    render_selector_box();
}

function print_css_text() {
    let rules = style.sheet.cssRules;
    let css_text = "";

    for (let i = 0; i < rules.length; i++) {
        css_text = css_text + "\n" + rules[i].cssText;
        console.log(rules[i].cssText);
    }

    return css_text
}


// Dump


function set_text(value) {
    console.log(value);
    console.log(current_element);
    if (current_element.tagName != "BODY" && current_element.tagName != "DIV") {
        current_element.innerText = value;
    }
}

function set_img_src(value) {
    if (current_element.tagName == "IMG") {
        if (value != "" && value != null) {
            current_element.src = "assets/" + value;
        }
        else {
            current_element.src = "assets/img.png";
        }
        render_selector_box(current_element);
    }
}


/*
function determine_position(event, x, y) {
    element = event.target;
    rect = element.getBoundingClientRect();
    middle_x = rect.top - rect.height / 2;

} */


//Hovering Element


function on_hover(event) {
    if (adding_element) return;
    hovered_element = event.target;
    hovered_tag_name = hovered_element.tagName;

    let coords = hovered_element.getBoundingClientRect();

    hover_box.style.top = String(coords.top + window.scrollY) + "px";
    hover_box.style.right = String(coords.right) + "px";
    hover_box.style.bottom = String(coords.bottom) + "px";
    hover_box.style.left = String(coords.left) + "px";

    hover_box.style.width = String(coords.width) + "px";
    hover_box.style.height = String(coords.height) + "px";

    hover_box.style.display = "block";
}

function off_hover(event) {
    if (adding_element) return;
    hovered_element = event.target;
    hover_box.style.display = "none";
}




document.addEventListener("mouseover", on_hover);

document.addEventListener("mouseout", off_hover);

document.addEventListener("mouseover", new_element_location);

//document.addEventListener("mouseout",hide_insertbox);

document.addEventListener("click", insert_element);

function moveBeforePrevious(el) {
    const prev = el.previousElementSibling;
    if (!prev) return;

    el.parentNode.insertBefore(el, prev);

}

function moveAfterNext(el) {
    /* const next = el.nextElementSibling;
    if (!next) return; // no next element

    const nextNext = next.nextElementSibling;

    if (nextNext) {
      el.parentNode.insertBefore(el, nextNext.nextElementSibling);
    } else {
      // move to the end if there is no element after next
      el.parentNode.appendChild(el);
    } */
    el.parentNode.insertBefore(el.nextElementSibling, el);
}



document.addEventListener("keydown", function (event) {
    if (event.key === "Delete") {
        console.log("delete");
        select_box.style.display = "none";
        current_element.remove();
    }
});

document.addEventListener("keydown", function (event) {
    console.log(event.key);
    if (event.key === "ArrowUp") {
        moveBeforePrevious(current_element);
        select_box.style.display = "none";
        current_element = "none";
    }

    if (event.key === "ArrowDown") {
        moveAfterNext(current_element);
        select_box.style.display = "none";
        current_element = "none";
    }

    /* if (event.key === "Delete") {
        console.log("delete");
        select_box.style.display = "none";
        current_element.remove();
    } */
});


/*
function isTrulyEmpty(el) {
  return (
    el.children.length === 0 &&
    el.textContent.trim() === ''
  );
}

function updateElement(el) {
  // Skip elements that should never be styled
  if (
    ['SCRIPT', 'STYLE', 'META', 'LINK', 'BR'].includes(el.tagName)
  ) return;

  el.classList.toggle('__auto-empty-placeholder', isTrulyEmpty(el));
}

function scanAll() {
  document.querySelectorAll('*').forEach(updateElement);
}

// Initial scan
scanAll();

// Watch for changes anywhere in the DOM
const observer = new MutationObserver(mutations => {
  mutations.forEach(mutation => {
    if (mutation.target.nodeType === 1) {
      updateElement(mutation.target);
    }
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
  characterData: true
});

 */


function save_page() {

    console.log(style.textContent);
    style.textContent = print_css_text();
    console.log(style.textContent);

    let htmlString = document.documentElement.outerHTML;

    let parser = new DOMParser();
    let document_copy = parser.parseFromString(htmlString, "text/html");

    document_copy.getElementById("dev-selectbox").remove();
    document_copy.getElementById("dev-hoverbox").remove();

    try {
        document_copy.getElementById("dev-insertbox").remove();
    }
    catch {
        console.log("");
    }

    /*     let style_tag = document_copy.getElementsByTagName("style");

        console.log(style_tag.textContent);
        console.log(print_css_text())

        style_tag.textContent =  style_tag.textContent + print_css_text();

        console.log(style_tag.textContent); */

    html_content = document_copy.documentElement.outerHTML;
    console.log(html_content);
    backend.save_page(html_content);

}

function export_code() {

    let htmlString = document.documentElement.outerHTML;

    let parser = new DOMParser();
    let document_copy = parser.parseFromString(htmlString, "text/html");

    document_copy.getElementById("dev-selectbox").remove();
    document_copy.getElementById("dev-hoverbox").remove();
    //document_copy.getElementsByTagName("style").remove();


    try {
        document_copy.getElementById("dev-insertbox").remove();
    }
    catch {
        console.log("");
    }

    style_content = print_css_text();

    html_content = document_copy.documentElement.outerHTML;
    console.log(html_content);
    backend.export_code(html_content,style_content);

}



