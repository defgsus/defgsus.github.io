
window.addEventListener('DOMContentLoaded', function(event) {

    let selected_tags = {};

    function update_repo_visibility() {
        function update_elem_visibility(elem) {
            const tags = elem.getAttribute("data-tags").split(' ');
            let hidden = Object.keys(selected_tags).length ? true : false;

            for (const tag of tags) {
                if (selected_tags[tag]) {
                    hidden = false;
                    break;
                }
            }
            if (hidden)
                elem.classList.add("hidden");
            else
                elem.classList.remove("hidden");
        }
        for (const elem of document.querySelectorAll(".repo-list .year-block")) {
            update_elem_visibility(elem);
        }
        for (const elem of document.querySelectorAll(".repo-list .repo")) {
            update_elem_visibility(elem);
        }
        for (const elem of document.querySelectorAll(".tag-filter .tag")) {
            const tag = elem.getAttribute("data-tag");
            if (selected_tags[tag])
                elem.classList.add("selected");
            else
                elem.classList.remove("selected");
        }
    }

    function render_tag_filter(tags) {
        let markup = ``;
        for (const tag of tags) {
            markup += `<div class="tag" data-tag="${tag}">${tag}</div>`;
        }
        document.querySelector(".tag-filter").innerHTML = markup;
        for (const elem of document.querySelectorAll(".tag-filter .tag")) {
            elem.onclick = function (e) {
                const tag = e.target.getAttribute("data-tag");
                if (selected_tags[tag]) {
                    delete selected_tags[tag];
                }
                else {
                    //selected_tags[tag] = true;
                    selected_tags = {[tag]: true};
                }
                update_repo_visibility();
            };
        }
    }

    function hook_to_page() {
        const tag_set = new Set();
        for (const elem of document.querySelectorAll(".repo-list .repo")) {
            const tags = elem.getAttribute("data-tags").split(' ');
            for (const tag of tags) {
                tag_set.add(tag);
            }
        }
        const all_tags = [...tag_set].sort();
        render_tag_filter(all_tags);
    }


    hook_to_page();
});
